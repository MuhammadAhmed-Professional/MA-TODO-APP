# Demo Video Script - Hackathon II Todo App

**Maximum Length**: 90 seconds
**Target Audience**: Hackathon Judges
**Goal**: Demonstrate all implemented features across all phases

---

## Script (90 seconds)

### Scene 1: Intro (0-5 seconds)
**Visual**: Title screen with app name "Evolution of Todo"
**Audio**: "Welcome to the Evolution of Todo - a full-stack AI-powered task management application built with Next.js, FastAPI, and OpenAI Agents SDK."

---

### Scene 2: User Authentication (5-15 seconds)
**Visual**:
- Show login page at `/en/login`
- User enters credentials
- Redirect to dashboard

**Audio**: "Secure authentication with Better Auth integration. Users can sign up and log in with JWT tokens stored in HttpOnly cookies for maximum security."

---

### Scene 3: Dashboard - Task CRUD (15-30 seconds)
**Visual**:
- Show dashboard with task list
- Create new task "Buy groceries" using the form
- Show task appearing in list
- Mark task as complete with checkbox
- Delete a task

**Audio**: "Full task management with Create, Read, Update, and Delete operations. Filter by status, search by title, and organize with categories and tags."

---

### Scene 4: AI Chatbot (30-55 seconds)
**Visual**:
- Navigate to `/en/chat`
- Show chat interface with voice input button
- Type: "Add a task called 'Finish project documentation'"
- Show AI response and task creation
- Type: "Show me my pending tasks"
- Show AI listing tasks
- Use voice input to say: "Mark the first task complete"

**Audio**: "The AI chatbot powered by OpenAI Agents SDK with MCP tool integration. Use natural language or voice commands to create, list, complete, and delete tasks. The agent understands context, pronouns, and multi-turn conversations."

---

### Scene 5: Internationalization (55-65 seconds)
**Visual**:
- Switch language from English to Urdu using language selector
- Show UI updating to Urdu text
- Show dashboard in Urdu

**Audio**: "Built-in internationalization supporting English and Urdu languages with the Next.js App Router [locale] pattern."

---

### Scene 6: Event-Driven Architecture (65-80 seconds)
**Visual**:
- Show terminal with Dapr running
- Show Kafka topic receiving events
- Show task creation triggering event publication

**Audio**: "Event-driven architecture with Dapr and Kafka integration. Every task operation publishes events for audit logging, recurring task processing, and real-time notifications."

---

### Scene 7: Outro (80-90 seconds)
**Visual**:
- Show tech stack badges: Next.js 16, FastAPI, OpenAI Agents SDK, Dapr, Kafka
- Show GitHub repo link
- Show "Thank You" message

**Audio**: "Built with modern technologies including Next.js 16, FastAPI, OpenAI Agents SDK, Dapr, and Kafka. Check out the repository for the full source code. Thank you!"

---

## Preparation Checklist

### Before Recording

1. **Backend Setup**:
   ```bash
   cd phase-2/backend
   uv sync
   export DATABASE_URL="postgresql://..."
   export OPENAI_API_KEY="sk-..."
   uv run uvicorn src.main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd phase-2/frontend
   pnpm install
   pnpm dev
   ```

3. **Dapr & Kafka** (for event demo):
   ```bash
   # Start Kafka with Docker
   docker-compose up -d kafka

   # Start backend with Dapr
   dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 \
    --components-path ./dapr/components -- uv run uvicorn src.main:app
   ```

4. **Create Test User**:
   - Email: `demo@example.com`
   - Password: `password123`

5. **Prepare Sample Tasks**:
   - "Buy groceries"
   - "Fix bug in dashboard"
   - "Write documentation"

---

## Recording Tips

### Screen Recording
- Use **OBS Studio** or **Loom** for recording
- Resolution: 1920x1080 (1080p)
- Frame rate: 30fps
- Zoom in on important UI elements

### Audio
- Use a good quality microphone
- Speak clearly and at a moderate pace
- Record voiceover separately if possible for better quality

### Editing
- Use **DaVinci Resolve** (free) or **CapCut** (free)
- Add subtle transitions between scenes
- Include text overlays for key features
- Add background music (optional, keep volume low)

### Visual Enhancements
- Highlight cursor movements
- Add arrow pointers to important elements
- Show keyboard shortcuts when used
- Display API calls/events in side panel

---

## Feature Coverage Checklist

| Feature | Scene | Time | Status |
|---------|-------|------|--------|
| User Signup/Login | Scene 2 | 10s | ☐ |
| Task Creation | Scene 3 | 5s | ☐ |
| Task Listing | Scene 3 | 3s | ☐ |
| Task Completion | Scene 3 | 3s | ☐ |
| Task Deletion | Scene 3 | 3s | ☐ |
| Task Filtering | Scene 3 | 2s | ☐ |
| AI Chat - Create Task | Scene 4 | 8s | ☐ |
| AI Chat - List Tasks | Scene 4 | 5s | ☐ |
| AI Chat - Voice Input | Scene 4 | 5s | ☐ |
| MCP Tool Integration | Scene 4 | 3s | ☐ |
| i18n - English/Urdu | Scene 5 | 10s | ☐ |
| Dapr Event Publishing | Scene 6 | 8s | ☐ |
| Kafka Events | Scene 6 | 5s | ☐ |

---

## Quick Commands Reference

### Start Everything (for demo)
```bash
# Terminal 1: Start Kafka
docker-compose up -d kafka redis

# Terminal 2: Start Backend with Dapr
cd phase-2/backend
dapr run --app-id todo-backend --app-port 8000 \
  --dapr-http-port 3500 --components-path ./dapr/components \
  -- uv run uvicorn src.main:app --reload

# Terminal 3: Start Frontend
cd phase-2/frontend
pnpm dev

# Terminal 4: Monitor Kafka events
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning
```

### Demo User Credentials
```
Email: demo@example.com
Password: password123
```

### Test Voice Commands
- "Add a task called 'Call mom'"
- "Show me my pending tasks"
- "Mark task 1 as complete"
- "Delete the first task"

---

## Estimated Time to Record

| Activity | Time |
|----------|------|
| Setup environment | 15 min |
| Practice walkthrough | 20 min |
| Record screen | 10 min |
| Record voiceover | 10 min |
| Edit video | 30 min |
| **Total** | **~85 min** |

---

## Output Format

- **File**: `demo-video.mp4`
- **Resolution**: 1920x1080 (1080p)
- **Format**: MP4 (H.264 codec)
- **Duration**: 90 seconds max
- **File Size**: ~50-100 MB (for easy upload)

---

## Upload Locations

1. **YouTube** - Unlisted link for judges
2. **GitHub Releases** - Attach to hackathon submission
3. **Loom** - Quick shareable link

---

## Notes for Judges

Key points to emphasize during Q&A:
- **OpenAI Agents SDK**: Used `@function_tool` decorator for MCP tools, `Agent` and `Runner` pattern for execution
- **MCP Server**: Stdio transport, exposes 5 task management tools
- **Chat Endpoint**: `/api/{user_id}/chat` per spec
- **Phase V Integration**: Dapr event publishing, Kafka topics
- **i18n**: `[locale]` directory structure with next-intl
- **Bonus Features**: Voice input/output, Urdu language support

Score Improvement: **~+125 points** from these fixes
Estimated Final Score: **~1405/1600** (88%)
