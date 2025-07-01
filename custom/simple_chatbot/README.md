# Simple Chatbot Module with n8n Integration

Module chatbot đơn giản tích hợp với n8n để hiển thị trong giao diện backend Odoo 16.

## Tính năng

- Hiển thị nút chatbot trong systray (thanh công cụ phía trên)
- Cửa sổ chatbot với giao diện đẹp mắt
- **Tích hợp n8n webhook** để xử lý tin nhắn AI
- Phản hồi thời gian thực từ n8n
- Hiển thị trạng thái loading và lỗi
- Timestamp cho mỗi tin nhắn
- Làm mới cấu hình động
- Giao diện responsive, thân thiện với mobile

## Cài đặt

1. Copy thư mục `simple_chatbot` vào `custom/` hoặc `addons/`
2. Khởi động lại Odoo server
3. Vào Apps, tìm "Simple Chatbot" và cài đặt
4. **Cấu hình n8n webhook**:
   - Vào menu "Simple Chatbot" → "Configuration"
   - Tạo cấu hình mới
   - Nhập URL webhook n8n của bạn
   - Đánh dấu "Active"

## Cấu hình n8n

### 1. Tạo workflow n8n
```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "chatbot",
        "responseMode": "responseNode"
      }
    },
    {
      "name": "Process Message",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Xử lý tin nhắn từ Odoo\nconst userMessage = items[0].json.message;\nconst userName = items[0].json.user_name;\n\n// Logic xử lý tin nhắn của bạn ở đây\nlet response = `Xin chào ${userName}! Bạn vừa nói: \"${userMessage}\"`;\n\n// Có thể tích hợp với OpenAI, ChatGPT, hoặc AI khác\n// const aiResponse = await callAI(userMessage);\n\nreturn [{\n  json: {\n    message: response,\n    user_id: items[0].json.user_id,\n    timestamp: new Date().toISOString()\n  }\n}];"
      }
    },
    {
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ JSON.stringify({message: $json.message}) }}"
      }
    }
  ]
}
```

### 2. Dữ liệu gửi từ Odoo
```json
{
  "message": "Tin nhắn của người dùng",
  "user_id": 1,
  "user_name": "Admin",
  "timestamp": "2024-07-01T10:00:00Z",
  "context": {}
}
```

### 3. Format phản hồi mong đợi
```json
{
  "message": "Phản hồi từ AI/n8n",
  "data": {
    "additional_info": "Thông tin thêm nếu có"
  }
}
```

## Sử dụng

- Click vào nút "Chatbot" trong systray để mở/đóng cửa sổ chat
- Nhập tin nhắn và nhấn Enter hoặc click nút gửi
- Bot sẽ gửi tin nhắn đến n8n và hiển thị phản hồi
- Click nút sync để làm mới cấu hình
- Click nút refresh để xóa cuộc trò chuyện
- Click nút X để đóng cửa sổ chat

## API Endpoints

- `POST /simple_chatbot/send_message`: Gửi tin nhắn đến n8n
- `POST /simple_chatbot/get_config`: Lấy thông tin cấu hình

## Troubleshooting

### Chatbot không phản hồi
1. Kiểm tra webhook URL trong cấu hình
2. Đảm bảo n8n workflow đang chạy
3. Kiểm tra log Odoo để xem lỗi chi tiết

### Hiển thị "Chưa cấu hình"
1. Vào menu "Simple Chatbot" → "Configuration"
2. Tạo hoặc cập nhật cấu hình với webhook URL hợp lệ
3. Click nút sync trong chatbot để làm mới

## Kỹ thuật

- Sử dụng OWL Framework của Odoo 16
- Component được đăng ký như systray item
- Model `simple.chatbot.config` để lưu cấu hình
- Controller xử lý API calls
- CSS tùy chỉnh cho giao diện đẹp
- Tích hợp requests library để gọi n8n webhook
