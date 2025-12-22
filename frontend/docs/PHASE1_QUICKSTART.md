# Phase 1 - Quick Start Guide

## ✅ Implementation Complete

Phase 1 of the Agent Lab frontend has been successfully implemented with the following features:

### What's Included

**🎨 UI Components:**
- Split-screen layout (60% chat, 40% sidebar placeholder)
- Tab navigation (Chat & Context Window)
- Message list with auto-scroll
- Message bubbles (user/assistant styling)
- Multi-line input with auto-expand
- Loading indicators (animated dots)

**⚡ State Management:**
- Zustand store for global chat state
- Custom `useChat` hook for chat operations
- Session ID auto-generation on first message
- In-memory message history

**🔌 API Integration:**
- Complete connection to POST /llm/chat endpoint
- Error handling with dismissable error banner
- Context data capture for Context Window tab

**✨ Features:**
- Send/receive messages
- Copy messages to clipboard
- Relative timestamps ("2 minutes ago")
- Empty state for first load
- Smooth animations

---

## 🚀 How to Run

### Prerequisites

Ensure the backend is running:
```bash
# In the project root
cd c:\Users\rdiaz\Documents\GitHub\ia-bootcamp-2005
uv run python -m agentlab.api.main
```

The backend should be available at `http://localhost:8000`

### Start the Frontend

```powershell
# Navigate to frontend directory
cd c:\Users\rdiaz\Documents\GitHub\ia-bootcamp-2005\frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

---

## 🧪 Testing the Chat

1. **Open browser:** Navigate to http://localhost:5173
2. **Send a message:** Type "Hello, who are you?" and press Enter
3. **Observe:**
   - Your message appears on the right (blue bubble)
   - Loading indicator appears (animated dots)
   - Assistant response appears on the left (gray bubble)
   - Session ID is generated automatically
4. **Test features:**
   - Copy message: Click the "📋 Copy" button on any message
   - View context: Click "Context Window" tab to see LLM context
   - Send multiple messages: Test conversation flow
   - Check timestamps: Hover to see relative time

---

## 📁 Files Created

### State Management
- `src/store/chatStore.js` - Zustand store for chat state
- `src/hooks/useChat.js` - Custom hook wrapping chatService

### Layout Components
- `src/components/Layout/Layout.jsx` - Main layout wrapper
- `src/components/Layout/Header.jsx` - Top bar with tabs
- `src/components/Layout/Sidebar.jsx` - Right panel placeholder

### Chat Components
- `src/components/Tabs/ChatTab.jsx` - Main chat interface
- `src/components/Tabs/ContextWindowTab.jsx` - Context display
- `src/components/Chat/MessageList.jsx` - Scrollable message area
- `src/components/Chat/Message.jsx` - Single message component
- `src/components/Chat/InputBox.jsx` - Message input field

### Utilities
- `src/utils/formatters.js` - Time formatting utilities

### Configuration
- `.env` - Environment variables

---

## 🎯 Key Implementation Decisions

**Session Management:**
- Session ID is generated lazily on first message (API auto-generates if not provided)
- Stored in Zustand store for subsequent messages
- No localStorage persistence (in-memory only for Phase 1)

**Message Persistence:**
- Messages stored in-memory via Zustand
- Lost on browser refresh (intentional for Phase 1)
- Will add localStorage in Phase 2 with memory integration

**Action Buttons:**
- Reset Session and Delete All buttons skipped for Phase 1
- Will be implemented in Phase 6 with proper confirmations

**Responsive Design:**
- Desktop: 60/40 split (chat/sidebar)
- Sidebar hidden on mobile (will be drawer in Phase 4)
- Optimized for desktop development workflow

---

## 🐛 Troubleshooting

### Backend Connection Issues

**Error:** "Failed to send message"

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `.env` file has correct `VITE_API_URL=http://localhost:8000`
3. Check browser console for CORS errors
4. Restart dev server: `npm run dev`

### Import Errors

**Error:** Module not found

**Solution:** Vite aliases are configured. Ensure imports use:
- `@components/...` for components
- `@services/...` for services
- `@hooks/...` for hooks
- `@store/...` for store
- `@utils/...` for utilities

### Styling Issues

**Error:** Styles not loading

**Solution:**
1. Check `index.css` is imported in `main.jsx`
2. Verify Tailwind is working: `npx tailwindcss --help`
3. Clear browser cache and reload

---

## 📝 Next Steps

### Ready for Phase 2: Memory Integration

Phase 2 will add:
- Memory sidebar section with toggles
- Short-term Memory tab
- Long-term Memory tab (semantic, episodic, profile, procedural views)
- Connection to memory API endpoints

### What's Working

✅ Full chat functionality  
✅ Session management  
✅ Context window display  
✅ Error handling  
✅ Message copying  
✅ Smooth animations  

### What's Pending

⏳ Memory integration (Phase 2)  
⏳ RAG file upload (Phase 3)  
⏳ Token usage visualization (Phase 4)  
⏳ MCP tools management (Phase 6)  
⏳ Session reset/delete all (Phase 6)  

---

## 🎓 Code Structure

```
frontend/src/
├── App.jsx                    # Main app with tab management
├── main.jsx                   # React entry point
├── index.css                  # Global styles + Tailwind
├── components/
│   ├── Layout/
│   │   ├── Layout.jsx         # Split-screen layout
│   │   ├── Header.jsx         # Tab navigation
│   │   └── Sidebar.jsx        # Config panel (placeholder)
│   ├── Tabs/
│   │   ├── ChatTab.jsx        # Main chat interface
│   │   └── ContextWindowTab.jsx  # Context display
│   └── Chat/
│       ├── MessageList.jsx    # Message area
│       ├── Message.jsx        # Single message
│       └── InputBox.jsx       # Input field
├── hooks/
│   └── useChat.js             # Chat logic hook
├── store/
│   └── chatStore.js           # Zustand store
├── services/
│   ├── api.js                 # Axios client
│   └── chatService.js         # Chat API calls
├── utils/
│   └── formatters.js          # Time formatting
└── constants/
    └── api.js                 # API endpoints
```

---

## 📞 Support

If you encounter issues:
1. Check browser console for errors
2. Verify backend is running and healthy
3. Check `.env` configuration
4. Review [CHECKLIST.md](./CHECKLIST.md) for implementation status
5. Consult [README.md](./README.md) for API specifications

---

**Last Updated:** December 21, 2025  
**Phase Status:** ✅ Phase 1 Complete (100%)  
**Next Phase:** Phase 2 - Memory Integration
