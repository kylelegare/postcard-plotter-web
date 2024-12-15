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
- Connect the USB cable to your computer
- The device should be automatically detected
- No additional driver installation needed on most systems

5. Run the application:
```bash
python main.py
```

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
│   └── fonts/          # Font files (PremiumUltra54 and SL variant)
├── templates/          # HTML templates
├── app.py             # Flask application with WebSocket support
├── main.py            # Entry point
├── font_parser.py     # Custom font handling and text layout
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
