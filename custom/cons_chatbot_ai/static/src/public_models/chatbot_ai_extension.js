/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Chatbot } from "@im_livechat/public_models/chatbot";

patch(Chatbot.prototype, {
    /**
     * Process AI Chat step - enhanced version
     */
    async processAiChatStep() {
        if (!this.messaging.publicLivechatGlobal.publicLivechat.uuid) {
            console.error('No channel UUID available for AI chat');
            return false;
        }

        try {
            const result = await this.messaging.rpc({
                route: '/chatbot/step/ai_chat',
                params: {
                    channel_uuid: this.messaging.publicLivechatGlobal.publicLivechat.uuid,
                },
            });

            if (result && result.success && result.posted_message) {
                this.addMessage(result.posted_message);
                return true;
            } else if (result && result.posted_message) {
                // Display error message if any
                this.addMessage(result.posted_message);
                return false;
            } else {
                console.error('AI Chat processing failed:', result ? result.error : 'Unknown error');
                return false;
            }
        } catch (error) {
            console.error('Error processing AI chat step:', error);
            return false;
        }
    },

    /**
     * Enhanced processStep method to handle AI chat
     * This completely overrides the AI chat handling from the original module
     */
    processStep() {
        if (!this.currentStep || !this.currentStep.data) {
            return this._super();
        }

        const stepType = this.currentStep.data.chatbot_step_type;
        
        if (stepType === 'ai_chat') {
            // Handle AI chat step logic
            if (this.shouldEndScript) {
                this.endScript();
                return;
            }

            if (this.messaging.publicLivechatGlobal.isLastMessageFromCustomer) {
                // User has sent a message, process it with AI
                this.setIsTyping();
                this.processAiChatStep().then((success) => {
                    if (success || !success) {
                        // After AI response (success or failure), enable input for next user message
                        this.messaging.publicLivechatGlobal.chatWindow.enableInput();
                    }
                });
            } else {
                // No user message yet or last message was from bot, enable input
                this.messaging.publicLivechatGlobal.chatWindow.enableInput();
            }
            
            // Don't show restart button during AI chat unless explicitly needed
            if (!this.hasRestartButton) {
                this.messaging.publicLivechatGlobal.chatWindow.widget.$('.o_livechat_chatbot_main_restart').hide();
            }
            
            return;
        }

        // Call original processStep for all other step types
        return this._super();
    },

    /**
     * Enhanced validation for AI chat steps
     */
    get isExpectingUserInput() {
        if (this.currentStep && this.currentStep.data && 
            this.currentStep.data.chatbot_step_type === 'ai_chat') {
            return true;
        }
        return this._super.isExpectingUserInput || false;
    },

    /**
     * Enhanced shouldEndScript to handle AI chat steps
     */
    get shouldEndScript() {
        if (!this.currentStep) {
            return this._super.shouldEndScript || false;
        }

        // AI chat steps should not end the script automatically
        if (this.currentStep.data.chatbot_step_type === 'ai_chat') {
            // Only end script if conversation was explicitly closed
            return this.currentStep.data.conversation_closed || false;
        }

        return this._super.shouldEndScript || false;
    },

    /**
     * Override awaitUserInput for AI chat steps
     */
    awaitUserInput() {
        if (this.currentStep && this.currentStep.data && 
            this.currentStep.data.chatbot_step_type === 'ai_chat') {
            // For AI chat, don't use debounced input - process immediately when user sends message
            if (this.messaging.publicLivechatGlobal.isLastMessageFromCustomer) {
                this.processStep();
            }
            return;
        }
        
        return this._super.awaitUserInput();
    },

    /**
     * Override onKeydownInput to handle AI chat
     */
    onKeydownInput(event) {
        if (this.currentStep && this.currentStep.data && 
            this.currentStep.data.chatbot_step_type === 'ai_chat') {
            // For AI chat, don't use debounced input handling
            // Let the normal message sending flow handle it
            return;
        }

        // Call original method for other step types
        if (this.currentStep && this.currentStep.data && 
            this.currentStep.data.chatbot_step_type === 'free_input_multi') {
            this.debouncedAwaitUserInput();
        }
    }
});