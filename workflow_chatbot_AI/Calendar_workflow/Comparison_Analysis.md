# So sánh Workflow: SQL Raw vs Odoo Node

## Kiến trúc Workflow

### Workflow Cũ (SQL Raw)

```
Input Query
    ↓
AI Agent (Generate SQL)
    ↓
Code (Timezone Conversion)
    ↓
PostgreSQL (Execute Raw SQL)
    ↓
Result
```

### Workflow Mới (Odoo Node)

```
Input Query
    ↓
AI Agent (Extract JSON Data)
    ↓
Code (Process & Convert)
    ↓
Odoo Node (Create via API)
    ↓
Format Response
    ↓
Structured Result
```

## Chi tiết từng bước

| Aspect              | SQL Raw Approach        | Odoo Node Approach     |
| ------------------- | ----------------------- | ---------------------- |
| **AI Output**       | SQL INSERT query string | Structured JSON object |
| **Data Processing** | String manipulation     | Object manipulation    |
| **Database Access** | Direct SQL execution    | Odoo ORM API           |
| **Validation**      | Manual/None             | Automatic via Odoo     |
| **Error Handling**  | SQL errors              | Odoo API errors        |
| **Security**        | SQL injection risk      | API authentication     |
| **Maintainability** | Hard to maintain        | Easy to maintain       |

## Code Examples

### AI Agent System Message

#### Cũ (SQL Generator):

```
You are a PostgreSQL SQL query generator for Odoo's calendar_event table.
Only generate valid SQL INSERT queries to create new events.
Target table: "calendar_event"
Always use double quotes for table and column names.
```

#### Mới (Data Extractor):

```
You are an AI assistant that extracts calendar event information from user requests.
Extract and structure calendar event data from natural language requests to create JSON objects.
Always return a valid JSON object with the required fields.
```

### Processing Node

#### Cũ (String Manipulation):

```javascript
// Regex để tìm và extract thời gian trong format 'YYYY-MM-DD HH:MM:SS'
const timeRegex = /'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'/g;
const updatedQuery = sqlQuery.replace(timeRegex, (match, timeString) => {
  const utcTime = convertToUTC(timeString);
  return `'${utcTime}'`;
});
```

#### Mới (Object Processing):

```javascript
// Parse JSON từ AI output
const eventData = JSON.parse($input.first().json.output);
// Convert start và stop time về UTC
if (eventData.start) {
  eventData.start = convertToUTC(eventData.start);
}
if (eventData.stop) {
  eventData.stop = convertToUTC(eventData.stop);
}
```

### Database Interaction

#### Cũ (Raw SQL):

```sql
INSERT INTO "calendar_event" (
  "name", "start", "stop", "duration", "active", "user_id", "privacy", "show_as"
) VALUES (
  'Họp nhóm', '2025-07-01 02:00:00', '2025-07-01 03:00:00', 1, true, 1, 'public', 'busy'
);
```

#### Mới (Odoo API):

```json
{
  "resource": "custom",
  "operation": "create",
  "customResource": "calendar.event",
  "fieldsUi": {
    "fieldValues": [
      { "fieldId": "name", "fieldValue": "={{ $json.name }}" },
      { "fieldId": "start", "fieldValue": "={{ $json.start }}" },
      { "fieldId": "stop", "fieldValue": "={{ $json.stop }}" }
    ]
  }
}
```

## Ưu nhược điểm

### SQL Raw Approach

#### Ưu điểm:

- ✅ Thực thi nhanh
- ✅ Ít dependency
- ✅ Đơn giản, trực tiếp

#### Nhược điểm:

- ❌ Risk SQL injection
- ❌ Không có validation
- ❌ Không trigger business logic
- ❌ Khó maintain khi schema thay đổi
- ❌ Không có audit trail
- ❌ Không respect Odoo permissions

### Odoo Node Approach

#### Ưu điểm:

- ✅ An toàn, không có SQL injection
- ✅ Automatic validation
- ✅ Trigger đầy đủ business logic
- ✅ Respect Odoo permissions
- ✅ Audit trail tự động
- ✅ Dễ maintain
- ✅ Support complex operations
- ✅ Consistent với Odoo ecosystem

#### Nhược điểm:

- ❌ Chậm hơn một chút (API overhead)
- ❌ Phụ thuộc vào Odoo API
- ❌ Cần setup credentials

## Kết luận

### Khuyến nghị:

**Nên chuyển sang Odoo Node approach** vì:

1. **Bảo mật tốt hơn**: Không có risk SQL injection
2. **Tích hợp chặt chẽ**: Sử dụng đúng Odoo ecosystem
3. **Maintainability**: Dễ duy trì và mở rộng
4. **Data integrity**: Validation và business logic đầy đủ
5. **Future-proof**: Không bị ảnh hưởng khi schema thay đổi

### Khi nào dùng SQL Raw:

- Chỉ trong trường hợp đặc biệt cần performance cao
- Bulk operations với lượng data lớn
- Data migration tasks
- Reporting queries phức tạp

### Best Practices:

1. Sử dụng Odoo Node cho CRUD operations
2. Implement proper error handling
3. Log all operations cho debugging
4. Test thoroughly với different scenarios
5. Monitor performance và optimize nếu cần
