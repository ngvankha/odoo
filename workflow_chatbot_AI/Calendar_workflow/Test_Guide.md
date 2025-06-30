# Test Script for Odoo Calendar Workflow

## Test Cases

### 1. Basic Event Creation

```json
{
  "query": "Tạo sự kiện Họp nhóm vào ngày mai lúc 9h sáng"
}
```

Expected Result:

- Event name: "Họp nhóm"
- Start: Tomorrow 9:00 AM (UTC)
- Duration: 1 hour
- Privacy: public
- Show as: busy

### 2. Event with Time Range

```json
{
  "query": "Tạo event Demo từ 2025-07-01 08:00 đến 2025-07-01 09:30"
}
```

Expected Result:

- Event name: "Demo"
- Start: 2025-07-01 01:00:00 (UTC, converted from UTC+7)
- Stop: 2025-07-01 02:30:00 (UTC)
- Duration: 1.5 hours

### 3. Event with Location

```json
{
  "query": "Tạo cuộc họp Design Review vào thứ 2 tuần sau từ 14:00 đến 16:00 tại phòng họp A"
}
```

Expected Result:

- Event name: "Design Review"
- Location: "phòng họp A"
- Duration: 2 hours

### 4. All-day Event

```json
{
  "query": "Tạo sự kiện Conference cả ngày vào 15/07/2025"
}
```

Expected Result:

- Event name: "Conference"
- All day: true
- Start: 2025-07-15 00:00:00
- Stop: 2025-07-15 23:59:59

## Test Commands

### Using cURL to test workflow:

```bash
curl -X POST http://your-n8n-server/webhook/test-calendar \
  -H "Content-Type: application/json" \
  -d '{"query": "Tạo sự kiện Họp nhóm vào ngày mai lúc 9h sáng"}'
```

### Expected Response Format:

```json
{
  "success": true,
  "message": "Đã tạo thành công sự kiện: Họp nhóm",
  "event_id": 123,
  "event_data": {
    "name": "Họp nhóm",
    "start": "2025-07-01 02:00:00",
    "stop": "2025-07-01 03:00:00",
    "duration": 1.0,
    "location": "",
    "description": ""
  }
}
```

## Verification Steps

1. **Check in Odoo Calendar**

   - Login to Odoo
   - Go to Calendar app
   - Verify event exists with correct data

2. **Check Database** (optional)

   ```sql
   SELECT name, start, stop, duration, user_id, privacy, show_as
   FROM calendar_event
   ORDER BY create_date DESC
   LIMIT 5;
   ```

3. **Check Logs**
   - Check n8n execution logs
   - Verify no errors in Odoo logs

## Performance Comparison

### Old Workflow (SQL):

- ✅ Fast execution
- ❌ SQL injection risk
- ❌ No business logic triggers
- ❌ No validation

### New Workflow (Odoo Node):

- ✅ Safe and secure
- ✅ Full Odoo integration
- ✅ Automatic validation
- ✅ Business logic support
- ⚠️ Slightly slower (API overhead)

## Common Issues & Solutions

### Issue 1: Timezone mismatch

**Problem**: Events created with wrong time
**Solution**: Verify timezone conversion in "Process Event Data" node

### Issue 2: Missing required fields

**Problem**: Odoo validation error
**Solution**: Ensure all NOT NULL fields are provided in AI response

### Issue 3: Authentication errors

**Problem**: Cannot connect to Odoo
**Solution**: Check API credentials and user permissions

### Issue 4: AI parsing errors

**Problem**: AI cannot extract event data
**Solution**: Improve system message prompts or add more examples
