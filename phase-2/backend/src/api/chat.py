"""
Chat API Endpoints for AI Agent

Provides endpoints for user-agent interactions with conversation persistence.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from src.auth.dependencies import get_current_user
from src.db.session import get_session
from src.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationResponse,
    Message,
    MessageCreate,
    MessageResponse,
)
from src.models.user import User
from src.services.agent_service import AgentService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    req: ConversationCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new conversation.

    Args:
        req: ConversationCreate request with optional title
        current_user: Authenticated user
        session: Database session

    Returns:
        ConversationResponse with created conversation details
    """
    try:
        conversation = Conversation(
            user_id=current_user.id,
            title=req.title,
        )

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            message_count=0,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}",
        )


@router.get("/conversations", response_model=list[ConversationResponse], status_code=200)
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List conversations for the authenticated user.

    Args:
        limit: Maximum number of conversations (1-100, default 50)
        offset: Number of conversations to skip (default 0)
        current_user: Authenticated user
        session: Database session

    Returns:
        List of ConversationResponse objects
    """
    try:
        # Build query
        query = (
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        conversations = session.exec(query).all()

        # Get message counts for each conversation
        responses = []
        for conv in conversations:
            count_query = select(func.count(Message.id)).where(
                Message.conversation_id == conv.id
            )
            message_count = session.exec(count_query).one()

            responses.append(
                ConversationResponse(
                    id=conv.id,
                    user_id=conv.user_id,
                    title=conv.title,
                    message_count=message_count,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                )
            )

        return responses

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}",
        )


@router.get(
    "/conversations/{conversation_id}", response_model=ConversationResponse, status_code=200
)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get a specific conversation with message count.

    Args:
        conversation_id: UUID of the conversation
        current_user: Authenticated user
        session: Database session

    Returns:
        ConversationResponse with message count

    Raises:
        404: Conversation not found
        403: Not authorized to access conversation
    """
    conversation = session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    # Get message count
    count_query = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    message_count = session.exec(count_query).one()

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        message_count=message_count,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=dict,
    status_code=201,
)
async def send_chat_message(
    conversation_id: UUID,
    req: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Send a message to the chat agent and get a response.

    Stores both user message and assistant response in conversation.

    Args:
        conversation_id: UUID of the conversation
        req: MessageCreate with user message content
        current_user: Authenticated user
        session: Database session

    Returns:
        Dictionary with user message, assistant message, and tool calls

    Raises:
        404: Conversation not found
        403: Not authorized to access conversation
    """
    try:
        # Verify conversation exists and belongs to user
        conversation = session.get(Conversation, conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation",
            )

        # Store user message
        user_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="user",
            content=req.content,
        )

        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        # Retrieve conversation history (last 20 messages for context)
        history_query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(20)
        )
        history_messages = session.exec(history_query).all()

        # Format history for API - include tool_calls for context resolution
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": msg.tool_calls.get("tool_calls", []) if msg.tool_calls else [],
            }
            for msg in history_messages
        ]

        # Process message through agent
        agent_service = AgentService(session)
        agent_result = await agent_service.process_user_message(
            user_id=current_user.id,
            user_message=req.content,
            conversation_history=conversation_history,
        )

        if not agent_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=agent_result.get("error", "Agent processing failed"),
            )

        # Store assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="assistant",
            content=agent_result["assistant_message"],
            tool_calls=agent_service.format_tool_calls_for_storage(
                agent_result.get("tool_calls", [])
            ),
        )

        session.add(assistant_message)
        conversation.updated_at = conversation.updated_at  # Trigger update
        session.add(conversation)
        session.commit()

        return {
            "success": True,
            "conversation_id": str(conversation.id),
            "user_message": {
                "id": str(user_message.id),
                "role": "user",
                "content": req.content,
                "created_at": user_message.created_at.isoformat(),
            },
            "assistant_message": {
                "id": str(assistant_message.id),
                "role": "assistant",
                "content": agent_result["assistant_message"],
                "tool_calls": agent_result.get("tool_calls", []),
                "created_at": assistant_message.created_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}",
        )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
    status_code=200,
)
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get messages from a conversation.

    Args:
        conversation_id: UUID of the conversation
        limit: Maximum number of messages (1-100, default 50)
        offset: Number of messages to skip (default 0)
        current_user: Authenticated user
        session: Database session

    Returns:
        List of MessageResponse objects ordered by creation time

    Raises:
        404: Conversation not found
        403: Not authorized to access conversation
    """
    # Verify conversation exists and belongs to user
    conversation = session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    # Get messages
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )

    messages = session.exec(query).all()

    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            user_id=msg.user_id,
            role=msg.role,
            content=msg.content,
            tool_calls=msg.tool_calls,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.delete(
    "/conversations/{conversation_id}",
    status_code=204,
)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: UUID of the conversation
        current_user: Authenticated user
        session: Database session

    Raises:
        404: Conversation not found
        403: Not authorized to delete conversation
    """
    conversation = session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this conversation",
        )

    try:
        session.delete(conversation)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}",
        )
