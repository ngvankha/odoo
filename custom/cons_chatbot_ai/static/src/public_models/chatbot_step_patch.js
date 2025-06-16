/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ChatbotStep } from "@im_livechat/public_models/chatbot_step";

patch(ChatbotStep.prototype, {
    /**
     * Enhanced validation for AI chat steps
     */
    get isAiChatStep() {
        return this.data && this.data.chatbot_step_type === 'ai_chat';
    },

    /**
     * Check if step expects user input - include AI chat
     */
    get expectsUserInput() {
        if (this.isAiChatStep) {
            return true;
        }
        return this._super.expectsUserInput || false;
    },

    /**
     * AI chat steps are never last steps (they continue conversation)
     */
    get isLastStep() {
        if (this.isAiChatStep) {
            return false;
        }
        return this._super.isLastStep || false;
    }
});