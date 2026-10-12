#!/bin/bash
TOKEN=$(cat "C:\Users\Maluva_26\Desktop\forexai\token_only.json" | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")
curl -s http://localhost:8000/api/v1/lessons -H "Authorization: Bearer $TOKEN" -w "\nHTTP:%{http_code}"