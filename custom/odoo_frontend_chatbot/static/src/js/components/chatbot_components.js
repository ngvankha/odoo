/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class FrontendChatbotButton extends Component {
    static template = "odoo_frontend_chatbot.ChatbotButton";
    
    setup() {
        this.chatbotService = useService("frontend_chatbot");
        this.state = useState({
            enabled: false,
            isOpen: false,
            position: 'bottom-right',
            unreadCount: 0
        });
        
        onMounted(() => {
            this.loadSettings();
        });
    }
    
    async loadSettings() {
        const settings = await this.chatbotService.getSettings();
        Object.assign(this.state, settings);
    }
    
    toggleChat() {
        this.chatbotService.toggleChat();
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) {
            this.state.unreadCount = 0;
        }
    }
}

export class FrontendChatbotWindow extends Component {
    static template = "odoo_frontend_chatbot.ChatbotWindow";
    
    setup() {
        this.chatbotService = useService("frontend_chatbot");
        this.messagesContainer = useRef("messagesContainer");
        this.messageInput = useRef("messageInput");
        
        this.state = useState({
            isOpen: false,
            position: 'bottom-right',
            messages: [],
            currentMessage: '',
            isTyping: false
        });
        
        onMounted(() => {
            this.loadMessages();
            if (this.messageInput.el) {
                this.messageInput.el.focus();
            }
        });
    }
    
    async loadMessages() {
        const messages = await this.chatbotService.getMessages();
        this.state.messages = messages;
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        if (this.messagesContainer.el) {
            this.messagesContainer.el.scrollTop = this.messagesContainer.el.scrollHeight;
        }
    }
    
    onKeyDown(ev) {
        if (ev.key === 'Enter' && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }
    
    async sendMessage() {
        const message = this.state.currentMessage.trim();
        if (!message) return;
        
        // Add user message
        const userMessage = {
            id: Date.now(),
            body: message,
            isBot: false,
            time: new Date().toLocaleTimeString()
        };
        
        this.state.messages.push(userMessage);
        this.state.currentMessage = '';
        this.scrollToBottom();
        
        // Show typing indicator
        this.state.isTyping = true;
        
        try {
            // Send to backend
            const response = await this.chatbotService.sendMessage(message);
            
            // Add bot response
            if (response && response.body) {
                const botMessage = {
                    id: Date.now() + 1,
                    body: response.body,
                    isBot: true,
                    time: new Date().toLocaleTimeString()
                };
                this.state.messages.push(botMessage);
            }
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            this.state.isTyping = false;
            this.scrollToBottom();
        }
    }
    
    minimizeChat() {
        this.chatbotService.minimizeChat();
    }
    
    closeChat() {
        this.chatbotService.closeChat();
        this.state.isOpen = false;
    }
}
