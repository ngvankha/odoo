/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SimpleChatbot extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            isOpen: false,
            messages: [],
            currentMessage: "",
            isLoading: false,
            isConfigured: false,
            isEnabled: true,
            welcomeMessage: "Xin chào! Tôi là chatbot AI của bạn. Tôi có thể giúp gì cho bạn?"
        });

        onMounted(async () => {
            await this.checkConfiguration();
        });
    }

    async checkConfiguration() {
        try {
            const result = await this.rpc('/simple_chatbot/get_config', {});
            this.state.isConfigured = result.config.webhook_configured;
            this.state.isEnabled = result.config.enabled;
            this.state.welcomeMessage = result.config.welcome_message;
            
            // Set initial message
            if (this.state.isEnabled) {
                if (this.state.isConfigured) {
                    this.state.messages = [
                        { 
                            text: this.state.welcomeMessage, 
                            isBot: true, 
                            timestamp: new Date()
                        }
                    ];
                } else {
                    this.state.messages = [
                        { 
                            text: "⚠️ Chatbot chưa được cấu hình. Vui lòng vào Settings → General Settings → Simple Chatbot để cấu hình webhook n8n.", 
                            isBot: true, 
                            timestamp: new Date(),
                            isError: true
                        }
                    ];
                }
            } else {
                this.state.messages = [
                    { 
                        text: "❌ Simple Chatbot đã bị tắt. Vui lòng vào Settings → General Settings → Simple Chatbot để bật lại.", 
                        isBot: true, 
                        timestamp: new Date(),
                        isError: true
                    }
                ];
            }
        } catch (error) {
            console.error("Error checking configuration:", error);
            this.state.isConfigured = false;
            this.state.isEnabled = true;
            this.state.messages = [
                { 
                    text: "❌ Lỗi khi tải cấu hình chatbot.", 
                    isBot: true, 
                    timestamp: new Date(),
                    isError: true
                }
            ];
        }
    }

    toggleChatbot() {
        this.state.isOpen = !this.state.isOpen;
    }

    async sendMessage() {
        if (!this.state.currentMessage.trim() || this.state.isLoading) {
            return;
        }

        const userMessage = this.state.currentMessage.trim();
        this.state.currentMessage = "";

        // Thêm tin nhắn của người dùng
        this.state.messages.push({
            text: userMessage,
            isBot: false,
            timestamp: new Date()
        });

        // Hiển thị loading
        this.state.isLoading = true;
        const loadingMessage = {
            text: "Đang suy nghĩ...",
            isBot: true,
            timestamp: new Date(),
            isLoading: true
        };
        this.state.messages.push(loadingMessage);

        try {
            if (this.state.isEnabled && this.state.isConfigured) {
                // Gửi đến n8n
                const result = await this.rpc('/simple_chatbot/send_message', {
                    message: userMessage,
                    timestamp: new Date().toISOString()
                });

                // Xóa tin nhắn loading
                const loadingIndex = this.state.messages.findIndex(msg => msg.isLoading === true);
                if (loadingIndex > -1) {
                    this.state.messages.splice(loadingIndex, 1);
                }

                if (result.success) {
                    this.state.messages.push({
                        text: result.response,
                        isBot: true,
                        timestamp: new Date(),
                        data: result.data
                    });
                } else {
                    this.state.messages.push({
                        text: `❌ ${result.response}`,
                        isBot: true,
                        timestamp: new Date(),
                        isError: true
                    });
                }
            } else {
                // Fallback message
                setTimeout(() => {
                    const loadingIndex = this.state.messages.findIndex(msg => msg.isLoading === true);
                    if (loadingIndex > -1) {
                        this.state.messages.splice(loadingIndex, 1);
                    }
                    
                    let errorMessage = "⚠️ Chatbot không khả dụng. ";
                    if (!this.state.isEnabled) {
                        errorMessage += "Vui lòng vào Settings → General Settings → Simple Chatbot để bật chatbot.";
                    } else if (!this.state.isConfigured) {
                        errorMessage += "Vui lòng vào Settings → General Settings → Simple Chatbot để cấu hình webhook n8n.";
                    }
                    
                    this.state.messages.push({
                        text: errorMessage,
                        isBot: true,
                        timestamp: new Date(),
                        isError: true
                    });
                }, 1000);
            }
        } catch (error) {
            console.error("Error sending message:", error);
            
            // Xóa tin nhắn loading
            const loadingIndex = this.state.messages.findIndex(msg => msg.isLoading === true);
            if (loadingIndex > -1) {
                this.state.messages.splice(loadingIndex, 1);
            }

            this.state.messages.push({
                text: `❌ Lỗi kết nối: ${error.message || 'Không thể kết nối đến server'}`,
                isBot: true,
                timestamp: new Date(),
                isError: true
            });

            this.notification.add("Lỗi khi gửi tin nhắn đến chatbot", {
                type: "danger"
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    onKeyPress(ev) {
        if (ev.key === 'Enter' && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    clearChat() {
        if (this.state.isEnabled) {
            if (this.state.isConfigured) {
                this.state.messages = [
                    { 
                        text: this.state.welcomeMessage, 
                        isBot: true, 
                        timestamp: new Date()
                    }
                ];
            } else {
                this.state.messages = [
                    { 
                        text: "⚠️ Chatbot chưa được cấu hình. Vui lòng vào Settings → General Settings → Simple Chatbot để cấu hình webhook n8n.", 
                        isBot: true, 
                        timestamp: new Date(),
                        isError: true
                    }
                ];
            }
        } else {
            this.state.messages = [
                { 
                    text: "❌ Simple Chatbot đã bị tắt. Vui lòng vào Settings → General Settings → Simple Chatbot để bật lại.", 
                    isBot: true, 
                    timestamp: new Date(),
                    isError: true
                }
            ];
        }
    }

    async refreshConfiguration() {
        await this.checkConfiguration();
        this.clearChat();
        this.notification.add("Đã làm mới cấu hình chatbot", {
            type: "success"
        });
    }

    formatTime(timestamp) {
        return timestamp.toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
}

SimpleChatbot.template = "simple_chatbot.ChatbotWidget";

// Đăng ký component như một systray item
registry.category("systray").add("SimpleChatbot", {
    Component: SimpleChatbot,
    isDisplayed: async (env) => {
        // Kiểm tra xem chatbot có được enable không
        try {
            const result = await env.services.rpc('/simple_chatbot/get_config', {});
            return result.config.enabled;
        } catch (error) {
            console.error("Error checking chatbot enabled status:", error);
            return true; // Default to true if error
        }
    }
});

export default SimpleChatbot;
