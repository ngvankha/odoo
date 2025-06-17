/** @odoo-module **/

import { registerModel } from '@mail/model/model_core';
import { patch } from '@web/core/utils/patch';
import { attr } from '@mail/model/model_field';

// Patch vào Chatbot model đã có
patch(registerModel({name: 'Chatbot'}), 'cons_chatbot_ai.Chatbot', {
    recordMethods: {
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
        async processAiChatStep() {
            if (!this.messaging.publicLivechatGlobal.isLastMessageFromCustomer) {
                return false;
            }
            
            try {
                const result = await this.messaging.rpc({
                    route: '/chatbot/step/ai_chat',
                    params: {
                        channel_uuid: this.messaging.publicLivechatGlobal.publicLivechat.uuid,
                    },
                });
                
                if (result.success && result.posted_message) {
                    this.addMessage(result.posted_message);
                    return true;
                } else {
                    console.error('AI Chat processing failed:', result.error);
                    return false;
                }
            } catch (error) {
                console.error('Error processing AI chat:', error);
                return false;
            }
        },
    },
    fields: {
        awaitUserInputDebounceTime: attr({
            compute() {
                return 10000;
            },
        }),
        isExpectingUserInput: attr({
            compute() {
                if (!this.currentStep) {
                    return false;
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
        shouldEndScript: attr({
            /**
             * Compute method that checks if the script should be ended or not.
             * If the user has closed the conversation -> script has ended.
             *
             * Otherwise, there are 2 use cases where we want to end the script:
             *
             * If the current step is the last one AND the conversation was not taken over by a human operator
             *   1. AND we expect a user input (or we are on a selection)
             *       AND the user has already answered
             *   2. AND we don't expect a user input
             */
            compute() {
                if (!this.currentStep) {
                    return false;
                }
                if (this.currentStep.data.conversation_closed) {
                    return true;
                }
                if (this.currentStep.data.chatbot_step_is_last &&
                    this.currentStep.data.chatbot_step_type !== 'ai_chat' &&
                    (this.currentStep.data.chatbot_step_type !== 'forward_operator' ||
                    !this.currentStep.data.chatbot_operator_found)
                ) {
                    if (this.currentStep.data.chatbot_step_type === 'question_email'
                        && !this.currentStep.data.is_email_valid
                    ) {
                        // email is not (yet) valid, let the user answer / try again
                        return false;
                    } else if (
                        (this.isExpectingUserInput ||
                        this.currentStep.data.chatbot_step_type === 'question_selection') &&
                        this.messaging.publicLivechatGlobal.messages.length !== 0
                    ) {
                        if (this.messaging.publicLivechatGlobal.lastMessage.authorId !== this.messaging.publicLivechatGlobal.publicLivechat.operator.id) {
                            // we are on the last step of the script, expect a user input and the user has
                            // already answered
                            // -> end the script
                            return true;
                        }
                    } else if (!this.isExpectingUserInput) {
                        // we are on the last step of the script and we do not expect a user input
                        // -> end the script
                        return true;
                    }
                }
                return false;
            },
            default: false,
        }),
    },
});