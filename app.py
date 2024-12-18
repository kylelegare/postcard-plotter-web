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
logging.getLogger('axidraw_controller').setLevel(logging.DEBUG)
axidraw = AxiDrawController(dev_mode=None)  # Auto-detect hardware/development mode
font_parser = FontParser()

# Log initialization status
logger.info(f"AxiDraw controller initialized in {'development' if axidraw.dev_mode else 'hardware'} mode")

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
    try:
        text = data.get('text', '')
        font_size = data.get('fontSize', 12)
        mistake_frequency = data.get('mistakeFrequency', 0.0)

        logger.debug(f"Received text update: text='{text}', fontSize={font_size}, mistakeFreq={mistake_frequency}")

        # Update font parser mistake frequency
        font_parser.set_mistake_frequency(mistake_frequency)

        # Generate preview paths
        preview_paths = font_parser.get_text_paths(text, font_size, for_preview=True)
        logger.debug(f"Generated {len(preview_paths)} paths for text")

        if preview_paths:
            # Log sample paths for debugging
            logger.debug(f"Sample of first path: {preview_paths[0]}")
            if len(preview_paths) > 1:
                logger.debug(f"Sample of second path: {preview_paths[1]}")

        # Generate preview data
        preview_data = {
            'text': text,
            'fontSize': font_size,
            'plotPaths': preview_paths
        }

        # Log the size of the data being sent
        import json
        preview_data_str = json.dumps(preview_data)
        logger.debug(f"Preview data size: {len(preview_data_str)} bytes")
        logger.debug(f"Number of paths: {len(preview_paths)}")

        # Send updated preview data back to client
        logger.debug("Emitting preview_update event")
        socketio.emit('preview_update', preview_data)
        logger.debug("Finished emitting preview_update event")

    except Exception as e:
        logger.error(f"Error handling text update: {str(e)}")
        logger.error(traceback.format_exc())
        socketio.emit('error', {'message': str(e)})

@app.route('/api/plot', methods=['POST'])
def plot_text():
    """Handle plot requests"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        font_size = data.get('fontSize', 12)

        logger.debug(f"Plot request received: text='{text}', fontSize={font_size}")

        # Generate paths specifically for plotting (not preview)
        plot_paths = font_parser.get_text_paths(text, font_size, for_preview=False)

        # Log path statistics
        logger.debug(f"Generated {len(plot_paths)} paths for plotting")
        if plot_paths:
            logger.debug(f"First plot path: {plot_paths[0]}")

            # Analyze coordinate ranges
            x_coords = [point['x'] for path in plot_paths for point in path]
            y_coords = [point['y'] for path in plot_paths for point in path]
            logger.debug(f"X range: {min(x_coords):.1f} to {max(x_coords):.1f}")
            logger.debug(f"Y range: {min(y_coords):.1f} to {max(y_coords):.1f}")

        # Send paths to AxiDraw
        result = axidraw.plot_paths(plot_paths)

        if not result['success']:
            logger.error(f"Plot failed: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500

        logger.info("Plot completed successfully")
        return jsonify(result)

    except Exception as e:
        error_msg = f"Error plotting text: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg,
            'simulation_logs': [f"Error: {str(e)}"]
        }), 500

@app.route('/api/connect', methods=['POST'])
def connect_axidraw():
    """Connect to AxiDraw device"""
    try:
        success = axidraw.connect()
        return jsonify(success)
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

# Ensure static folders exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

if __name__ == '__main__':
    print("Please run 'python main.py' to start the server")