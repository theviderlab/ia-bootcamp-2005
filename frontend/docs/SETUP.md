# Frontend Setup Guide

## Quick Start

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create environment file
cp .env.example .env

# 4. Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Prerequisites Checklist

- [ ] Node.js >= 18.0.0 installed
- [ ] npm >= 9.0.0 installed
- [ ] Backend server running at `http://localhost:8000`
- [ ] Git installed (for version control)

### Verify Prerequisites

```bash
# Check Node.js version
node --version  # Should be >= 18.0.0

# Check npm version
npm --version   # Should be >= 9.0.0

# Check if backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

## Detailed Setup Steps

### 1. Install Dependencies

```bash
npm install
```

This will install:
- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **Zustand**: State management
- **Tailwind CSS**: Styling
- **React Router**: Navigation (if needed)

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Backend API URL (default is fine for local development)
VITE_API_URL=http://localhost:8000

# Enable MCP tools section
VITE_ENABLE_MCP=true

# Enable debug mode (shows API calls in console)
VITE_ENABLE_DEBUG_MODE=true

# Session timeout in milliseconds (1 hour)
VITE_DEFAULT_SESSION_TIMEOUT=3600000
```

### 3. Start Development Server

```bash
npm run dev
```

You should see:

```
  VITE v5.4.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 4. Verify Setup

Open [http://localhost:5173](http://localhost:5173) and you should see:
- "Agent Lab Frontend" heading
- "Implementation ready to start" message
- Test counter button

Open browser console (F12) and test backend connection:

```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
// Expected: {status: "healthy"}
```

## Development Workflow

### Start Developing

The project structure is ready with:
- ✅ Configuration files (package.json, vite.config.js, tailwind.config.js)
- ✅ Basic app skeleton (App.jsx, main.jsx, index.html)
- ✅ API constants and services (api.js, chatService.js, sessionService.js, mcpService.js)
- ✅ Path aliases configured (@components, @services, @hooks, etc.)

### Available Commands

```bash
# Development
npm run dev          # Start dev server with hot reload

# Build
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint
npm run format       # Format code with Prettier
```

### Project Structure

```
frontend/
├── src/
│   ├── components/       # React components (to be created)
│   ├── services/         # API service layer
│   │   ├── api.js               ✅ Base axios client
│   │   ├── chatService.js       ✅ Chat endpoints
│   │   ├── sessionService.js    ✅ Session management
│   │   └── mcpService.js        ✅ MCP tools
│   ├── constants/        # Constants and config
│   │   ├── api.js               ✅ API endpoints
│   │   └── memoryTypes.js       ✅ Memory type constants
│   ├── hooks/            # Custom React hooks (to be created)
│   ├── utils/            # Utility functions (to be created)
│   ├── store/            # State management (to be created)
│   ├── App.jsx           ✅ Main app component
│   ├── main.jsx          ✅ Entry point
│   └── index.css         ✅ Global styles
├── public/               # Static assets
├── .env                  ⚠️  Create from .env.example
├── .env.example          ✅ Environment template
├── package.json          ✅ Dependencies
├── vite.config.js        ✅ Vite configuration
├── tailwind.config.js    ✅ Tailwind CSS config
├── postcss.config.js     ✅ PostCSS config
└── jsconfig.json         ✅ Path aliases

✅ = Created
⚠️  = Needs action
```

## Common Issues & Solutions

### Issue: `npm install` fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: Port 5173 already in use

**Solution:**
```bash
# Use different port
npm run dev -- --port 3000

# Or kill process using port 5173 (Linux/Mac)
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Issue: Backend connection fails (CORS error)

**Symptoms:** Console shows CORS error when fetching from backend.

**Solution:**
- Ensure backend is running: `curl http://localhost:8000/health`
- Backend CORS is configured to allow `http://localhost:5173` (already set)
- Check `.env` file has correct `VITE_API_URL`

### Issue: Tailwind CSS not working

**Solution:**
```bash
# Ensure PostCSS and Tailwind are installed
npm install -D tailwindcss postcss autoprefixer

# Verify tailwind.config.js and postcss.config.js exist
ls tailwind.config.js postcss.config.js

# Check index.css has Tailwind directives
cat src/index.css | grep @tailwind
```

## Next Steps

Once setup is complete, you're ready to start implementing features:

1. **Phase 1 (Week 1-2)**: Core Chat Interface
   - Create Layout components (Header, Sidebar, Main)
   - Build Chat tab with message list and input
   - Connect to `/llm/chat` endpoint
   - Implement basic session management

2. **Phase 2 (Week 3)**: Memory Integration
   - Implement Memory sidebar section with toggles
   - Build Memory tabs (Short-term and Long-term)
   - Connect to memory endpoints

3. **Phase 3 (Week 4)**: RAG Integration
   - Build RAG sidebar with file uploader
   - Implement document management
   - Build RAG Results tab

See [README.md](README.md) for complete development roadmap.

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes to files will reflect immediately without full page reload.

### Path Aliases

Use configured aliases for cleaner imports:

```javascript
// Instead of:
import apiClient from '../../services/api';

// Use:
import apiClient from '@services/api';
```

Available aliases:
- `@/` → `src/`
- `@components/` → `src/components/`
- `@services/` → `src/services/`
- `@hooks/` → `src/hooks/`
- `@utils/` → `src/utils/`
- `@constants/` → `src/constants/`
- `@store/` → `src/store/`

### Debug Mode

Enable debug logging in `.env`:

```bash
VITE_ENABLE_DEBUG_MODE=true
```

This will log all API requests and responses to browser console.

### Backend Integration

The API client is configured with interceptors. All requests automatically:
- Add `Content-Type: application/json` header
- Log requests/responses in debug mode
- Handle errors gracefully

Example usage:

```javascript
import { chatService } from '@services/chatService';

const response = await chatService.sendMessage(
  [{ role: 'user', content: 'Hello' }],
  { sessionId: 'my-session-123' }
);

console.log(response.response); // LLM response text
```

## Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Axios](https://axios-http.com/)
- [Zustand](https://zustand-demo.pmnd.rs/)
- [Backend API Documentation](../docs/API.md)

## Support

If you encounter issues:

1. Check this SETUP.md for common solutions
2. Review [README.md](README.md) for specifications
3. Check backend is running and accessible
4. Enable debug mode and check browser console
5. Verify Node.js and npm versions

---

**Setup complete!** 🚀 You're ready to start developing the Agent Lab frontend.
