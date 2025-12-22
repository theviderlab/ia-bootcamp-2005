# Phase 1 Testing Checklist

## Manual Testing Steps

### 1. Backend Health Check
- [ ] Backend is running on http://localhost:8000
- [ ] Test: `curl http://localhost:8000/health`
- [ ] Expected: `{"status":"healthy"}`

### 2. Frontend Startup
- [ ] Run `npm run dev` in frontend directory
- [ ] Browser opens to http://localhost:5173
- [ ] No console errors on load
- [ ] Chat tab is active by default

### 3. UI Rendering
- [ ] Header displays "Chat" and "Context Window" tabs
- [ ] Chat tab is highlighted (blue background)
- [ ] Empty state message: "Start a conversation"
- [ ] Input box at bottom with placeholder text
- [ ] Send button is visible
- [ ] Sidebar placeholder visible on right (desktop)

### 4. Send First Message
- [ ] Type: "Hello, who are you?"
- [ ] Press Enter or click Send button
- [ ] User message appears immediately (right side, blue bubble)
- [ ] Loading indicator appears (animated dots + "Thinking...")
- [ ] Assistant response appears after ~2-5 seconds
- [ ] Response is on left side (gray bubble)
- [ ] Both messages have timestamps

### 5. Message Features
- [ ] Click "📋 Copy" on user message
- [ ] Confirmation shows: "✓ Copied"
- [ ] Paste in notepad - matches original message
- [ ] Hover over message shows relative time
- [ ] Long messages wrap properly
- [ ] Multiple messages stack vertically

### 6. Conversation Flow
- [ ] Send 3-4 messages in sequence
- [ ] Each message waits for previous response
- [ ] Auto-scroll keeps latest message visible
- [ ] Session ID persists (same conversation)
- [ ] Input box clears after each send

### 7. Input Box Features
- [ ] Type multiple lines with Shift+Enter
- [ ] Textarea auto-expands with content
- [ ] Enter without Shift sends message
- [ ] Send button disabled when input is empty
- [ ] Helper text shows: "Press Enter to send, Shift+Enter for a new line"
- [ ] Input disabled during loading

### 8. Context Window Tab
- [ ] Click "Context Window" tab
- [ ] Tab switches (Context Window highlighted)
- [ ] Before first message: Shows "No context data yet"
- [ ] After sending message: Shows context data
- [ ] Token count displayed
- [ ] Full context text visible in scrollable area
- [ ] RAG sources section (empty for now)

### 9. Error Handling
- [ ] Stop backend server
- [ ] Try sending a message
- [ ] Error banner appears at top: "Failed to send message..."
- [ ] Error is dismissable (click "Dismiss")
- [ ] User message still visible in history
- [ ] Restart backend and retry - works again

### 10. Responsive Design (Desktop)
- [ ] Resize browser window to ~1200px width
- [ ] Layout maintains 60/40 split (chat/sidebar)
- [ ] Messages readable at all sizes
- [ ] Input box remains at bottom

### 11. Tab Navigation
- [ ] Click between "Chat" and "Context Window" multiple times
- [ ] Tabs switch smoothly
- [ ] Chat history persists when switching back
- [ ] Context data persists when switching back

### 12. Multi-line Messages
- [ ] Type: "Line 1" + Shift+Enter + "Line 2" + Shift+Enter + "Line 3"
- [ ] Press Enter to send
- [ ] Message displays all 3 lines
- [ ] Formatting preserved in response

---

## Expected API Behavior

### First Message Request
```json
{
  "messages": [{"role": "user", "content": "Hello"}],
  "use_memory": true,
  "use_rag": false,
  "memory_types": ["semantic", "episodic", "profile", "procedural"]
}
```

### First Message Response
```json
{
  "response": "Hello! I'm...",
  "session_id": "uuid-generated-by-backend",
  "context_text": "## System Prompt\n...",
  "context_tokens": 1250
}
```

### Subsequent Messages Request
```json
{
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hello! I'm..."},
    {"role": "user", "content": "What's the weather?"}
  ],
  "session_id": "uuid-from-first-response",
  "use_memory": true,
  ...
}
```

---

## Common Issues & Solutions

### Issue: "Module not found"
**Solution:** Check imports use path aliases (@components, @services, etc.)

### Issue: Tailwind styles not applying
**Solution:** Ensure `index.css` imports Tailwind directives and is imported in `main.jsx`

### Issue: Backend connection refused
**Solution:** Verify backend is running: `uv run python -m agentlab.api.main`

### Issue: CORS errors
**Solution:** Vite proxy is configured in `vite.config.js` - should work automatically

### Issue: Session ID not persisting
**Solution:** Check browser console - Zustand store should log session ID on first response

---

## Browser Console Checks

### Expected Logs (Debug Mode)
```
[API] Request: POST http://localhost:8000/api/llm/chat
[API] Response: { response: "...", session_id: "..." }
```

### No Errors Should Appear
- No 404 errors
- No CORS errors
- No React rendering errors
- No Zustand state errors

---

## Performance Expectations

- **Message send latency:** < 5 seconds (depends on LLM)
- **UI responsiveness:** Instant (optimistic UI updates)
- **Scroll performance:** Smooth 60fps
- **Memory usage:** < 100MB (browser)

---

## Test Status

- [ ] All UI rendering tests passed
- [ ] All message features work
- [ ] Conversation flow works
- [ ] Context window displays correctly
- [ ] Error handling works
- [ ] Tab navigation works
- [ ] No console errors

**Tested by:** _____________  
**Date:** _____________  
**Result:** ☐ Pass ☐ Fail  
**Notes:** _____________

---

Last Updated: December 21, 2025
