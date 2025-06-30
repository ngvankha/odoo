/** @odoo-module **/

import { registry } from "@web/core/registry";
import { whenReady } from "@odoo/owl";

const startFrontendChatbot = {
    dependencies: ["frontend_chatbot"],
    async start(env, { frontend_chatbot }) {
        const settings = await frontend_chatbot.getSettings();
        if (settings.enabled) {
            await whenReady();
            
            // Create container div
            const container = document.createElement('div');
            container.id = 'frontend-chatbot-container';
            document.body.appendChild(container);
            
            // Simple approach: directly create and append elements
            const buttonEl = document.createElement('div');
            buttonEl.className = `o_frontend_chatbot_button ${settings.position}`;
            buttonEl.innerHTML = `
                <button class="btn btn-primary o_chatbot_toggle" title="Chat with Odoo Assistant">
                    <i class="fa fa-comments"></i>
                </button>
            `;
            
            const windowEl = document.createElement('div');
            windowEl.className = `o_frontend_chatbot_window ${settings.position}`;
            windowEl.style.display = 'none';
            windowEl.innerHTML = `
                <div class="o_chatbot_header">
                    <div class="o_chatbot_title">
                        <i class="fa fa-robot"></i> Odoo Assistant
                    </div>
                    <button class="o_chatbot_close">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                <div class="o_chatbot_body">
                    <div class="o_chatbot_messages">
                        <div class="o_message o_bot_message">
                            <div class="o_message_content">${settings.welcomeMessage}</div>
                        </div>
                    </div>
                    <div class="o_chatbot_composer">
                        <input type="text" class="o_composer_input" placeholder="Type your message...">
                        <button class="o_send_button">
                            <i class="fa fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            `;
            
            container.appendChild(buttonEl);
            container.appendChild(windowEl);
            
            // Add event listeners
            const toggleButton = buttonEl.querySelector('.o_chatbot_toggle');
            const closeButton = windowEl.querySelector('.o_chatbot_close');
            const sendButton = windowEl.querySelector('.o_send_button');
            const inputField = windowEl.querySelector('.o_composer_input');
            const messagesContainer = windowEl.querySelector('.o_chatbot_messages');
            
            let isOpen = false;
            
            toggleButton.addEventListener('click', () => {
                isOpen = !isOpen;
                windowEl.style.display = isOpen ? 'block' : 'none';
                toggleButton.innerHTML = isOpen ? 
                    '<i class="fa fa-times"></i>' : 
                    '<i class="fa fa-comments"></i>';
            });
            
            closeButton.addEventListener('click', () => {
                isOpen = false;
                windowEl.style.display = 'none';
                toggleButton.innerHTML = '<i class="fa fa-comments"></i>';
            });
            
            const sendMessage = async () => {
                const message = inputField.value.trim();
                if (!message) return;
                
                // Add user message
                const userMsg = document.createElement('div');
                userMsg.className = 'o_message o_user_message';
                userMsg.innerHTML = `<div class="o_message_content">${message}</div>`;
                messagesContainer.appendChild(userMsg);
                
                inputField.value = '';
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                try {
                    // Send to backend (simplified - just echo for now)
                    setTimeout(() => {
                        const botMsg = document.createElement('div');
                        botMsg.className = 'o_message o_bot_message';
                        botMsg.innerHTML = `<div class="o_message_content">I received your message: "${message}". I'm still learning how to respond better!</div>`;
                        messagesContainer.appendChild(botMsg);
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }, 1000);
                } catch (error) {
                    console.error('Error sending message:', error);
                }
            };
            
            sendButton.addEventListener('click', sendMessage);
            inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
    }
};

registry.category("services").add("start_frontend_chatbot", startFrontendChatbot);
