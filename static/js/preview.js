class PostcardPreview {
    constructor() {
        this.canvas = document.getElementById('previewCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.socket = io();
        
        // Postcard dimensions (6" × 4" at 100 DPI)
        this.width = 600;
        this.height = 400;
        
        this.setupEventListeners();
        this.setupWebSocket();
    }
    
    setupEventListeners() {
        const messageText = document.getElementById('messageText');
        const fontSize = document.getElementById('fontSize');
        const fontSizeValue = document.getElementById('fontSizeValue');
        
        messageText.addEventListener('input', () => {
            this.updatePreview();
        });
        
        fontSize.addEventListener('input', (e) => {
            fontSizeValue.textContent = `${e.target.value}pt`;
            this.updatePreview();
        });
    }
    
    setupWebSocket() {
        this.socket.on('preview_update', (data) => {
            this.drawPaths(data.paths);
        });
    }
    
    updatePreview() {
        const text = document.getElementById('messageText').value;
        const fontSize = document.getElementById('fontSize').value;
        
        this.socket.emit('update_text', {
            text: text,
            fontSize: parseInt(fontSize)
        });
    }
    
    drawPaths(data) {
        // Draw postcard background
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw subtle postcard border
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(10, 10, this.width - 20, this.height - 20);
        
        const text = document.getElementById('messageText').value;
        if (!text) return;
        
        const fontSize = document.getElementById('fontSize').value;
        
        this.ctx.save();
        
        // Set up text rendering with a nice pen-like appearance
        this.ctx.fillStyle = '#1a1a1a';  // Slightly softer than pure black
        this.ctx.font = `${fontSize}px PremiumUltra`;  // Using our custom font
        this.ctx.textBaseline = 'top';
        
        // Calculate comfortable margins (about 1 inch at 100 DPI)
        const margin = 100;
        const x = margin;
        let y = margin;
        
        // Calculate maximum width for text wrapping
        const maxWidth = this.width - (margin * 2);
        
        // Handle text wrapping and rendering
        const words = text.split(/\s+/);
        const lineHeight = fontSize * 1.5;
        let line = '';
        
        // Process each word
        words.forEach(word => {
            const testLine = line + (line ? ' ' : '') + word;
            const metrics = this.ctx.measureText(testLine);
            
            if (metrics.width > maxWidth && line !== '') {
                // Current line is full, render it and start new line
                this.ctx.fillText(line, x, y, maxWidth);
                line = word;
                y += lineHeight;
            } else {
                // Add word to current line
                line = testLine;
            }
        });
        
        // Draw remaining text
        if (line) {
            this.ctx.fillText(line, x, y, maxWidth);
        }
        
        this.ctx.restore();
    }
}

// Initialize preview when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.postcardPreview = new PostcardPreview();
});
