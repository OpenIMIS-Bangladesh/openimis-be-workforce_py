# API Error Codes

This document defines structure for API error responses and lists all error codes used in the system.

---

## 🔧 Error Response Format

All API errors follow this JSON structure:

```json
{
  "error": "<short_error_key>",
  "code": "<numeric_code>",
  "message": "<human-readable message>"
}

```

### Field Explanation

| Field   | Type   | Description                            |
|---------|--------|----------------------------------------|
| error   | string | Short identifier for the error.        |
| code    | int    | Unique numeric code for the error.     |
| message | string | Readable message describing the error. |



### Error Codes

| Code | Error Key                   | Description                                                           |
|------|-----------------------------|-----------------------------------------------------------------------|
| 1001 | login_name_already_exists   | Thrown when creating a user with a duplicate login name.              |
| 1002 | phone_number_already_exists | Thrown when creating a user with an existing phone number.            |
| 1003 | duplicate_nid   | Thrown when creating a user with a duplicate nid, from workforce_user |
| 1004 | duplicate_phone_number | Thrown when creating a user with an existing phone number,  from workforce_user           |
