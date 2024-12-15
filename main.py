# Import the Flask application instance and SocketIO object
from app import app, socketio

# This file exists to expose the application for WSGI servers
# The actual server is started from app.py when run directly
