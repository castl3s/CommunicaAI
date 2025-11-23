class CommunicaAI {
    constructor() {
        this.API_KEY = "ApiKey-29b2c13f-14f4-436a-92c2-bfe5dcc7f8ff";
        this.SCORING_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/9a25c432-dafa-4c43-b2ce-2eabd6aec8e5/ai_service_stream?version=2021-05-01";
        this.accessToken = null;
        this.isConnected = false;
        this.conversationHistory = [];
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeConnection();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearChatButton = document.getElementById('clearChat');
        this.exportChatButton = document.getElementById('exportChat');
        this.voiceInputButton = document.getElementById('voiceInput');
        this.quickActions = document.getElementById('quickActions');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.apiKeySection = document.getElementById('apiKeySection');
        this.apiKeyDisplay = document.getElementById('apiKeyDisplay');
        this.toggleApiKeyButton = document.getElementById('toggleApiKey');
        this.apiKeyInputContainer = document.getElementById('apiKeyInputContainer');
        this.apiKeyInput = document.getElementById('apiKeyInput');
        this.updateApiKeyButton = document.getElementById('updateApiKey');
        this.charCounter = document.getElementById('charCounter');
    }

    initializeEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.clearChatButton.addEventListener('click', () => this.clearChat());
        this.exportChatButton.addEventListener('click', () => this.exportChat());
        this.voiceInputButton.addEventListener('click', () => this.toggleVoiceInput());
        this.toggleApiKeyButton.addEventListener('click', () => this.toggleApiKeyVisibility());
        this.updateApiKeyButton.addEventListener('click', () => this.updateApiKey());
        
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.userInput.addEventListener('input', () => {
            this.sendButton.disabled = this.userInput.value.trim() === '' || !this.isConnected;
            this.autoResizeTextarea();
            this.updateCharCounter();
        });

        // Enter key for API key input
        this.apiKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.updateApiKey();
            }
        });
    }

    autoResizeTextarea() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = Math.min(this.userInput.scrollHeight, 120) + 'px';
    }

    updateCharCounter() {
        const length = this.userInput.value.length;
        this.charCounter.textContent = `${length}/1000`;
        
        if (length > 800) {
            this.charCounter.style.color = '#f1c21b';
        } else if (length >= 1000) {
            this.charCounter.style.color = '#da1e28';
        } else {
            this.charCounter.style.color = '#8d8d8d';
        }
    }

    toggleApiKeyVisibility() {
        if (this.apiKeyInputContainer.style.display === 'none') {
            this.apiKeyInputContainer.style.display = 'block';
            this.toggleApiKeyButton.textContent = 'Hide API Key';
            this.apiKeyInput.value = this.API_KEY;
        } else {
            this.apiKeyInputContainer.style.display = 'none';
            this.toggleApiKeyButton.textContent = 'Show API Key';
        }
    }

    updateApiKey() {
        const newApiKey = this.apiKeyInput.value.trim();
        if (newApiKey) {
            this.API_KEY = newApiKey;
            this.apiKeyDisplay.textContent = '••••••••••••••••';
            this.apiKeyInputContainer.style.display = 'none';
            this.toggleApiKeyButton.textContent = 'Show API Key';
            this.showNotification('API Key updated successfully!');
            
            // Reinitialize connection with new API key
            this.initializeConnection();
        } else {
            this.showNotification('Please enter a valid API key', true);
        }
    }

    toggleVoiceInput() {
        this.showNotification('Voice input feature coming soon!');
        // Voice input implementation would go here
    }

    async initializeConnection() {
        this.updateStatus('Connecting to CommunicaAI...', 'connecting');
        this.sendButton.disabled = true;
        
        try {
            await this.getAccessToken();
            this.isConnected = true;
            this.updateStatus('Connected to CommunicaAI', 'connected');
            this.sendButton.disabled = false;
            
            // Load initial content from API
            await this.loadInitialContent();
        } catch (error) {
            console.error('Connection failed:', error);
            this.updateStatus('Connection failed. Please check your API key.', 'error');
            this.isConnected = false;
            this.sendButton.disabled = true;
            this.loadFallbackContent();
        }
    }

    async getAccessToken() {
        return new Promise((resolve, reject) => {
            const req = new XMLHttpRequest();
            req.open('POST', 'https://iam.cloud.ibm.com/identity/token');
            req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            req.setRequestHeader('Accept', 'application/json');
            
            req.onload = () => {
                if (req.status === 200) {
                    try {
                        const response = JSON.parse(req.responseText);
                        this.accessToken = response.access_token;
                        resolve();
                    } catch (error) {
                        reject(error);
                    }
                } else {
                    reject(new Error(`Token request failed: ${req.status}`));
                }
            };
            
            req.onerror = () => reject(new Error('Network error'));
            req.send(`grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=${this.API_KEY}`);
        });
    }

    async loadInitialContent() {
        try {
            // Get initial greeting and quick actions from API
            const initialPayload = {
                messages: [
                    {
                        role: "user",
                        content: "Generate a welcome message for CommunicaAI - a communication-focused AI assistant that helps with content creation, language translation, voice synthesis, and communication strategies. Also provide 4-5 quick action suggestions relevant to communication tasks."
                    }
                ]
            };

            const response = await this.sendToWatson(initialPayload);
            this.processInitialResponse(response);
        } catch (error) {
            console.error('Failed to load initial content:', error);
            this.loadFallbackContent();
        }
    }

    processInitialResponse(response) {
        try {
            let botResponse = "";
            let suggestions = [];

            // Parse response based on different possible structures
            if (response.choices && response.choices.length > 0 && response.choices[0].message) {
                botResponse = response.choices[0].message.content;
            } else if (response.result && response.result.output && response.result.output.generic) {
                botResponse = response.result.output.generic[0].text;
            } else if (response.predictions && response.predictions.length > 0) {
                botResponse = response.predictions[0];
            } else if (response.text) {
                botResponse = response.text;
            }

            // Extract suggestions from response or use fallbacks
            suggestions = this.extractSuggestionsFromResponse(response) || this.getFallbackSuggestions();

            // Add welcome message
            this.addMessage(botResponse || this.getFallbackGreeting(), 'assistant');

            // Add quick actions
            this.renderQuickActions(suggestions);

        } catch (error) {
            console.error('Error processing initial response:', error);
            this.loadFallbackContent();
        }
    }

    extractSuggestionsFromResponse(response) {
        try {
            const responseText = JSON.stringify(response).toLowerCase();
            const suggestions = [];

            // Communication-focused quick action patterns
            const quickActionPatterns = [
                { pattern: /email|mail/i, suggestion: "Help me write a professional email", icon: "✉️" },
                { pattern: /presentation|speech/i, suggestion: "Create a presentation outline", icon: "📊" },
                { pattern: /translate|language/i, suggestion: "Translate text to Spanish", icon: "🌐" },
                { pattern: /social.media|post/i, suggestion: "Write a social media post", icon: "📱" },
                { pattern: /summary|summarize/i, suggestion: "Summarize this document", icon: "📄" },
                { pattern: /voice|audio/i, suggestion: "Generate voiceover script", icon: "🔊" },
                { pattern: /meeting|agenda/i, suggestion: "Create meeting agenda", icon: "📅" }
            ];

            quickActionPatterns.forEach(({ pattern, suggestion, icon }) => {
                if (responseText.match(pattern)) {
                    suggestions.push({ text: suggestion, icon });
                }
            });

            return suggestions.length > 0 ? suggestions.slice(0, 4) : null;
        } catch (error) {
            return null;
        }
    }

    getFallbackGreeting() {
        return `Welcome to CommunicaAI! 🎯

I'm your specialized AI assistant focused on communication tasks. I can help you with:

• Content creation and writing assistance
• Multi-language translation
• Voice synthesis and script writing
• Communication strategy development
• Presentation and speech preparation
• Social media content creation

What communication challenge can I help you solve today?`;
    }

    getFallbackSuggestions() {
        return [
            { text: "Help me write a professional email", icon: "✉️" },
            { text: "Translate this text to Spanish", icon: "🌐" },
            { text: "Create a social media post", icon: "📱" },
            { text: "Write a presentation outline", icon: "📊" }
        ];
    }

    loadFallbackContent() {
        this.addMessage(this.getFallbackGreeting(), 'assistant');
        this.renderQuickActions(this.getFallbackSuggestions());
    }

    renderQuickActions(suggestions) {
        this.quickActions.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const button = document.createElement('button');
            button.className = 'quick-action';
            button.innerHTML = `${suggestion.icon} ${suggestion.text}`;
            button.addEventListener('click', () => {
                this.userInput.value = suggestion.text;
                this.autoResizeTextarea();
                this.updateCharCounter();
                this.userInput.focus();
            });
            this.quickActions.appendChild(button);
        });
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || !this.isConnected) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.userInput.value = '';
        this.sendButton.disabled = true;
        this.autoResizeTextarea();
        this.updateCharCounter();

        // Hide quick actions and show typing indicator
        this.quickActions.style.display = 'none';
        this.showTypingIndicator();

        try {
            const payload = {
                messages: [
                    ...this.conversationHistory,
                    {
                        role: "user",
                        content: message
                    }
                ]
            };

            const response = await this.sendToWatson(payload);
            this.processResponse(response, message);

        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage("Sorry, I'm having trouble connecting to the service right now. Please check your API key and try again.", 'assistant');
            this.updateStatus('Connection error', 'error');
        } finally {
            this.hideTypingIndicator();
            this.quickActions.style.display = 'flex';
            this.sendButton.disabled = false;
        }
    }

    async sendToWatson(payload) {
        return new Promise((resolve, reject) => {
            const req = new XMLHttpRequest();
            req.open('POST', this.SCORING_URL);
            req.setRequestHeader('Accept', 'application/json');
            req.setRequestHeader('Authorization', `Bearer ${this.accessToken}`);
            req.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            
            req.onload = () => {
                if (req.status === 200) {
                    try {
                        const response = JSON.parse(req.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(error);
                    }
                } else {
                    reject(new Error(`API request failed: ${req.status}`));
                }
            };
            
            req.onerror = () => reject(new Error('Network error'));
            req.send(JSON.stringify(payload));
        });
    }

    processResponse(response, userMessage) {
        try {
            let botResponse = "";

            // Parse response based on different possible structures
            if (response.choices && response.choices.length > 0 && response.choices[0].message) {
                botResponse = response.choices[0].message.content;
            } else if (response.result && response.result.output && response.result.output.generic) {
                botResponse = response.result.output.generic[0].text;
            } else if (response.predictions && response.predictions.length > 0) {
                botResponse = response.predictions[0];
            } else if (response.text) {
                botResponse = response.text;
            }

            this.addMessage(botResponse || "I received your message but couldn't process it properly. Please try again.", 'assistant');

            // Update conversation history
            this.conversationHistory.push(
                { role: "user", content: userMessage },
                { role: "assistant", content: botResponse }
            );

            // Limit conversation history to prevent token limits
            if (this.conversationHistory.length > 20) {
                this.conversationHistory = this.conversationHistory.slice(-20);
            }

        } catch (error) {
            console.error('Error processing response:', error);
            this.addMessage("Sorry, I encountered an error processing your request. Please try rephrasing your question.", 'assistant');
        }
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${sender}-avatar`;
        avatar.textContent = sender === 'user' ? 'You' : 'AI';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = content;
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageContent.appendChild(bubble);
        messageContent.appendChild(time);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    updateStatus(message, type) {
        this.statusText.textContent = message;
        this.statusDot.className = 'status-dot ' + type;
    }

    showNotification(message, isError = false) {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            background: ${isError ? '#da1e28' : '#24a148'};
            color: white;
            border-radius: 6px;
            font-size: 14px;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    clearChat() {
        this.chatMessages.innerHTML = '';
        this.conversationHistory = [];
        this.loadInitialContent();
        this.showNotification('Chat cleared successfully');
    }

    exportChat() {
        const chatContent = this.conversationHistory.map(msg => 
            `${msg.role.toUpperCase()}: ${msg.content}`
        ).join('\n\n');
        
        const blob = new Blob([`CommunicaAI Conversation Export\n${new Date().toLocaleString()}\n\n${chatContent}`], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `communicaai-chat-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        this.showNotification('Conversation exported successfully');
    }
}

// Add CSS for notification animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CommunicaAI();
});