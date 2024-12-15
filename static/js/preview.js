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
        // Clear canvas with white background
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        const text = document.getElementById('messageText').value;
        if (!text) return;
        
        const fontSize = document.getElementById('fontSize').value;
        
        this.ctx.save();
        
        // Set up text rendering
        this.ctx.fillStyle = '#000';
        this.ctx.font = `${fontSize}px Arial`;
        this.ctx.textBaseline = 'top';
        
        // Position text with comfortable margins
        const x = 50;
        let y = 50;
        
        // Split text into lines and render
        const lines = text.split('\n');
        const lineHeight = fontSize * 1.5;
        
        lines.forEach(line => {
            this.ctx.fillText(line, x, y);
            y += lineHeight;
        });
        
        this.ctx.restore();
    }
}

// Initialize preview when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.postcardPreview = new PostcardPreview();
});
