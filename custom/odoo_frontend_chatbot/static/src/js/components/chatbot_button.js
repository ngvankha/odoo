/** @odoo-module **/

import { Component, useState, onMounted, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FrontendChatbotButton extends Component {
    static template = "odoo_frontend_chatbot.ChatbotButton";
    
    setup() {
        this.state = useState({
            isVisible: false,
            position: 'bottom-right'
        });
        
        this.chatbotService = useService("frontend_chatbot");
        
        onWillStart(async () => {
            await this.loadConfig();
        });
    }
    
    async loadConfig() {
        const config = await this.chatbotService.getConfig();
        this.state.isVisible = config.enabled;
        this.state.position = config.position || 'bottom-right';
    }
    
    onClickChatbot() {
        // Trigger window open event
        window.dispatchEvent(new CustomEvent('open-frontend-chatbot'));
    }
}
