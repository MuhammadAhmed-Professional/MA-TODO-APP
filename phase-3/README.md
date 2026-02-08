# Phase III: AI Chatbot with MCP Tools

**Status**: ✅ Complete (integrated into Phase II backend)
**Live**: [https://talal-s-tda.vercel.app](https://talal-s-tda.vercel.app) (Chat page)

---

## Overview

Phase III adds an AI-powered chatbot to the Todo application using the OpenAI Agents SDK and the official Model Context Protocol (MCP) SDK. The chatbot understands natural language and manages tasks through 5 MCP tools.

## Implementation Location

The chatbot is integrated into the Phase II backend at `/phase-2/backend/`:

| Component | Location |
|-----------|----------|
| MCP Server | `src/mcp_server.py` |
| MCP Tools (5) | `src/mcp_tools/` |
| Chat API (6 endpoints) | `src/api/chat.py` |
| Agent Service | `src/services/agent_service.py` |
| Conversation Models | `src/models/conversation.py` |
| Chat UI | `../frontend/src/components/chat/ChatBot.tsx` |
| Voice Input | `../frontend/src/hooks/useSpeechRecognition.ts` |
| Voice Output | `../frontend/src/hooks/useSpeechSynthesis.ts` |

## Key Technologies

- **OpenAI Agents SDK** (`openai-agents>=0.0.2`) - Agent framework with function tools
- **Official MCP SDK** (`mcp>=1.24.0`) - Model Context Protocol with stdio transport
- **Gemini Model Rotation** - 4 Gemini models for reliability
- **Vercel AI SDK** - Frontend chat UI integration
- **Web Speech API** - Voice input (recognition) + voice output (synthesis)

## MCP Tools

| Tool | Description |
|------|-------------|
| `add_task` | Create new tasks via natural language |
| `list_tasks` | List and filter tasks |
| `complete_task` | Mark tasks as complete |
| `delete_task` | Delete tasks with confirmation |
| `update_task` | Update task title/description |

## Chat Endpoints

- `POST /api/chat/conversations` - Create conversation
- `GET /api/chat/conversations` - List conversations
- `GET /api/chat/conversations/{id}` - Get conversation
- `POST /api/chat/conversations/{id}/messages` - Send message & get AI response
- `GET /api/chat/conversations/{id}/messages` - Get message history
- `DELETE /api/chat/conversations/{id}` - Delete conversation

## Architecture

- Conversation state persisted in PostgreSQL (not in-memory)
- Stateless server design (context rebuilt from DB on each request)
- Intent detection, pronoun resolution, confirmation flows
- Fallback execution when agent API fails

See Phase II README for running instructions.
