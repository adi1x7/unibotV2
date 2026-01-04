# UniBot React Frontend

This is the React-based frontend for UniBot, built with Vite.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── Header.jsx
│   │   ├── ChatContainer.jsx
│   │   ├── InputArea.jsx
│   │   └── WelcomeScreen.jsx
│   ├── utils/           # Utility functions
│   │   ├── api.js       # API calls
│   │   └── formatter.js # Message formatting
│   ├── App.jsx          # Main App component
│   └── main.jsx         # Entry point
├── index.html           # HTML template
├── styles.css           # Global styles
├── package.json         # Dependencies
└── vite.config.js       # Vite configuration
```

## Features

- React-based component architecture
- Real-time chat interface
- Backend status monitoring
- Message formatting (markdown support)
- Responsive design
- Auto-scrolling chat

