class AxiDrawController {
    constructor() {
        this.connected = false;
        this.simulationLog = document.getElementById('simulationLog');
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const connectBtn = document.getElementById('connectBtn');
        const plotBtn = document.getElementById('plotBtn');
        
        connectBtn.addEventListener('click', () => {
            if (!this.connected) {
                this.connect();
            } else {
                this.disconnect();
            }
        });
        
        plotBtn.addEventListener('click', () => {
            this.plotMessage();
        });
    }
    
    async connect() {
        try {
            this.clearSimulationLog();
            this.addSimulationLog('Attempting to connect to AxiDraw...');
            
            const response = await fetch('/api/connect', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.connected = true;
                this.updateStatus('Connected to AxiDraw (Development Mode)', 'success');
                this.addSimulationLog('Connected in development mode - all operations will be simulated');
                this.updateButtons(true);
            } else {
                throw new Error(data.error || 'Failed to connect');
            }
        } catch (error) {
            this.updateStatus(`Connection error: ${error.message}`, 'danger');
            this.addSimulationLog(`Error: ${error.message}`, 'text-danger');
        }
    }
    
    async disconnect() {
        try {
            this.addSimulationLog('Disconnecting from AxiDraw...');
            
            const response = await fetch('/api/disconnect', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.connected = false;
                this.updateStatus('Disconnected from AxiDraw', 'info');
                this.addSimulationLog('Disconnected from AxiDraw');
                this.updateButtons(false);
            } else {
                throw new Error(data.error || 'Failed to disconnect');
            }
        } catch (error) {
            this.updateStatus(`Disconnection error: ${error.message}`, 'danger');
            this.addSimulationLog(`Error: ${error.message}`, 'text-danger');
        }
    }
    
    async plotMessage() {
        try {
            const text = document.getElementById('messageText').value;
            const fontSize = document.getElementById('fontSize').value;
            
            if (!text.trim()) {
                throw new Error('Please enter a message to plot');
            }
            
            this.updateStatus('Plotting message...', 'info');
            this.addSimulationLog('Starting plot simulation...');
            this.addSimulationLog(`Text: "${text}"`);
            this.addSimulationLog(`Font size: ${fontSize}pt`);
            
            const response = await fetch('/api/plot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    fontSize: parseInt(fontSize)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateStatus('Message plotted successfully', 'success');
                this.addSimulationLog('Plot simulation completed successfully');
            } else {
                throw new Error(data.error || 'Failed to plot message');
            }
        } catch (error) {
            this.updateStatus(`Plotting error: ${error.message}`, 'danger');
            this.addSimulationLog(`Error: ${error.message}`, 'text-danger');
        }
    }
    
    clearSimulationLog() {
        this.simulationLog.innerHTML = '';
    }
    
    addSimulationLog(message, className = '') {
        const entry = document.createElement('div');
        entry.className = className;
        entry.textContent = message;
        this.simulationLog.appendChild(entry);
        this.simulationLog.scrollTop = this.simulationLog.scrollHeight;
    }
    
    updateStatus(message, type) {
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.className = `alert alert-${type}`;
        statusMessage.textContent = message;
    }
    
    updateButtons(connected) {
        const connectBtn = document.getElementById('connectBtn');
        const plotBtn = document.getElementById('plotBtn');
        
        connectBtn.innerHTML = connected ? 
            '<i class="fas fa-plug-circle-xmark"></i> Disconnect' :
            '<i class="fas fa-plug"></i> Connect AxiDraw';
        
        plotBtn.disabled = !connected;
    }
}

// Initialize controller when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.axiDrawController = new AxiDrawController();
});
