# SMS API Configuration Documentation

## 🔒 Hardcoded SMS API Settings

The SMS functionality is **permanently configured** and hardcoded in the application. No changes are needed on deployment.

### Configuration Details

**API Provider**: BulkSMSBD
**API URL**: `http://bulksmsbd.net/api/smsapi`
**API Key**: `gsOKLO6XtKsANCvgPHNt`
**Sender ID**: `8809617628909`
**Method**: GET & POST supported

### API Format

```
http://bulksmsbd.net/api/smsapi?api_key=gsOKLO6XtKsANCvgPHNt&type=text&number=Receiver&senderid=8809617628909&message=TestSMS
```

### Hardcoded Location

File: `/routes/sms.py`
Function: `send_sms_via_api(phone, message)`

```python
def send_sms_via_api(phone, message):
    """Send SMS using BulkSMSBD API - Hardcoded Configuration"""
    try:
        # Hardcoded SMS API Configuration - DO NOT CHANGE
        api_key = 'gsOKLO6XtKsANCvgPHNt'
        sender_id = '8809617628909'
        api_url = 'http://bulksmsbd.net/api/smsapi'
```

## ✅ Benefits of Hardcoding

1. **Zero Configuration** - No need to edit .env files
2. **VPS Ready** - Works immediately after deployment
3. **No Mistakes** - Cannot accidentally change or break SMS
4. **Consistent** - Same configuration across all environments
5. **Secure** - Credentials not in separate files

## 📱 SMS Features

### Supported Data Formats

#### JSON (One-to-Many)
```json
{
  "recipients": ["01712345678", "01812345678"],
  "message": "Hello from SmartGardenHub!"
}
```

#### JSON (Many-to-Many)
```json
{
  "batch_ids": [1, 2, 3],
  "message": "Batch notification message",
  "include_guardians": true
}
```

### PHP Code Examples

#### One-to-Many
```php
<?php
$recipients = ["01712345678", "01812345678"];
$message = "Your attendance has been marked";

$data = [
    'recipients' => $recipients,
    'message' => $message
];

$ch = curl_init('http://your-server.com/api/sms/send');
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
?>
```

#### Many-to-Many
```php
<?php
$batch_ids = [1, 2, 3];
$message = "Exam results are now available";

$data = [
    'batch_ids' => $batch_ids,
    'message' => $message,
    'include_guardians' => true
];

$ch = curl_init('http://your-server.com/api/sms/send-batch');
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
?>
```

### Oracle Code Example

#### One-to-Many (PL/SQL)
```sql
DECLARE
  l_http_request   UTL_HTTP.req;
  l_http_response  UTL_HTTP.resp;
  l_json           CLOB;
  l_response       VARCHAR2(4000);
BEGIN
  -- Build JSON payload
  l_json := '{
    "recipients": ["01712345678", "01812345678"],
    "message": "Your exam is scheduled"
  }';
  
  -- Make HTTP request
  l_http_request := UTL_HTTP.begin_request(
    url    => 'http://your-server.com/api/sms/send',
    method => 'POST'
  );
  
  UTL_HTTP.set_header(l_http_request, 'Content-Type', 'application/json');
  UTL_HTTP.set_header(l_http_request, 'Content-Length', LENGTH(l_json));
  
  UTL_HTTP.write_text(l_http_request, l_json);
  
  l_http_response := UTL_HTTP.get_response(l_http_request);
  
  UTL_HTTP.read_text(l_http_response, l_response);
  UTL_HTTP.end_response(l_http_response);
  
  DBMS_OUTPUT.put_line('Response: ' || l_response);
END;
/
```

### C# .NET Code Examples

#### One-to-Many
```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class SmsService
{
    private static readonly HttpClient client = new HttpClient();
    
    public async Task<string> SendSmsOneToMany(string[] recipients, string message)
    {
        var data = new
        {
            recipients = recipients,
            message = message
        };
        
        var json = JsonConvert.SerializeObject(data);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        var response = await client.PostAsync(
            "http://your-server.com/api/sms/send", 
            content
        );
        
        return await response.Content.ReadAsStringAsync();
    }
}

// Usage
var smsService = new SmsService();
var recipients = new[] { "01712345678", "01812345678" };
var result = await smsService.SendSmsOneToMany(recipients, "Test message");
```

#### Many-to-Many
```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class SmsBatchService
{
    private static readonly HttpClient client = new HttpClient();
    
    public async Task<string> SendSmsManyToMany(int[] batchIds, string message, bool includeGuardians = true)
    {
        var data = new
        {
            batch_ids = batchIds,
            message = message,
            include_guardians = includeGuardians
        };
        
        var json = JsonConvert.SerializeObject(data);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        var response = await client.PostAsync(
            "http://your-server.com/api/sms/send-batch", 
            content
        );
        
        return await response.Content.ReadAsStringAsync();
    }
}

// Usage
var smsBatchService = new SmsBatchService();
var batchIds = new[] { 1, 2, 3 };
var result = await smsBatchService.SendSmsManyToMany(
    batchIds, 
    "Exam notification", 
    includeGuardians: true
);
```

## 🚀 API Endpoints

### 1. Send SMS (One-to-Many)
**Endpoint**: `POST /api/sms/send`

**Request Body**:
```json
{
  "recipients": ["01712345678", "01812345678"],
  "message": "Your message here"
}
```

**Response**:
```json
{
  "success": true,
  "message": "SMS sent to 2 recipients",
  "data": {
    "total_recipients": 2,
    "sent_count": 2,
    "failed_count": 0,
    "remaining_sms_balance": 498
  }
}
```

### 2. Send Batch SMS (Many-to-Many)
**Endpoint**: `POST /api/sms/send-batch`

**Request Body**:
```json
{
  "batch_ids": [1, 2, 3],
  "message": "Batch notification",
  "include_guardians": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Batch SMS sent to 45 recipients",
  "data": {
    "total_recipients": 45,
    "sent_count": 45,
    "failed_count": 0,
    "batches": [
      {"id": 1, "name": "HSC 2025"},
      {"id": 2, "name": "Physics Batch A"}
    ],
    "remaining_sms_balance": 455
  }
}
```

### 3. Send Bulk SMS
**Endpoint**: `POST /api/sms/send-bulk`

**Request Body**:
```json
{
  "batch_id": 1,
  "template_id": "attendance_present",
  "recipient_type": "all",
  "use_custom_message": false
}
```

Or with custom message:
```json
{
  "batch_id": 1,
  "custom_message": "Dear parent, your child was present today",
  "recipient_type": "individual",
  "student_ids": [1, 2, 3],
  "use_custom_message": true
}
```

### 4. Get SMS Logs
**Endpoint**: `GET /api/sms/logs`

**Query Parameters**:
- `page` (optional): Page number
- `per_page` (optional): Items per page
- `status` (optional): Filter by status (sent, failed, pending)
- `phone` (optional): Filter by phone number
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)

### 5. Get SMS Balance
**Endpoint**: `GET /api/sms/balance`

**Response**:
```json
{
  "success": true,
  "data": {
    "balance": 500,
    "total_sent": 250,
    "sent_this_month": 45
  }
}
```

### 6. Add SMS Credits (Super User Only)
**Endpoint**: `POST /api/sms/balance/add`

**Request Body**:
```json
{
  "user_id": 2,
  "amount": 500
}
```

## 📊 Character Counting

The system uses a special character counting system:
- **English characters**: 1 character each
- **Bengali characters**: 2 characters each
- **Maximum**: 130 characters per SMS

Example:
```
"Hello" = 5 characters
"হ্যালো" = 10 characters (5 Bengali chars × 2)
"Hello হ্যালো" = 15 characters
```

## 🔒 Security Features

1. **Role-based Access**: Only Teachers and Super Users can send SMS
2. **Balance Checking**: Prevents sending if insufficient balance
3. **Phone Validation**: Validates Bangladesh mobile numbers
4. **Audit Logging**: All SMS sends are logged
5. **Hardcoded Credentials**: Cannot be accidentally changed

## ⚠️ Important Notes

### DO NOT CHANGE

The SMS API configuration is **permanently hardcoded**. Do not attempt to:
- Change API credentials in code
- Add SMS_API_KEY to .env
- Modify the `send_sms_via_api()` function

### Phone Number Format

The system automatically handles these formats:
- `01712345678` → Valid
- `8801712345678` → Valid (auto-converted)
- `+8801712345678` → Valid (auto-converted)

### Bangladesh Numbers Only

Only Bangladesh mobile numbers starting with `01` are accepted:
- `017` - Grameenphone, Robi, Airtel
- `018` - Robi, Airtel
- `019` - Banglalink, Teletalk
- `013` - Grameenphone
- `014` - Banglalink
- `015` - Teletalk
- `016` - Airtel

## 📞 Support

If SMS is not working:

1. **Check SMS Balance**: `GET /api/sms/balance`
2. **View Logs**: `GET /api/sms/logs`
3. **Test Single SMS**: Send to your own number first
4. **Verify Phone Format**: Must be valid Bangladesh number

The API credentials are correct and hardcoded - no configuration needed!

---

**API Provider**: BulkSMSBD  
**Last Updated**: October 19, 2025  
**Status**: Production Ready ✅  
**Configuration**: Hardcoded (No changes needed)
