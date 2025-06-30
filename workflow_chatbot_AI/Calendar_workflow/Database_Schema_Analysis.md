# Phân tích Database Schema cho Calendar Event trong Odoo

## Tổng quan

Khi tạo một cuộc họp mới trên frontend Odoo, hệ thống sẽ tương tác với các bảng chính sau:

## 1. Bảng chính: `calendar_event`

### 🔑 Thông tin cơ bản

- **Model**: `calendar.event`
- **Mô tả**: Bảng chính lưu trữ thông tin sự kiện/cuộc họp
- **Order**: `start desc`

### 📋 Fields bắt buộc (NOT NULL)

```python
# Thông tin cơ bản
name = fields.Char('Meeting Subject', required=True)  # Tên cuộc họp
start = fields.Datetime('Start', required=True)       # Thời gian bắt đầu
stop = fields.Datetime('Stop', required=True)         # Thời gian kết thúc
privacy = fields.Selection(required=True)             # Chế độ riêng tư
show_as = fields.Selection(required=True)             # Hiển thị là bận/rảnh
active = fields.Boolean(default=True)                 # Trạng thái hoạt động
```

### 📋 Fields quan trọng khác

```python
# Người tổ chức
user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
partner_id = fields.Many2one('res.partner', related='user_id.partner_id')

# Thông tin chi tiết
description = fields.Html('Description')              # Mô tả
location = fields.Char('Location')                   # Địa điểm
videocall_location = fields.Char('Meeting URL')      # Link họp online

# Thời gian
allday = fields.Boolean('All Day', default=False)    # Sự kiện cả ngày
duration = fields.Float('Duration')                  # Thời lượng (giờ)
start_date = fields.Date('Start Date')               # Ngày bắt đầu
stop_date = fields.Date('End Date')                  # Ngày kết thúc

# Phân loại
categ_ids = fields.Many2many('calendar.event.type')  # Danh mục sự kiện

# Token và bảo mật
access_token = fields.Char('Invitation Token')       # Token mời tham gia
```

### 🎨 Giá trị Selection Fields

```python
# Privacy options
privacy = [
    ('public', 'Public'),
    ('private', 'Private'),
    ('confidential', 'Only internal users')
]

# Show as options
show_as = [
    ('free', 'Available'),
    ('busy', 'Busy')
]
```

## 2. Bảng người tham dự: `calendar_attendee`

### 🔑 Thông tin cơ bản

- **Model**: `calendar.attendee`
- **Mô tả**: Lưu trữ thông tin người tham dự cuộc họp
- **Relation**: Many2one với `calendar_event`

### 📋 Fields chính

```python
# Liên kết
event_id = fields.Many2one('calendar.event', required=True, ondelete='cascade')
partner_id = fields.Many2one('res.partner', required=True)

# Thông tin liên lạc
email = fields.Char(related='partner_id.email')
phone = fields.Char(related='partner_id.phone')
common_name = fields.Char('Common name')

# Trạng thái tham dự
state = fields.Selection([
    ('needsAction', 'Needs Action'),
    ('tentative', 'Uncertain'),
    ('declined', 'Declined'),
    ('accepted', 'Accepted')
], default='needsAction')

# Bảo mật
access_token = fields.Char('Invitation Token')
```

## 3. Bảng nhắc nhở: `calendar_alarm`

### 🔑 Thông tin cơ bản

- **Model**: `calendar.alarm`
- **Relation**: Many2many với `calendar_event`

### 📋 Fields chính

```python
name = fields.Char('Name', required=True)
alarm_type = fields.Selection([
    ('notification', 'Notification'),
    ('email', 'Email')
])
duration = fields.Integer('Remind Before')
interval = fields.Selection([
    ('minutes', 'Minutes'),
    ('hours', 'Hours'),
    ('days', 'Days')
])
```

## 4. Bảng phân loại: `calendar_event_type`

### 🔑 Thông tin cơ bản

- **Model**: `calendar.event.type`
- **Relation**: Many2many với `calendar_event`

### 📋 Fields chính

```python
name = fields.Char('Name', required=True)
color = fields.Integer('Color')
```

## 5. Bảng lặp lại: `calendar_recurrence`

### 🔑 Thông tin cơ bản

- **Model**: `calendar.recurrence`
- **Mô tả**: Quản lý quy tắc lặp lại sự kiện

### 📋 Fields chính

```python
rrule_type = fields.Selection([
    ('daily', 'Days'),
    ('weekly', 'Weeks'),
    ('monthly', 'Months'),
    ('yearly', 'Years')
])
interval = fields.Integer('Repeat Every')
count = fields.Integer('Repeat')
until = fields.Date('Until')
```

## 📊 Relationship Diagram

```
calendar_event (1) -------- (M) calendar_attendee
      |                              |
      |                              |
      | (M)                          | (M)
      |                              |
calendar_alarm                 res_partner
      |
      |
calendar_event_type (M) ---- (M) calendar_event
      |
      |
calendar_recurrence (1) ---- (M) calendar_event
```

## 🛠️ SQL Insert Commands

### 1. Tạo sự kiện cơ bản

```sql
INSERT INTO calendar_event (
    name, start, stop, user_id, privacy, show_as, active, duration,
    create_date, write_date, create_uid, write_uid
) VALUES (
    'Cuộc họp mới',                    -- name
    '2025-07-01 02:00:00',            -- start (UTC)
    '2025-07-01 03:00:00',            -- stop (UTC)
    1,                                 -- user_id
    'public',                          -- privacy
    'busy',                            -- show_as
    true,                              -- active
    1.0,                               -- duration (hours)
    NOW(),                             -- create_date
    NOW(),                             -- write_date
    1,                                 -- create_uid
    1                                  -- write_uid
);
```

### 2. Thêm người tham dự

```sql
INSERT INTO calendar_attendee (
    event_id, partner_id, state, access_token,
    create_date, write_date, create_uid, write_uid
) VALUES (
    [EVENT_ID],                        -- event_id (từ query trên)
    [PARTNER_ID],                      -- partner_id
    'needsAction',                     -- state
    '[RANDOM_TOKEN]',                  -- access_token
    NOW(),                             -- create_date
    NOW(),                             -- write_date
    1,                                 -- create_uid
    1                                  -- write_uid
);
```

### 3. Liên kết với phân loại (optional)

```sql
INSERT INTO meeting_category_rel (event_id, type_id)
VALUES ([EVENT_ID], [CATEGORY_ID]);
```

### 4. Thêm nhắc nhở (optional)

```sql
INSERT INTO calendar_alarm_calendar_event_rel (calendar_event_id, calendar_alarm_id)
VALUES ([EVENT_ID], [ALARM_ID]);
```

## 🔧 Odoo API Create Examples

### 1. Tạo sự kiện đơn giản

```python
event_data = {
    'name': 'Cuộc họp mới',
    'start': '2025-07-01 09:00:00',
    'stop': '2025-07-01 10:00:00',
    'user_id': 1,
    'privacy': 'public',
    'show_as': 'busy',
    'active': True,
    'duration': 1.0,
    'location': 'Phòng họp A',
    'description': '<p>Nội dung cuộc họp</p>'
}
```

### 2. Tạo sự kiện với người tham dự

```python
event_data = {
    'name': 'Cuộc họp với khách hàng',
    'start': '2025-07-01 14:00:00',
    'stop': '2025-07-01 16:00:00',
    'user_id': 1,
    'privacy': 'public',
    'show_as': 'busy',
    'active': True,
    'partner_ids': [(6, 0, [partner_id_1, partner_id_2])],  # Attendees
    'location': 'Phòng họp B',
    'categ_ids': [(6, 0, [category_id])],                   # Categories
    'alarm_ids': [(6, 0, [alarm_id])]                       # Reminders
}
```

### 3. Tạo sự kiện lặp lại

```python
event_data = {
    'name': 'Họp tuần',
    'start': '2025-07-01 09:00:00',
    'stop': '2025-07-01 10:00:00',
    'user_id': 1,
    'privacy': 'public',
    'show_as': 'busy',
    'recurrency': True,
    'rrule_type': 'weekly',
    'interval': 1,
    'count': 10,  # Lặp 10 lần
    'mon': True,  # Thứ 2 hàng tuần
}
```

## 🎯 Các trường hợp sử dụng thực tế

### 1. Meeting đơn giản (1 giờ)

```json
{
  "name": "Daily Standup",
  "start": "2025-07-01 02:00:00", // 9:00 UTC+7 -> 2:00 UTC
  "stop": "2025-07-01 02:30:00", // 9:30 UTC+7 -> 2:30 UTC
  "duration": 0.5,
  "user_id": 1,
  "privacy": "public",
  "show_as": "busy",
  "active": true
}
```

### 2. Meeting với location và description

```json
{
  "name": "Client Meeting",
  "start": "2025-07-01 07:00:00", // 14:00 UTC+7 -> 7:00 UTC
  "stop": "2025-07-01 09:00:00", // 16:00 UTC+7 -> 9:00 UTC
  "duration": 2.0,
  "location": "Conference Room A",
  "description": "<p>Discuss project requirements</p>",
  "user_id": 1,
  "privacy": "private",
  "show_as": "busy",
  "active": true
}
```

### 3. All-day event

```json
{
  "name": "Company Training",
  "start": "2025-07-01 00:00:00",
  "stop": "2025-07-01 23:59:59",
  "allday": true,
  "user_id": 1,
  "privacy": "public",
  "show_as": "busy",
  "active": true
}
```

## ⚠️ Lưu ý quan trọng

### 1. Timezone Conversion

- Frontend Odoo hiển thị theo timezone của user (VD: UTC+7)
- Database lưu trữ theo UTC
- Cần convert: `UTC+7 time - 7 hours = UTC time`

### 2. Required Fields

- `name`: Bắt buộc có
- `start`, `stop`: Bắt buộc và `stop` phải > `start`
- `privacy`: Default 'public'
- `show_as`: Default 'busy'
- `active`: Default true
- `user_id`: Default current user

### 3. Relations

- Khi tạo event, Odoo tự động tạo attendee cho organizer
- `partner_ids` sẽ tự động tạo records trong `calendar_attendee`
- Token được tự động generate cho mỗi attendee

### 4. Business Logic

- Organizer mặc định có state = 'accepted'
- Other attendees mặc định có state = 'needsAction'
- Event được tự động subscribe tới organizer
- Mail notification được gửi tự động (nếu configured)

## 🔍 Debug Query

### Xem event vừa tạo

```sql
SELECT
    id, name, start, stop, duration, privacy, show_as, user_id, active,
    create_date, write_date
FROM calendar_event
WHERE create_date >= NOW() - INTERVAL '1 hour'
ORDER BY create_date DESC;
```

### Xem attendees của event

```sql
SELECT
    ca.id, ca.event_id, ca.partner_id, rp.name as partner_name,
    ca.state, ca.email, ca.access_token
FROM calendar_attendee ca
JOIN res_partner rp ON ca.partner_id = rp.id
WHERE ca.event_id = [EVENT_ID];
```
