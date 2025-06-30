/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FrontendChatbotWindow extends Component {
    static template = "odoo_frontend_chatbot.ChatbotWindow";
    
    setup() {
        this.state = useState({
            isOpen: false,
            position: 'bottom-right',
            messages: [],
            inputValue: '',
            isLoading: false,
            isTyping: false
        });
        
        this.chatbotService = useService("frontend_chatbot");
        this.notification = useService("notification");
        this.inputRef = useRef("chatInput");
        this.messagesRef = useRef("messagesContainer");
        
        onWillStart(async () => {
            await this.loadConfig();
            await this.loadInitialMessages();
        });
        
        onMounted(() => {
            // Listen for button click to open chatbot
            window.addEventListener('open-frontend-chatbot', this.openChatbot.bind(this));
        });
        
        onWillUnmount(() => {
            this.chatbotService.stopMessagePolling();
            window.removeEventListener('open-frontend-chatbot', this.openChatbot.bind(this));
        });
    }
    
    async loadConfig() {
        const config = await this.chatbotService.getConfig();
        this.state.position = config.position || 'bottom-right';
    }
    
    async loadInitialMessages() {
        const messages = await this.chatbotService.getMessages();
        this.state.messages = messages;
        this.scrollToBottom();
    }
    
    openChatbot() {
        this.state.isOpen = true;
        this.scrollToBottom();
        
        // Start polling for new messages
        this.chatbotService.startMessagePolling((newMessages) => {
            this.state.messages = [...this.state.messages, ...newMessages];
            this.scrollToBottom();
            
            // Show typing indicator briefly for bot messages
            const hasBotMessage = newMessages.some(msg => msg.is_bot);
            if (hasBotMessage) {
                this.state.isTyping = false;
            }
        });
        
        // Focus input
        setTimeout(() => {
            if (this.inputRef.el) {
                this.inputRef.el.focus();
            }
        }, 100);
    }
    
    closeChatbot() {
        this.state.isOpen = false;
        this.chatbotService.stopMessagePolling();
    }
    
    async sendMessage() {
        const message = this.state.inputValue.trim();
        if (!message || this.state.isLoading) return;
        
        this.state.isLoading = true;
        this.state.inputValue = '';
        
        // Add user message to UI immediately
        this.state.messages.push({
            id: Date.now(), // Temporary ID
            body: message,
            author_name: 'You',
            is_bot: false,
            date: new Date().toISOString()
        });
        this.scrollToBottom();
        
        // Show typing indicator
        this.state.isTyping = true;
        
        try {
            await this.chatbotService.sendMessage(message);
        } catch (error) {
            console.error('Error sending message:', error);
            this.notification.add('Failed to send message', { type: 'danger' });
        }
        
        this.state.isLoading = false;
        
        // Focus input
        if (this.inputRef.el) {
            this.inputRef.el.focus();
        }
    }
    
    onKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            if (this.messagesRef.el) {
                this.messagesRef.el.scrollTop = this.messagesRef.el.scrollHeight;
            }
        }, 50);
    }
    
    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
    }
    
    formatMessageBody(body) {
        // Basic HTML formatting
        return body.replace(/\n/g, '<br>');
    }
}
