# Frontend for Agent Lab

This directory contains the frontend application for Agent Lab, a learning platform for experimenting with LLMs, MCP (Model Context Protocol), and RAG systems.

## Technology Stack

**To be decided:**
- React or Vue.js
- Vite or Create React App
- UI library (Material-UI, Chakra UI, etc.)

## Structure

```
frontend/
├── src/
│   ├── components/       # React/Vue components
│   │   ├── Chat.jsx     # Chat interface component
│   │   ├── RAGViewer.jsx # RAG results visualization
│   │   └── MPCManager.jsx # MPC instance management UI
│   ├── services/         # API client services
│   ├── hooks/           # Custom React hooks
│   ├── utils/           # Utility functions
│   ├── App.jsx          # Main application component
│   └── main.jsx         # Entry point
├── public/              # Static assets
├── package.json         # Node.js dependencies
└── vite.config.js       # Vite configuration
```

## Planned Features

### Chat Interface
- Send messages to LLM
- View conversation history
- Toggle RAG mode
- Display sources when using RAG

### MPC Manager
- Create new MPC server instances
- View running instances
- Stop/restart instances
- Monitor instance status

### RAG Viewer
- Upload documents to knowledge base
- Query the RAG system
- Visualize retrieved sources
- View document embeddings

## Setup (To be implemented)

```bash
cd frontend
npm install
npm run dev
```

## API Integration

The frontend will communicate with the backend API at:
- Development: `http://localhost:8000`
- Production: TBD

Endpoints:
- `/api/chat/message` - Send chat messages
- `/api/chat/rag/query` - Query RAG system
- `/api/mpc/instances` - Manage MPC instances
