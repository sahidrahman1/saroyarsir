# SMS Character Counting System

## Overview
Implemented accurate SMS character counting system that handles:
- **Bangla characters** (2.2x weight compared to English)
- **Mixed Bangla/English** (100 character limit per SMS)
- **Auto-truncation** to fit within SMS limits
- **Hardcoded short templates** (not editable)
- **Custom templates** (user-editable with limits)

## Character Counting Rules

### 1. Pure English SMS
- **First SMS**: 160 characters
- **Subsequent SMS**: 153 characters each
- **Encoding**: GSM-7

### 2. Mixed Bangla/English SMS
- **Per SMS**: 100 characters (weighted)
- **Bangla character weight**: 2.2x English
- **Encoding**: Unicode (UCS-2)
- **Formula**: `weighted_count = (bangla_chars × 2.2) + english_chars`

### 3. Pure Bangla SMS
- **Per SMS**: ~45 characters (70 chars / 1.54)
- **Weight factor**: 2.2x
- **Encoding**: Unicode (UCS-2)

## Template Types

### Hardcoded Templates (NOT Editable)
These are optimized for minimum SMS usage:

1. **Exam Result**
   - Template: `{student_name} পেয়েছে {marks}/{total} ({subject}) {date}`
   - Example: `আহমেদ আলী পেয়েছে 85/100 (গণিত) ২৩/১০/২০২৫`
   - ~40 weighted chars = 1 SMS

2. **Attendance Present**
   - Template: `{student_name} উপস্থিত ({batch_name})`
   - Example: `ফাতিমা খান উপস্থিত (HSC-২৫)`
   - ~30 weighted chars = 1 SMS

3. **Attendance Absent**
   - Template: `{student_name} অনুপস্থিত {date} ({batch_name})`
   - Example: `রহিম উদ্দিন অনুপস্থিত ২৩/১০ (SSC-২৬)`
   - ~40 weighted chars = 1 SMS

4. **Fee Reminder**
   - Template: `{student_name} এর ফি {amount}৳ বকেয়া। শেষ তারিখ {due_date}`
   - Example: `সাকিব হোসেন এর ফি ২৫০০৳ বকেয়া। শেষ তারিখ ৩০/১০`
   - ~50 weighted chars = 1 SMS

### Custom Templates (Editable)
Users can create custom messages with these limits:

1. **Custom Exam** - Max 2 SMS (200 weighted chars)
2. **Custom General** - Max 2 SMS (200 weighted chars)

## API Functions

### `calculate_sms_count(text: str)`
Returns detailed SMS statistics:
```python
{
    'sms_count': 1,              # Number of SMS required
    'char_count': 35,            # Actual character count
    'weighted_count': 77,        # Weighted count (Bangla × 2.2)
    'bangla_chars': 25,          # Number of Bangla chars
    'english_chars': 10,         # Number of English chars
    'type': 'mixed',             # 'english', 'bangla', 'mixed', 'unicode'
    'limit_per_sms': 100,        # Character limit per SMS
    'chars_used': 77,            # Characters used
    'chars_remaining': 23        # Characters remaining
}
```

### `truncate_message(text: str, max_sms: int = 1)`
Automatically truncates message to fit within SMS limit:
```python
long_message = "আমার নাম আহমেদ আলী। আমি একজন ছাত্র। আমি গণিত পড়ি। আমার স্কুল ঢাকায়।"
truncated = sms_service.truncate_message(long_message, max_sms=1)
# Returns message that fits in 1 SMS (100 weighted chars)
```

### `/api/sms/validate-message` (POST)
Validates message and returns character count:
```json
{
  "message": "আহমেদ পেয়েছে 85/100 (গণিত)"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "char_count": 25,
    "weighted_count": 55,
    "sms_count": 1,
    "max_characters": 100,
    "remaining": 45,
    "is_valid": true,
    "type": "mixed",
    "bangla_chars": 15,
    "english_chars": 10
  }
}
```

## Template Management

### Get Templates
```
GET /api/sms/templates
```

Returns all templates with editable flags:
```json
{
  "exam_result": {
    "name": "Exam Result",
    "template": "{student_name} পেয়েছে {marks}/{total} ({subject}) {date}",
    "editable": false,
    "max_sms": 1
  },
  "custom_exam": {
    "name": "Custom Exam Message",
    "default": "{student_name} scored {marks}/{total} in {subject}",
    "editable": true,
    "max_sms": 2
  }
}
```

### Update Template (Only Editable Ones)
```
POST /api/sms/templates/{template_type}
```

```json
{
  "message": "Custom message here",
  "max_sms": 2
}
```

If message exceeds `max_sms`, it will be automatically truncated.

### Preview Template
```
POST /api/sms/templates/preview
```

```json
{
  "template": "{student_name} পেয়েছে {marks}/{total}",
  "template_type": "exam_result"
}
```

Returns preview with accurate SMS count.

## Benefits

1. **Cost Optimization**: Short templates = fewer SMS = lower cost
2. **Bangla Support**: Proper handling of Bangla characters
3. **Automatic Truncation**: Prevents exceeding SMS limits
4. **Real-time Validation**: See SMS count before sending
5. **Hardcoded Templates**: Can't be accidentally modified
6. **Flexible Custom**: Allow custom messages when needed

## Examples

### Example 1: Exam Result (Bangla)
```
Input: আহমেদ আলী পেয়েছে 92/100 (পদার্থবিজ্ঞান) ২৩/১০/২০২৫

Breakdown:
- Bangla chars: 25 (× 2.2 = 55)
- English chars: 17
- Weighted total: 55 + 17 = 72
- SMS count: 1 (within 100 limit)
```

### Example 2: Custom Message (Mixed)
```
Input: Dear Parent, আপনার সন্তান আহমেদ আজ উপস্থিত ছিলেন। তার পরীক্ষা খুব ভালো হয়েছে। ধন্যবাদ।

Breakdown:
- Bangla chars: 45 (× 2.2 = 99)
- English chars: 18
- Weighted total: 99 + 18 = 117
- SMS count: 2 (exceeds 100 limit)
```

### Example 3: Auto-truncated (Limited to 1 SMS)
```
Input: আমার নাম আহমেদ আলী। আমি একজন ছাত্র। আমি গণিত পড়ি। আমার স্কুল ঢাকায়। আমি প্রতিদিন ক্লাস করি।

Auto-truncate to 1 SMS:
Output: আমার নাম আহমেদ আলী। আমি একজন ছাত্র। আমি গণিত পড়ি।

(Weighted count: 95 ≤ 100)
```

## Deployment Notes

All changes are committed to:
- `services/services/sms_service.py` - SMS counting logic
- `routes/sms_templates.py` - Template management + validation API
- `templates/partials/sms_management.html` - UI (already has validation hooks)

**Ready to deploy to VPS!**
