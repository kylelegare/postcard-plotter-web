import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from axidraw_controller import AxiDrawController
from font_parser import FontParser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app with explicit static folder config
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Add logging for static file requests
@app.after_request
def after_request(response):
    if '/static/' in request.path:
        app.logger.debug(f'Static file requested: {request.path}')
    return response

# Initialize AxiDraw controller and font parser
axidraw = AxiDrawController()
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
    
    if plot_paths:
        logger.debug(f"First path sample: {plot_paths[0]}")
    
    # Generate preview data
    preview_data = {
        'text': text,
        'fontSize': font_size,
        'plotPaths': plot_paths
    }
    logger.debug(f"Sending preview data with {len(preview_data['plotPaths'])} paths")
    
    # Send updated preview data back to client
    socketio.emit('preview_update', preview_data)

@app.route('/api/plot', methods=['POST'])
def plot_text():
    """Handle plot requests"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        font_size = data.get('fontSize', 12)
        
        # Get text paths and plot
        paths = font_parser.get_text_paths(text, font_size)
        result = axidraw.plot_paths(paths)
        
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
