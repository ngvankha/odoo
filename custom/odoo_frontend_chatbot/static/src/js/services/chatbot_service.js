/** @odoo-module **/

import { registry } from "@web/core/registry";

export const frontendChatbotService = {
    dependencies: ["rpc", "user", "notification"],
    
    start(env, { rpc, user, notification }) {
        let isOpen = false;
        let messages = [];
        let settings = {
            enabled: false,
            welcomeMessage: '',
            position: 'bottom-right'
        };
        
        // Load settings from backend
        const loadSettings = async () => {
            try {
                const result = await rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
                    model: "ir.config_parameter",
                    method: "get_param",
                    args: ["odoo_frontend_chatbot.enabled"],
                    kwargs: {}
                });
                settings.enabled = result === 'True';
                
                if (settings.enabled) {
                    const welcomeMsg = await rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
                        model: "ir.config_parameter", 
                        method: "get_param",
                        args: ["odoo_frontend_chatbot.welcome_message"],
                        kwargs: {}
                    });
                    settings.welcomeMessage = welcomeMsg || "Hello! I'm your Odoo assistant. How can I help you today? 👋";
                    
                    const position = await rpc("/web/dataset/call_kw/ir.config_parameter/get_param", {
                        model: "ir.config_parameter",
                        method: "get_param", 
                        args: ["odoo_frontend_chatbot.position"],
                        kwargs: {}
                    });
                    settings.position = position || 'bottom-right';
                }
            } catch (error) {
                console.error('Error loading chatbot settings:', error);
            }
        };
        
        // Initialize welcome message
        const initializeChat = () => {
            if (messages.length === 0 && settings.welcomeMessage) {
                messages.push({
                    id: 1,
                    body: settings.welcomeMessage,
                    isBot: true,
                    time: new Date().toLocaleTimeString(),
                    author_id: 1 // OdooBot ID
                });
            }
        };
        
        return {
            async getSettings() {
                await loadSettings();
                return settings;
            },
            
            getMessages() {
                initializeChat();
                return messages;
            },
            
            toggleChat() {
                isOpen = !isOpen;
                if (isOpen) {
                    initializeChat();
                }
                return isOpen;
            },
            
            closeChat() {
                isOpen = false;
                return isOpen;
            },
            
            minimizeChat() {
                isOpen = false;
                return isOpen;
            },
            
            async sendMessage(messageText) {
                try {
                    // Get or create private channel with OdooBot
                    const channel = await this.getOrCreateBotChannel();
                    
                    // Send message via standard mail mechanism
                    const result = await rpc("/mail/message/post", {
                        thread_id: channel.id,
                        thread_model: "mail.channel",
                        post_data: {
                            body: messageText,
                            message_type: "comment",
                        }
                    });
                    
                    // The response should come through the bus/websocket
                    // For now, we'll return a simple acknowledgment
                    return {
                        success: true,
                        message_id: result.id
                    };
                    
                } catch (error) {
                    console.error('Error sending message:', error);
                    notification.add("Failed to send message", { type: "danger" });
                    throw error;
                }
            },
            
            async getOrCreateBotChannel() {
                try {
                    // Try to find existing private channel with OdooBot
                    const channels = await rpc("/web/dataset/search_read", {
                        model: "mail.channel",
                        domain: [
                            ["channel_type", "=", "chat"],
                            ["channel_member_ids.partner_id", "=", user.partnerId]
                        ],
                        fields: ["id", "name", "channel_member_ids"]
                    });
                    
                    // Look for channel with OdooBot
                    const odoobot_partner_id = 1; // Usually OdooBot has ID 1
                    for (let channel of channels) {
                        const memberIds = channel.channel_member_ids;
                        if (memberIds.includes(odoobot_partner_id) && memberIds.length === 2) {
                            return channel;
                        }
                    }
                    
                    // Create new private channel with OdooBot
                    const newChannel = await rpc("/web/dataset/call_kw/mail.channel/create", {
                        model: "mail.channel",
                        method: "create",
                        args: [{
                            name: "Frontend Chatbot",
                            channel_type: "chat",
                            channel_member_ids: [
                                [0, 0, { partner_id: user.partnerId }],
                                [0, 0, { partner_id: odoobot_partner_id }]
                            ]
                        }],
                        kwargs: {}
                    });
                    
                    return { id: newChannel, name: "Frontend Chatbot" };
                    
                } catch (error) {
                    console.error('Error getting/creating bot channel:', error);
                    throw error;
                }
            }
        };
    }
};

registry.category("services").add("frontend_chatbot", frontendChatbotService);
