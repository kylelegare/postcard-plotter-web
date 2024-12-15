# Postcard Plotter Web Interface

A web interface for controlling AxiDraw Mini to write text on postcards with custom font support. The system implements coordinate scaling, font parsing, and plotting simulation specifically optimized for the AxiDraw Mini workspace.

## Features

- Custom font parsing and rendering
- AxiDraw Mini workspace simulation
- Coordinate scaling for postcard writing
- Web-based control interface
- Preview functionality with real-time text layout
- Support for intentional writing variations
- Automatic font switching between preview and plotting
- Word wrapping and text positioning optimization

## Requirements

- Python 3.11+
- AxiDraw Mini plotter 
- Modern web browser
- USB connection for AxiDraw
- [pyaxidraw](https://axidraw.com/doc/py_api/#installation) Python module (installed automatically)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/postcard-plotter-web.git
### GitHub Setup

1. First, create a new repository on GitHub:
   - Go to https://github.com/new
   - Name your repository (e.g., "postcard-plotter-web")
   - Leave it empty (no README, no license)
   - Copy the repository URL

2. Clone this repository to your local machine:
```bash
git clone https://github.com/YOUR_USERNAME/postcard-plotter-web.git
cd postcard-plotter-web
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Connect your AxiDraw via USB and run the application:
```bash
python main.py
```

The application will:
- Automatically detect your AxiDraw Mini through USB
- Fall back to simulation mode if no device is found
- Provide real-time connection status in the web interface
- Show detailed logs in the browser console

Note: The USB connection is handled by the pyaxidraw module, which searches for available AxiDraw devices on startup. You don't need to specify any USB ports or connection details manually.

cd postcard-plotter-web
```

2. Install the AxiDraw Python module:
```bash
python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip
```

3. Install other Python dependencies:
```bash
pip install flask flask-socketio fonttools
```

4. Connect your AxiDraw Mini via USB:
- Connect the USB cable between your computer and the AxiDraw Mini
- The device uses a standard USB connection and is detected as a serial device
- No additional driver installation needed on most systems
- The application automatically detects the AxiDraw through pyaxidraw's USB detection
- If multiple AxiDraw devices are connected, the first available one will be used
- Connection issues are handled gracefully with fallback to simulation mode

5. Run the application:
```bash
python main.py
```

### USB Connection Details

The application automatically handles USB connection to your AxiDraw Mini:
1. On startup, it searches all available USB ports for AxiDraw devices
2. Uses pyaxidraw's built-in device detection
3. Automatically falls back to simulation mode if no device is found
4. Provides real-time connection status in the web interface
5. Handles connection/disconnection events during operation

#### Troubleshooting USB Connection:
- Ensure the AxiDraw is powered on
- Try unplugging and reconnecting the USB cable
- Check if the device appears in your system's USB devices list
- The status panel in the web interface shows current connection state
- Check the browser console for detailed connection logs

6. Open a web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Connect to AxiDraw:
   - Click the "Connect" button
   - The system will automatically detect your AxiDraw Mini
   - If no device is found, it will run in simulation mode

2. Create your text:
   - Enter text in the input field
   - Adjust font size using the slider
   - Text automatically wraps to fit the postcard
   - Preview updates in real-time

3. Preview and Plot:
   - Check the preview to see exact text placement
   - The preview uses the regular font (PremiumUltra54)
   - Plotting uses the single-stroke version (PremiumUltra54SL)
   - Click "Plot" to begin writing

## Development Setup

The project uses Flask for the web interface and custom font parsing for single-stroke text rendering. The coordinate system is specifically calibrated for the AxiDraw Mini workspace.

### Project Structure
```
.
├── static/
│   ├── css/           # Stylesheet files
│   │   ├── style.css  # Main application styles
│   │   └── fonts.css  # Font-specific styles
│   ├── js/            # JavaScript files
│   │   ├── preview.js # Real-time preview handling
│   │   └── axidraw.js # AxiDraw control interface
│   └── fonts/         # Font files (PremiumUltra54 and SL variant)
├── templates/         # HTML templates
│   └── index.html    # Main application interface
├── app.py            # Flask application with WebSocket support
├── main.py           # Entry point
├── font_parser.py    # Custom font handling and text layout
└── axidraw_controller.py  # AxiDraw interface with simulation support
```

### Local Development

The application includes a development mode that simulates AxiDraw operations:
- No physical hardware required for testing
- Real-time preview of plotting paths
- Accurate simulation of pen movements
- Detailed logging of operations

### Hardware Notes

This application is specifically designed for the AxiDraw Mini:
- Uses optimized workspace coordinates
- Handles USB connection automatically
- Implements proper pen up/down timing
- Maintains accurate scaling for postcards

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Uses the AxiDraw Python API from Evil Mad Scientist Laboratories
- Custom font processing powered by FontTools
- Real-time updates via Flask-SocketIO
