# UniBot Frontend

Modern web frontend for UniBot - College AI Assistant.

## Features

- Clean, modern UI design matching the design mockup
- Real-time chat interface
- Suggested questions for quick access
- Backend status indicator
- Responsive design for mobile and desktop
- Markdown support for formatted messages
- Clickable source links
- No evaluator feedback shown to users

## Setup

### 1. Install Frontend Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

### 2. Start the Backend API Server

From the `frontend` directory:
```bash
python api_server.py
```

Or from the root directory:
```bash
cd frontend
python api_server.py
```

The API server will start on `http://127.0.0.1:8000`

### 3. Open the Frontend

**Option 1: Using Python HTTP Server**
```bash
# In a new terminal, from the frontend directory
python -m http.server 8080
```
Then open http://localhost:8080 in your browser

**Option 2: Using Node.js**
```bash
cd frontend
npx serve
```

**Option 3: Direct File**
- Simply double-click `index.html` to open in your browser
- Note: Some browsers may block API calls due to CORS. Use a local server (Option 1 or 2) for best results.

## Configuration

If you need to change the API port, update both:
1. `api_server.py` - Change the port in `uvicorn.run(app, host="127.0.0.1", port=8000)`
2. `app.js` - Change `API_BASE_URL` to match

## Files

- `index.html` - Main HTML structure
- `styles.css` - Styling and layout (matches design mockup)
- `app.js` - Frontend logic and API integration
- `api_server.py` - FastAPI backend server
- `requirements.txt` - Python dependencies for API server
- `README.md` - This file

## Architecture

- **Frontend**: Pure HTML/CSS/JavaScript (no build step required)
- **Backend**: FastAPI server that wraps UniBot functionality
- **Communication**: REST API with JSON
- **CORS**: Enabled for local development

## Notes

- The frontend connects to the FastAPI backend (not Gradio)
- Evaluator feedback is automatically filtered out
- Source links are clickable and open in new tabs
- The interface is fully responsive for mobile devices
- Backend status is checked automatically and shown in the header

