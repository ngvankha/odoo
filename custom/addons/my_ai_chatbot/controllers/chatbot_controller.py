from odoo import http
from odoo.http import request
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

class ChatbotController(http.Controller):
    # Khởi tạo client và service cho chatbot
    openAIClient = AsyncOpenAI(
        api_key="-lm-studio-",
        base_url="http://localhost:1234/v1",
        default_headers={'Connection': 'close'}
    )

    service = OpenAIChatCompletion(
        ai_model_id="vistral-7b-chat-dpo",
        service_id="unique_service_id",  # Đặt ID dịch vụ của bạn
        async_client=openAIClient
    )

    @http.route('/chatbot/api', type='json', auth='public', methods=['POST'])
    def chatbot_api(self, **kwargs):
        question = kwargs.get('question')
        if not question:
            return {'error': 'Question is required'}
        
        try:
            # Gửi câu hỏi đến API chatbot
            response = self.service.complete_chat(
                messages=[{"role": "user", "content": question}]
            )
            if response and 'choices' in response:
                return {'response': response['choices'][0]['message']['content']}
            else:
                return {'error': 'No response from the AI model'}
        except Exception as e:
            return {'error': str(e)}