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
        if (this.shouldEndScript) {
            this.endScript();
        } else if (
            this.currentStep.data.chatbot_step_type === 'forward_operator' &&
            this.currentStep.data.chatbot_operator_found
        ) {
            this.messaging.publicLivechatGlobal.chatWindow.enableInput();
        } else if (this.isExpectingUserInput) {
            if (this.messaging.publicLivechatGlobal.isLastMessageFromCustomer) {
                // ✅ Xử lý đặc biệt cho AI Chat
                if (this.currentStep.data.chatbot_step_type === 'ai_chat') {
                    this.setIsTyping();
                    this.processAiChatStep().then((success) => {
                        if (success) {
                            // AI đã trả lời, tiếp tục với step hiện tại để chờ input tiếp theo
                            this.messaging.publicLivechatGlobal.chatWindow.enableInput();
                        }
                    });
                    return;
                } 
                
                // user has already typed a message in -> trigger next step
                this.setIsTyping();
                this.update({
                    nextStepTimeout: setTimeout(
                        this.triggerNextStep,
                        this.messageDelay,
                    ),
                });
            } else {
                this.messaging.publicLivechatGlobal.chatWindow.enableInput();
            }
        } else {
            let triggerNextStep = true;
            if (this.currentStep.data.chatbot_step_type === 'question_selection') {
                if (!this.messaging.publicLivechatGlobal.isLastMessageFromCustomer) {
                    // if there is no last message or if the last message is from the bot
                    // -> don't trigger the next step, we are waiting for the user to pick an option
                    triggerNextStep = false;
                }
            }

            if (triggerNextStep) {
                let nextStepDelay = this.messageDelay;
                if (this.messaging.publicLivechatGlobal.chatWindow.widget.$('.o_livechat_chatbot_typing').length !== 0) {
                    // special case where we already have a "is typing" message displayed
                    // can happen when the previous step did not trigger any message posted from the bot
                    // e.g: previous step was "forward_operator" and no-one is available
                    // -> in that case, don't wait and trigger the next step immediately
                    nextStepDelay = 0;
                } else {
                    this.setIsTyping();
                }

                this.update({
                    nextStepTimeout: setTimeout(
                        this.triggerNextStep,
                        nextStepDelay,
                    ),
                });
            }
        }

        if (!this.hasRestartButton) {
            this.messaging.publicLivechatGlobal.chatWindow.widget.$('.o_livechat_chatbot_main_restart').hide();
        }
    },

    isExpectingUserInput: attr({
        compute() {
            if (!this.currentStep) {
                return clear();
            }
            return [
                'question_phone',
                'question_email',
                'free_input_single',
                'free_input_multi',
                'ai_chat',  // ✅ Thêm ai_chat vào list expecting input
            ].includes(this.currentStep.data.chatbot_step_type);
        },
        default: false,
    }),

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