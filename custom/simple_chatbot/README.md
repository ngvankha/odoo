# Simple Chatbot Module

Module đơn giản hiển thị chatbot trong giao diện backend Odoo 16.

## Tính năng

- Hiển thị nút chatbot trong systray (thanh công cụ phía trên)
- Cửa sổ chatbot với giao diện giống im_livechat
- Phản hồi tự động từ bot
- Có thể xóa cuộc trò chuyện và bắt đầu lại
- Giao diện responsive, thân thiện với mobile

## Cài đặt

1. Copy thư mục `simple_chatbot` vào `custom/` hoặc `addons/`
2. Khởi động lại Odoo server
3. Vào Apps, tìm "Simple Chatbot" và cài đặt
4. Chatbot sẽ xuất hiện trong thanh systray ở góc trên bên phải

## Sử dụng

- Click vào nút "Chatbot" trong systray để mở/đóng cửa sổ chat
- Nhập tin nhắn và nhấn Enter hoặc click nút gửi
- Bot sẽ tự động phản hồi
- Click nút refresh để xóa cuộc trò chuyện
- Click nút X để đóng cửa sổ chat

## Kỹ thuật

- Sử dụng OWL Framework của Odoo 16
- Component được đăng ký như systray item
- CSS tùy chỉnh cho giao diện đẹp
- Không cần database models, chỉ frontend thuần
