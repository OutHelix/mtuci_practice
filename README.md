# Animal Detection System

A web application for detecting cats and dogs in images using YOLO neural network.

## Features

- Upload images for animal detection
- Adjustable confidence threshold
- Real-time detection results
- Detection history with thumbnails
- PDF report generation (both individual and full reports)
- Statistics dashboard
- Responsive design

## Project Structure

```
animal_detection_app/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database models
│   ├── detection_logic.py  # YOLO detection logic
│   ├── pdf_generator.py    # PDF report generation
│   ├── requirements.txt    # Python dependencies
│   ├── models/
│   │   └── yolo11n.pt     # YOLO model file (already included)
│   └── uploads/           # Uploaded images
├── frontend/
│   ├── index.html         # Main HTML file
│   ├── css/
│   │   └── style.css      # Stylesheet
│   └── js/
│       └── main.js        # Frontend JavaScript
└── README.md              # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Modern web browser (Chrome, Firefox, Edge)

## Quick Start Guide

### 1. Clone the Repository

```bash
git clone https://github.com/OutHelix/mtuci_practice.git
cd mtuci_practice
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Backend Server

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment if not already activated
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Start the Flask server
python app.py
```

You should see output similar to:
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://192.168.x.x:5000
```

### 4. Open the Frontend

Since the frontend runs separately, you have several options:

#### Option A: Using Live Server (Recommended for development)

1. Install Live Server extension in VS Code
2. Open the `frontend` folder in VS Code
3. Right-click on `index.html` and select "Open with Live Server"
4. The application will open in your browser at `http://127.0.0.1:5500/frontend/`

#### Option B: Direct file access

Simply open `frontend/index.html` in your web browser:
- Double-click the file in your file explorer
- Or drag and drop it into your browser

#### Option C: Using Python's HTTP server (Alternative)

```bash
# Open a new terminal/tab
cd frontend
python -m http.server 8080
```
Then open `http://localhost:8080` in your browser.

### 5. Connect Frontend to Backend

The frontend is configured to connect to `http://localhost:5000` by default. 
Make sure:
1. Backend is running on port 5000
2. Both frontend and backend are running simultaneously

## Troubleshooting

### Common Issues

#### 1. Port 5000 already in use
**Solution:** Change the port in `backend/app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')  # Change port to 5001
```
Also update `frontend/js/main.js`:
```javascript
const API_BASE_URL = 'http://localhost:5001/api';  // Match the new port
```

#### 2. CORS errors in browser console
**Solution:** The backend already has CORS enabled. Make sure both servers are running.

#### 3. "No module named 'ultralytics'"
**Solution:** Make sure you installed all requirements:
```bash
cd backend
pip install -r requirements.txt
```

#### 4. Frontend can't connect to backend
**Solution:** 
1. Check if backend is running: `http://localhost:5000/api/test`
2. Check browser console for errors (F12 → Console)
3. Make sure no firewall is blocking the connection

### Database Issues

If you encounter database errors:
```bash
cd backend
# Remove old database and restart
rm detections.db
python app.py
```

## Usage Instructions

1. **Upload Image**: Click "Choose File" to select an image (JPG, PNG, etc.)
2. **Adjust Confidence**: Use the slider (0.01 to 0.99)
3. **Detect Animals**: Click "Detect Animals" button
4. **View Results**: See detection results and statistics
5. **Check History**: View all previous detections
6. **Export Reports**: Download PDF reports for individual or all detections

## API Documentation

### Test Connection
```bash
GET http://localhost:5000/api/test
```

### Upload Image
```bash
POST http://localhost:5000/api/upload
Content-Type: multipart/form-data

Parameters:
- image: File upload
- confidence: Float (0.01-0.99)
```

### Get History
```bash
GET http://localhost:5000/api/history
```

### Get Single History Item
```bash
GET http://localhost:5000/api/history/{id}
```

### Get Statistics
```bash
GET http://localhost:5000/api/stats
```

### Export Full PDF Report
```bash
GET http://localhost:5000/api/export/pdf
```

### Export Single PDF Report
```bash
GET http://localhost:5000/api/export/pdf/{id}
```

### Clear History
```bash
POST http://localhost:5000/api/clear
```

## Development

### Running in Development Mode

```bash
# Backend (with auto-reload)
cd backend
python app.py

# Frontend (with Live Server)
# Open frontend/index.html with Live Server
```

### Project Structure Details

- **Backend**: Flask REST API with SQLite database
- **Frontend**: Vanilla HTML/CSS/JS with no frameworks
- **Model**: YOLOv8 (yolo11n.pt) for object detection
- **Database**: SQLite for storing detection history

### Adding New Features

1. **New API endpoint**: Add to `backend/app.py`
2. **Database changes**: Update `backend/database.py`
3. **Frontend changes**: Update HTML/CSS/JS in `frontend/`
4. **Detection logic**: Modify `backend/detection_logic.py`

## Dependencies

### Backend Dependencies
See `backend/requirements.txt` for complete list:
- Flask: Web framework
- ultralytics: YOLO model
- opencv-python: Image processing
- reportlab: PDF generation
- Flask-SQLAlchemy: Database ORM
- Flask-CORS: Cross-origin support

### Frontend Dependencies
- Font Awesome: Icons
- No external JS frameworks

## License

MIT License

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Open an issue on GitHub
3. Ensure you have followed all setup steps

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request