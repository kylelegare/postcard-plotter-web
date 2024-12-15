# Configure eventlet first
import eventlet
eventlet.monkey_patch()

# Standard library imports
import os
import logging
import traceback

# Configure logging before other imports
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Third-party imports
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

# Local imports
from axidraw_controller import AxiDrawController
from font_parser import FontParser

# Initialize Flask app with explicit static folder config
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, async_mode='eventlet', logger=True, engineio_logger=True)

# Add logging for static file requests
@app.after_request
def after_request(response):
    if '/static/' in request.path:
        app.logger.debug(f'Static file requested: {request.path}')
    return response

# Initialize AxiDraw controller and font parser
# Set to development mode for testing sequence
logging.getLogger('axidraw_controller').setLevel(logging.DEBUG)
axidraw = AxiDrawController(dev_mode=False)  # Hardware mode enabled
font_parser = FontParser()

@app.route('/')
def index():
    """Render the main interface"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.debug('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.debug('Client disconnected')

@socketio.on('update_text')
def handle_text_update(data):
    """Handle text updates from client"""
    text = data.get('text', '')
    font_size = data.get('fontSize', 12)
    mistake_frequency = data.get('mistakeFrequency', 0.0)
    
    logger.debug(f"Received text update: text='{text}', fontSize={font_size}, mistakeFreq={mistake_frequency}")
    
    # Update font parser mistake frequency
    font_parser.set_mistake_frequency(mistake_frequency)
    
    # Generate plot paths
    plot_paths = font_parser.get_text_paths(text, font_size)
    logger.debug(f"Generated {len(plot_paths)} paths for text")
    
    if not plot_paths:
        logger.debug("No paths generated")
    else:
        logger.debug(f"Sample of first path: {plot_paths[0]}")
        if len(plot_paths) > 1:
            logger.debug(f"Sample of second path: {plot_paths[1]}")
    
    # Generate preview data
    preview_data = {
        'text': text,
        'fontSize': font_size,
        'plotPaths': plot_paths
    }
    
    # Log the size of the data being sent
    import json
    preview_data_str = json.dumps(preview_data)
    logger.debug(f"Preview data size: {len(preview_data_str)} bytes")
    logger.debug(f"Number of paths: {len(plot_paths)}")
    
    # Send updated preview data back to client
    logger.debug("Emitting preview_update event")
    socketio.emit('preview_update', preview_data)
    logger.debug("Finished emitting preview_update event")

@app.route('/api/plot', methods=['POST'])
def plot_text():
    """Handle plot requests"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        font_size = data.get('fontSize', 12)
        
        # Get text paths and plot
        # Convert text to paths and reshape for plotting
        raw_paths = font_parser.get_text_paths(text, font_size)
        
        # Reshape paths to match expected format [[{x, y}, {x, y}], ...]
        plot_paths = []
        for path in raw_paths:
            if len(path) >= 2:  # Only include valid paths with at least 2 points
                plot_paths.append(path)
        
        result = axidraw.plot_paths(plot_paths)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error plotting text: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'simulation_logs': [f"Error: {str(e)}"]
        }), 500

@app.route('/api/connect', methods=['POST'])
def connect_axidraw():
    """Connect to AxiDraw device"""
    try:
        success = axidraw.connect()
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error connecting to AxiDraw: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/disconnect', methods=['POST'])
def disconnect_axidraw():
    """Disconnect from AxiDraw device"""
    try:
        success = axidraw.disconnect()
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error disconnecting from AxiDraw: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    try:
        logger.info("Initializing Flask server...")
        # Ensure static folders exist
        os.makedirs('static', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        
        # Initialize application components
        logger.info("Initializing AxiDraw controller and font parser...")
        axidraw = AxiDrawController(dev_mode=False)  # Hardware mode enabled
        font_parser = FontParser()
        
        logger.info("Starting server on port 5000...")
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,
            log_output=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
