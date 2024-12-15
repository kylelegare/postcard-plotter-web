class PostcardPreview {
// Font loading observer
class FontLoadObserver {
    static async waitForFont(fontFamily) {
        const font = new FontFace(fontFamily, `url('/static/fonts/PremiumUltra54.ttf')`);
        try {
            await font.load();
            document.fonts.add(font);
            return true;
        } catch (error) {
            console.error('Font loading error:', error);
            return false;
        }
    }
}

    constructor() {
        this.canvas = document.getElementById('previewCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.socket = io();
        
        // Wait for font to load before initializing
        FontLoadObserver.waitForFont('PremiumUltra').then(() => {
            console.log('PremiumUltra font loaded');
            this.setupCanvas();
        }).catch(err => {
            console.warn('Font loading failed, falling back to system font:', err);
            this.setupCanvas();
        });
    }
    
    setupCanvas() {
        
        // Postcard dimensions (6" × 4" at 100 DPI)
        this.width = 600;
        this.height = 400;
        
        // Handle high DPI displays
        const dpr = window.devicePixelRatio || 1;
        
        // Set display size (css pixels)
        this.canvas.style.width = this.width + 'px';
        this.canvas.style.height = this.height + 'px';
        
        // Set actual size in memory (scaled for retina)
        this.canvas.width = this.width * dpr;
        this.canvas.height = this.height * dpr;
        
        // Scale all drawing operations by the dpr
        this.ctx.scale(dpr, dpr);
        
        this.setupEventListeners();
        this.setupWebSocket();
        
        // Initial clear
        this.clear();
    }
    
    clear() {
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.width, this.height);
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(10, 10, this.width - 20, this.height - 20);
    }
    
    setupEventListeners() {
        const messageText = document.getElementById('messageText');
        const fontSize = document.getElementById('fontSize');
        const fontSizeValue = document.getElementById('fontSizeValue');
        const mistakeFrequency = document.getElementById('mistakeFrequency');
        const mistakeValue = document.getElementById('mistakeValue');
        
        messageText.addEventListener('input', () => {
            this.updatePreview();
        });
        
        fontSize.addEventListener('input', (e) => {
            fontSizeValue.textContent = `${e.target.value}pt`;
            this.updatePreview();
        });

        mistakeFrequency.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            // Map slider values to specific ratios
            const ratios = {
                0: 'Never',
                1: '1 in 500',
                2: '1 in 100',
                3: '1 in 50',
                4: '1 in 10'
            };
            mistakeValue.textContent = ratios[value];
            this.updatePreview();
        });
    }
    
    setupWebSocket() {
        this.socket.on('connect', () => {
            console.log('Socket connected');
        });

        this.socket.on('preview_update', (data) => {
            console.log('Received preview update:', data);
            if (data && data.plotPaths) {
                console.log(`Processing ${data.plotPaths.length} paths`);
                this.drawPaths(data);
            } else {
                console.log('No valid plot paths in preview update');
            }
        });

        this.socket.on('disconnect', () => {
            console.log('Socket disconnected');
        });
    }
    
    updatePreview() {
        const text = document.getElementById('messageText').value;
        const fontSize = document.getElementById('fontSize').value;
        const mistakeFrequency = document.getElementById('mistakeFrequency').value;
        
        this.socket.emit('update_text', {
            text: text,
            fontSize: parseInt(fontSize),
            // Convert slider value to actual frequency ratio
            mistakeFrequency: (() => {
                const ratios = {
                    0: 0.0,      // Never
                    1: 0.002,    // 1 in 500
                    2: 0.01,     // 1 in 100
                    3: 0.02,     // 1 in 50
                    4: 0.1       // 1 in 10
                };
                return ratios[parseInt(mistakeFrequency)] || 0.0;
            })()
        });
    }
    
    drawPaths(data) {
        // Clear canvas and set up initial state
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.ctx.save();
        
        // Draw postcard background
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw subtle postcard border
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(10, 10, this.width - 20, this.height - 20);
        
        if (!data || !data.text) {
            console.log("No valid text provided");
            this.ctx.restore();
            return;
        }
        
        // Set up text rendering with preview font
        this.ctx.fillStyle = '#000';
        this.ctx.font = `${data.fontSize}px PremiumUltra`;
        this.ctx.textBaseline = 'top';
        
        const margin = 20;
        const lineHeight = data.fontSize * 1.2;
        const maxWidth = this.width - (margin * 2);
        
        // Split text into lines
        const lines = data.text.split('\n');
        let y = margin;
        
        // Draw each line
        lines.forEach(line => {
            let x = margin;
            const words = line.split(' ');
            let currentLine = '';
            
            // Process words for wrapping
            words.forEach(word => {
                const testLine = currentLine ? currentLine + ' ' + word : word;
                const metrics = this.ctx.measureText(testLine);
                
                if (metrics.width > maxWidth && currentLine) {
                    this.ctx.fillText(currentLine, x, y);
                    currentLine = word;
                    y += lineHeight;
                } else {
                    currentLine = testLine;
                }
            });
            
            // Draw remaining text in current line
            if (currentLine) {
                this.ctx.fillText(currentLine, x, y);
                y += lineHeight;
            }
        });
        
        // Draw strike-throughs for mistakes if any
        if (data.plotPaths) {
            this.ctx.strokeStyle = '#000';
            this.ctx.lineWidth = 1;
            
            // Look for strike-through paths (which are always 2 points for mistakes)
            data.plotPaths.forEach(path => {
                if (path.length === 2) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(path[0].x, path[0].y);
                    this.ctx.lineTo(path[1].x, path[1].y);
                    this.ctx.stroke();
                }
            });
        }
        
        this.ctx.restore();
    }
}

// Initialize preview when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.postcardPreview = new PostcardPreview();
});
