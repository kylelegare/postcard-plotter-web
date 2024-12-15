class PostcardPreview {
    constructor() {
        this.canvas = document.getElementById('previewCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.socket = io();
        
        // Postcard dimensions (6" × 4" at 100 DPI)
        this.width = 600;
        this.height = 400;
        
        // Set canvas dimensions
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        
        // Enable high DPI rendering
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
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
            this.ctx.restore();
            return;
        }
        
        // Set up text rendering with PremiumUltra font
        this.ctx.fillStyle = '#000000';
        this.ctx.font = `${data.fontSize}px PremiumUltra`;
        this.ctx.textBaseline = 'top';
        
        // Calculate text position (50px margin)
        const margin = 50;
        const x = margin;
        const y = margin;
        
        // Draw the text for preview
        this.ctx.fillText(data.text, x, y);
        
        this.ctx.restore();
    }
}

// Initialize preview when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.postcardPreview = new PostcardPreview();
});
