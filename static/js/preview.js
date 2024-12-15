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
    
    drawPaths(paths) {
        console.log('Drawing paths:', paths);
        
        // Clear canvas
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Add grid for debugging
        this.drawGrid();
        
        if (!paths || paths.length === 0) {
            console.log('No paths to draw');
            return;
        }
        
        this.ctx.save();
        
        // Add margin and center vertically
        this.ctx.translate(50, 50);
        
        // Draw text paths
        paths.forEach((path, pathIndex) => {
            if (!path || path.length === 0) return;
            
            console.log(`Drawing path ${pathIndex}:`, path);
            
            // Draw the path
            this.ctx.beginPath();
            this.ctx.strokeStyle = 'black';
            this.ctx.lineWidth = 1;
            
            path.forEach((point, index) => {
                if (index === 0) {
                    this.ctx.moveTo(point.x, point.y);
                } else {
                    this.ctx.lineTo(point.x, point.y);
                }
            });
            this.ctx.stroke();
            
            // Draw points and coordinates for debugging
            path.forEach((point, index) => {
                // Draw point
                this.ctx.fillStyle = index === 0 ? 'green' : 'red';
                this.ctx.beginPath();
                this.ctx.arc(point.x, point.y, 2, 0, Math.PI * 2);
                this.ctx.fill();
                
                // Draw coordinates
                this.ctx.fillStyle = 'blue';
                this.ctx.font = '8px monospace';
                this.ctx.fillText(
                    `(${Math.round(point.x)},${Math.round(point.y)})`,
                    point.x + 5,
                    point.y - 5
                );
            });
        });
        
        this.ctx.restore();
    }
    
    drawGrid() {
        // Draw light grid for reference
        this.ctx.strokeStyle = '#eee';
        this.ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x < this.width; x += 50) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.height);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y < this.height; y += 50) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.width, y);
            this.ctx.stroke();
        }
    }
}

// Initialize preview when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.postcardPreview = new PostcardPreview();
});
