# Traceability Matrix

| FR | Endpoint(s) | Screen(s) | Test(s) |
|---|---|---|---|
| FR1 Upload + analyze | POST /charts/analyze | /analyze | TC-03, TC-04, TC-05 |
| FR2 CNN detection | POST /charts/analyze | /analyze | TC-03, TC-05, TC-06 |
| FR3 Educational signal | POST /charts/analyze | /analyze | TC-06 |
| FR4 Disclaimer | All analysis responses | /analyze | TC-06 |
| FR5 Lessons | GET /lessons, GET /lessons/{id} | /learn, /learn/[id] | TC-07, TC-12 |
| FR6 Quizzes | POST /lessons/{id}/quiz | /learn/[id] | TC-07 |
| FR7 Risk calculator | POST /risk/calculate | /risk | TC-09 |
| FR8 Market quotes | GET /market/quote | /market | TC-10 |
| FR9 Journal | GET/POST /journal | /journal | TC-11 |
| FR10 Dashboard | GET /dashboard | /dashboard | TC-07 |
| FR11 Assistant | POST /assistant/chat | /assistant | TC-08 |
| FR12 Admin | GET/POST /admin/lessons | /admin | TC-12 |
| FR13 Reports | GET /reports/activity | /reports | TC-11 |
