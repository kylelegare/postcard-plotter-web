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
        this.socket.on('preview_update', (data) => {
            this.drawPaths(data.plotPaths);
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
        // Draw postcard background
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw subtle postcard border
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(10, 10, this.width - 20, this.height - 20);
        
        if (!data.plotPaths || !data.plotPaths.length) return;
        
        this.ctx.save();
        
        // Set up path rendering with a pen-like appearance
        this.ctx.strokeStyle = '#1a1a1a';
        this.ctx.lineWidth = 1;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        
        // Draw each path
        data.plotPaths.forEach((path, index) => {
            if (!path || path.length < 2) return;
            
            // Log path info for debugging
            console.log(`Drawing path ${index}:`, path);
            
            this.ctx.beginPath();
            this.ctx.moveTo(path[0].x, path[0].y);
            
            // Draw the rest of the points
            for (let i = 1; i < path.length; i++) {
                this.ctx.lineTo(path[i].x, path[i].y);
            }
            
            this.ctx.stroke();
        });
        
        this.ctx.restore();
    }
}

// Initialize preview when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.postcardPreview = new PostcardPreview();
});
