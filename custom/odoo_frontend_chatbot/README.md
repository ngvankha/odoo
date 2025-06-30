# Odoo Frontend Chatbot

Module tạo chatbot floating trong giao diện frontend của Odoo 16, tương tự như im_livechat nhưng dành cho người dùng nội bộ và tích hợp với OdooBot.

## Tính năng

- 🤖 Floating chatbot button ở góc màn hình
- 💬 Cửa sổ chat hiện đại với UI đẹp mắt
- 🔗 Tích hợp với OdooBot có sẵn trong Odoo
- 🧠 Hỗ trợ AI bot (nếu có module ai_bot)
- 📱 Responsive design cho mobile
- ⚙️ Cấu hình linh hoạt qua Settings
- 🎨 Giao diện giống im_livechat

## Cài đặt

1. **Copy module vào thư mục addons/custom:**
   ```bash
   cp -r odoo_frontend_chatbot /path/to/odoo/custom/
   ```

2. **Cập nhật danh sách modules:**
   - Vào Apps → Update Apps List

3. **Cài đặt module:**
   - Tìm "Odoo Frontend Chatbot" và click Install

## Cấu hình

1. **Vào Settings → Technical → Frontend Chatbot:**
   - ✅ Enable Frontend Chatbot
   - 📝 Đặt Welcome Message 
   - 📍 Chọn vị trí hiển thị (bottom-right, bottom-left, top-right, top-left)

2. **Lưu cấu hình**

## Sử dụng

1. **Sau khi cấu hình, reload trang**
2. **Sẽ thấy nút chat floating** 💬
3. **Click để mở cửa sổ chat**
4. **Nhập tin nhắn và Enter để gửi**
5. **OdooBot sẽ trả lời tự động**

## Tích hợp với AI Bot

Nếu bạn có module `ai_bot`, chatbot sẽ tự động sử dụng AI để trả lời thông minh hơn thay vì chỉ dùng OdooBot thông thường.

## Cấu trúc Module

```
odoo_frontend_chatbot/
├── __manifest__.py
├── controllers/
│   └── main.py              # API endpoints
├── models/
│   └── res_config_settings.py
├── static/src/
│   ├── scss/chatbot.scss    # Styles
│   ├── js/
│   │   ├── services/chatbot_service.js
│   │   ├── components/
│   │   │   ├── chatbot_button.js
│   │   │   └── chatbot_window.js
│   │   └── main.js
│   └── xml/chatbot_templates.xml
├── views/
│   └── res_config_settings_views.xml
└── data/
    └── ir_config_parameter_data.xml
```

## API Endpoints

- `GET /frontend_chatbot/config` - Lấy cấu hình chatbot
- `POST /frontend_chatbot/create_channel` - Tạo/lấy channel chat
- `POST /frontend_chatbot/send_message` - Gửi tin nhắn
- `POST /frontend_chatbot/get_messages` - Lấy tin nhắn mới

## Tùy chỉnh

### Thay đổi màu sắc
Sửa file `static/src/scss/chatbot.scss`:
```scss
.o_frontend_chatbot_button {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

### Thay đổi vị trí mặc định
Sửa file `data/ir_config_parameter_data.xml`:
```xml
<field name="value">bottom-left</field> <!-- thay vì bottom-right -->
```

## Xử lý lỗi

### Nếu chatbot không hiển thị:
1. Kiểm tra module đã cài đặt thành công
2. Kiểm tra cấu hình trong Settings
3. Kiểm tra console browser có lỗi JavaScript không
4. Restart Odoo server và clear cache

### Nếu tin nhắn không gửi được:
1. Kiểm tra user có quyền truy cập mail.channel không
2. Kiểm tra log server có lỗi không
3. Kiểm tra kết nối database

## Tương thích

- ✅ Odoo 16.0
- ✅ Tích hợp với mail_bot
- ✅ Tích hợp với ai_bot (optional)
- ✅ Responsive design
- ✅ Multi-language support

## Giấy phép

LGPL-3

## Hỗ trợ

Nếu có vấn đề, vui lòng tạo issue hoặc liên hệ developer.

---

**Lưu ý**: Module này được thiết kế để hoạt động độc lập và không ảnh hưởng đến các chức năng khác của Odoo.
