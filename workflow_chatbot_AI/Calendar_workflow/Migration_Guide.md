# Hướng dẫn Migration từ SQL Raw sang Odoo Node

## Tổng quan thay đổi

### Workflow cũ (SQL Raw):

1. **AI Agent** → Generate SQL INSERT query
2. **Code Node** → Convert timezone UTC+7 to UTC
3. **PostgreSQL Node** → Execute raw SQL

### Workflow mới (Odoo Node):

1. **AI Agent** → Extract event data thành JSON object
2. **Code Node** → Process và convert timezone
3. **Odoo Node** → Create record thông qua Odoo API
4. **Format Response** → Format response cho user

## Chi tiết các thay đổi

### 1. AI Agent System Message

**Cũ:** Generate SQL INSERT queries

```
"You are a PostgreSQL SQL query generator for Odoo's calendar_event table."
```

**Mới:** Extract structured data

```
"You are an AI assistant that extracts calendar event information from user requests."
```

### 2. Node thay thế PostgreSQL

**Cũ:** PostgreSQL Node với raw SQL

```json
{
  "type": "n8n-nodes-base.postgres",
  "parameters": {
    "operation": "executeQuery",
    "query": "{{ $json.output }}"
  }
}
```

**Mới:** Odoo Node với structured data

```json
{
  "type": "n8n-nodes-base.odoo",
  "parameters": {
    "resource": "custom",
    "operation": "create",
    "customResource": "calendar.event",
    "fieldsUi": {
      "fieldValues": [
        {
          "fieldId": "name",
          "fieldValue": "={{ $json.name }}"
        }
        // ... other fields
      ]
    }
  }
}
```

### 3. Xử lý dữ liệu

**Cũ:** Regex replace trong SQL string
**Mới:** Parse JSON và xử lý từng field

## Ưu điểm của Odoo Node

### 1. **Tích hợp tốt hơn**

- Sử dụng Odoo ORM thay vì raw SQL
- Tự động validate dữ liệu
- Trigger các workflow và business logic của Odoo

### 2. **Bảo mật cao hơn**

- Không có SQL injection risk
- Sử dụng Odoo permission system
- Audit trail tự động

### 3. **Dễ maintain**

- Không cần biết database schema
- Tự động handle field changes
- Error handling tốt hơn

### 4. **Flexible hơn**

- Có thể set computed fields
- Trigger related actions (email, notifications)
- Support complex data types

## Cách setup Odoo Node

### 1. Tạo Odoo API Credential

```
Host: http://your-odoo-server:8069
Database: your_database_name
Username: your_username
Password: your_password (hoặc API key)
```

### 2. Configure Odoo Node

- **Resource**: custom
- **Operation**: create
- **Custom Resource**: calendar.event
- **Fields**: Map từ JSON data

### 3. Test workflow

```json
{
  "query": "Tạo sự kiện Họp nhóm vào ngày mai lúc 9h sáng"
}
```

## Migration Steps

### Bước 1: Backup workflow cũ

- Export workflow hiện tại
- Save as `Insert_Calendar_workflow_backup.json`

### Bước 2: Import workflow mới

- Import `Insert_Calendar_workflow_v2.json`
- Configure Odoo credentials

### Bước 3: Test và verify

- Test với các case cơ bản
- Verify data được tạo đúng trong Odoo
- Check timezone conversion

### Bước 4: Update calling workflows

- Update các workflow khác gọi đến workflow này
- Verify response format compatibility

## Troubleshooting

### 1. Credential issues

```
Error: "Authentication failed"
```

**Solution**: Check Odoo credentials, ensure API access enabled

### 2. Field mapping issues

```
Error: "Field 'xyz' does not exist"
```

**Solution**: Check field names in Odoo model, update fieldsUi

### 3. Timezone issues

```
Error: Wrong time created
```

**Solution**: Verify timezone conversion in Process Event Data node

### 4. Permission issues

```
Error: "Access denied"
```

**Solution**: Check user permissions for calendar.event model

## Code Examples

### Test input data:

```json
{
  "query": "Tạo cuộc họp Design Review vào thứ 2 tuần sau từ 14:00 đến 16:00 tại phòng họp A"
}
```

### Expected output:

```json
{
  "success": true,
  "message": "Đã tạo thành công sự kiện: Design Review",
  "event_id": 123,
  "event_data": {
    "name": "Design Review",
    "start": "2025-07-07 07:00:00",
    "stop": "2025-07-07 09:00:00",
    "duration": 2.0,
    "location": "phòng họp A",
    "description": ""
  }
}
```
