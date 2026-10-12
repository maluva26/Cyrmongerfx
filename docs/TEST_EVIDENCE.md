# Test Evidence

| ID | Input | Expected | Observed | Pass/Fail | Defect ID | Evidence File |
|---|---|---|---|---|---|---|
| TC-01 | Register valid email/password | 201, user created | | | | |
| TC-02 | Login with wrong password 5x | 429 lockout | | | | |
| TC-03 | Upload valid PNG | 201 analysis | | | | |
| TC-04 | Upload oversized file | 413 | | | | |
| TC-05 | Upload corrupt file | 400 INVALID_IMAGE | | | | |
| TC-06 | Valid analysis result | detections + disclaimer | | | | |
| TC-07 | Submit quiz | score + progress | | | | |
| TC-08 | Assistant educational question | educational reply | | | | |
| TC-09 | Risk entry == stop | ZERO_PRICE_DISTANCE | | | | |
| TC-10 | Market provider down | available:false | | | | |
| TC-11 | List own journal | only own entries | | | | |
| TC-12 | Trader access admin | 403/404 | | | | |
| SEC-01 | Unauthenticated request | 401 | | | | |
| SEC-02 | Access foreign chart | 404 | | | | |
| SEC-03 | Trader admin endpoint | 403 | | | | |
| SEC-04 | Rename .exe to .png | 400 | | | | |
| SEC-05 | Lockout after failures | 429 | | | | |
| SEC-06 | Inspect password hash | argon2$ prefix | | | | |
| SEC-07 | Admin action | audit log entry | | | | |
| SEC-08 | Inspect cookies | Secure HttpOnly SameSite | | | | |
