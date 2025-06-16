/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { LivechatButtonView } from "@im_livechat/public_models/livechat_button_view";

patch(LivechatButtonView.prototype, {
    /**
     * Override _sendMessageChatbotAfter to handle AI chat completely in this module
     */
    _sendMessageChatbotAfter() {
        if (this.messaging.publicLivechatGlobal.chatbot.isRedirecting) {
            return;
        }
        
        if (
            this.messaging.publicLivechatGlobal.chatbot.isActive &&
            this.messaging.publicLivechatGlobal.chatbot.currentStep &&
            this.messaging.publicLivechatGlobal.chatbot.currentStep.data
        ) {
            const stepType = this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_step_type;
            
            if (
                stepType === 'forward_operator' &&
                this.messaging.publicLivechatGlobal.chatbot.currentStep.data.chatbot_operator_found
            ) {
                return; // operator has taken over the conversation
            } 
            else if (stepType === 'free_input_multi') {
                this.messaging.publicLivechatGlobal.chatbot.debouncedAwaitUserInput();
            } 
            // Handle AI Chat - completely override the original handling
            else if (stepType === 'ai_chat') {
                // Set typing indicator and process AI chat
                this.messaging.publicLivechatGlobal.chatbot.setIsTyping();
                
                setTimeout(() => {
                    this.messaging.publicLivechatGlobal.chatbot.processStep();
                }, 500); // Delay to ensure message is saved
                
                this.messaging.publicLivechatGlobal.chatbot.saveSession();
                return; // Don't continue with regular step processing
            }
            else if (!this.messaging.publicLivechatGlobal.chatbot.shouldEndScript) {
                this.messaging.publicLivechatGlobal.chatbot.setIsTyping();
                this.messaging.publicLivechatGlobal.chatbot.update({
                    nextStepTimeout: setTimeout(
                        this.messaging.publicLivechatGlobal.chatbot.triggerNextStep,
                        this.messaging.publicLivechatGlobal.chatbot.messageDelay,
                    ),
                });
            } else {
                this.messaging.publicLivechatGlobal.chatbot.endScript();
            }
            
            this.messaging.publicLivechatGlobal.chatbot.saveSession();
        }
    }
});