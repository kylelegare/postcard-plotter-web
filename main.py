# Configure eventlet first before any other imports
import eventlet
eventlet.monkey_patch()

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    # Import Flask app and socketio after eventlet configuration
    from app import app, socketio
    
    if __name__ == '__main__':
        print("Starting server on port 5000...")
        # Start the server with eventlet
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,  # Disable reloader to prevent conflicts
            log_output=True
        )
except Exception as e:
    import traceback
    logger.error(f"Failed to start server: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise
