// trading-connector.js
// This file connects the frontend HTML to the Python backend
// Include this in your HTML file or integrate into the existing script

class TradingConnector {
    constructor(config = {}) {
        // For Vercel deployment, the API will be at the same domain
        // For local development: 'http://localhost:5000'
        // For Vercel: window.location.origin (same domain)
        this.apiUrl = config.apiUrl || (window.location.hostname === 'localhost' ? 'http://localhost:5000' : window.location.origin);
        this.userId = config.userId || this.generateUserId();
        this.socket = null;
        this.session = {
            asset: null,
            price: null,
            timeframe: null,
            accountType: null,
            balance: null
        };
        
        this.initializeWebSocket();
    }
    
    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeWebSocket() {
        // Connect to Socket.IO for real-time updates
        if (typeof io !== 'undefined') {
            this.socket = io(this.apiUrl);
            
            this.socket.on('connect', () => {
                console.log('Connected to trading backend');
                this.onConnected();
            });
            
            this.socket.on('market_update', (data) => {
                this.onMarketUpdate(data);
            });
            
            this.socket.on('analysis_progress', (data) => {
                this.onAnalysisProgress(data);
            });
        }
    }
    
    // API Methods
    async sendMessage(message) {
        try {
            const response = await fetch(`${this.apiUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    message: message,
                    session: this.session
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update session based on response
            if (data.action) {
                this.handleAction(data.action, data.data);
            }
            
            return data;
        } catch (error) {
            console.error('Error sending message:', error);
            return {
                text: 'Connection error. Please check if the backend is running.',
                error: true
            };
        }
    }
    
    async performAnalysis() {
        try {
            // Show loading state
            this.onAnalysisStart();
            
            const response = await fetch(`${this.apiUrl}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    ...this.session
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const analysisData = await response.json();
            this.onAnalysisComplete(analysisData);
            
            return analysisData;
        } catch (error) {
            console.error('Error performing analysis:', error);
            this.onAnalysisError(error);
            return null;
        }
    }
    
    async getMarketData(symbol) {
        try {
            const response = await fetch(`${this.apiUrl}/api/market-data/${symbol}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching market data:', error);
            return null;
        }
    }
    
    async calculatePosition(params) {
        try {
            const response = await fetch(`${this.apiUrl}/api/calculate-position`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error calculating position:', error);
            return null;
        }
    }
    
    // Session Management
    handleAction(action, data) {
        switch(action) {
            case 'asset_selected':
                this.session.asset = data.asset;
                this.session.symbol = data.symbol;
                if (this.socket) {
                    this.socket.emit('subscribe_market_data', { symbol: data.symbol });
                }
                break;
                
            case 'price_set':
                this.session.price = data.price;
                break;
                
            case 'timeframe_set':
                this.session.timeframe = data.timeframe;
                break;
                
            case 'account_set':
                this.session.accountType = data.type;
                this.session.balance = data.balance;
                break;
                
            case 'analyze':
                this.performAnalysis();
                break;
        }
    }
    
    // Event Handlers (to be overridden)
    onConnected() {
        console.log('Override onConnected to handle connection event');
    }
    
    onMarketUpdate(data) {
        console.log('Market update:', data);
    }
    
    onAnalysisStart() {
        console.log('Analysis started');
    }
    
    onAnalysisProgress(progress) {
        console.log('Analysis progress:', progress);
    }
    
    onAnalysisComplete(data) {
        console.log('Analysis complete:', data);
    }
    
    onAnalysisError(error) {
        console.error('Analysis error:', error);
    }
    
    // Helper Methods
    formatAnalysisResult(data) {
        if (!data || !data.trade_setup) return '';
        
        const setup = data.trade_setup;
        const confidence = data.confidence || 0;
        
        return `
            <div class="trade-card">
                <div class="trade-header">
                    <strong>📊 ${data.asset} Analysis - ${data.timeframe}</strong>
                    <span class="${setup.bias === 'bullish' ? 'buy-signal' : 'sell-signal'}">
                        ${setup.bias.toUpperCase()} ${confidence}%
                    </span>
                </div>
                
                <div class="trade-details">
                    <div class="trade-detail-item">
                        <span>Entry</span>
                        <strong>$${setup.entry}</strong>
                    </div>
                    <div class="trade-detail-item">
                        <span>Stop Loss</span>
                        <strong style="color: #f44336;">$${setup.stop_loss}</strong>
                    </div>
                    <div class="trade-detail-item">
                        <span>Target 1</span>
                        <strong style="color: #4CAF50;">$${setup.targets.tp1}</strong>
                    </div>
                    <div class="trade-detail-item">
                        <span>Target 2</span>
                        <strong style="color: #4CAF50;">$${setup.targets.tp2}</strong>
                    </div>
                    <div class="trade-detail-item">
                        <span>Position Size</span>
                        <strong>${setup.position_size} lots</strong>
                    </div>
                    <div class="trade-detail-item">
                        <span>Risk</span>
                        <strong>$${setup.risk_amount}</strong>
                    </div>
                </div>
                
                ${this.formatConfluenceFactors(data.analysis)}
                ${this.formatRiskWarnings(data.risk_warnings)}
            </div>
        `;
    }
    
    formatConfluenceFactors(analysis) {
        if (!analysis || !analysis.confluence_factors) return '';
        
        return `
            <div style="margin-top: 15px;">
                <strong>Confluence Factors:</strong>
                <ul>
                    ${analysis.confluence_factors.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    formatRiskWarnings(warnings) {
        if (!warnings || warnings.length === 0) return '';
        
        return `
            <div class="warning-box" style="margin-top: 15px;">
                <strong>⚠️ Risk Warning:</strong>
                <ul>
                    ${warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Utility Methods
    validateSession() {
        const required = ['asset', 'price', 'timeframe'];
        const missing = required.filter(field => !this.session[field]);
        
        if (missing.length > 0) {
            return {
                valid: false,
                missing: missing,
                message: `Please provide: ${missing.join(', ')}`
            };
        }
        
        return { valid: true };
    }
    
    resetSession() {
        this.session = {
            asset: null,
            price: null,
            timeframe: null,
            accountType: null,
            balance: null
        };
    }
    
    subscribeToAsset(symbol) {
        if (this.socket) {
            this.socket.emit('subscribe_market_data', { symbol });
        }
    }
    
    unsubscribeFromAsset(symbol) {
        if (this.socket) {
            this.socket.emit('unsubscribe_market_data', { symbol });
        }
    }
}

// Integration with existing HTML
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the connector
    const connector = new TradingConnector({
        apiUrl: 'http://localhost:5000'  // Change this to your backend URL
    });
    
    // Override event handlers for UI updates
    connector.onConnected = function() {
        const statusIndicator = document.querySelector('.status-indicator');
        if (statusIndicator) {
            statusIndicator.textContent = 'Connected to Backend';
            statusIndicator.style.color = '#4CAF50';
        }
    };
    
    connector.onMarketUpdate = function(data) {
        // Update UI with real-time market data
        console.log('Market update received:', data);
        
        // Update price display if exists
        const priceDisplay = document.getElementById('current-price');
        if (priceDisplay && data.data && data.data.price) {
            priceDisplay.textContent = `$${data.data.price.toFixed(2)}`;
        }
    };
    
    connector.onAnalysisStart = function() {
        // Show loading indicator
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.classList.add('active');
        }
        
        // Add loading message to chat
        if (window.tradingAssistant) {
            window.tradingAssistant.addMessage(
                'Starting comprehensive analysis... Activating all modules...',
                'ai'
            );
        }
    };
    
    connector.onAnalysisProgress = function(progress) {
        // Update progress bar
        const progressBar = document.querySelector('.progress-fill');
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
    };
    
    connector.onAnalysisComplete = function(data) {
        // Hide loading
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.classList.remove('active');
        }
        
        // Display results
        if (window.tradingAssistant) {
            const formattedResult = connector.formatAnalysisResult(data);
            window.tradingAssistant.addMessage(formattedResult, 'ai');
        }
    };
    
    connector.onAnalysisError = function(error) {
        // Hide loading
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.classList.remove('active');
        }
        
        // Show error message
        if (window.tradingAssistant) {
            window.tradingAssistant.addMessage(
                '❌ Analysis failed. Please check your connection and try again.',
                'ai'
            );
        }
    };
    
    // Modify the existing TradingAssistantAI to use the connector
    if (window.tradingAssistant) {
        const originalProcessMessage = window.tradingAssistant.processMessage;
        
        window.tradingAssistant.processMessage = async function(message) {
            // Send to backend
            const response = await connector.sendMessage(message);
            
            // Display response
            this.hideTyping();
            this.addMessage(response.text, 'ai');
            
            // If analysis is requested, trigger it
            if (response.action === 'analyze') {
                const validation = connector.validateSession();
                if (validation.valid) {
                    connector.performAnalysis();
                } else {
                    this.addMessage(validation.message, 'ai');
                }
            }
        };
    }
    
    // Make connector globally available
    window.tradingConnector = connector;
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TradingConnector;
}