#!/usr/bin/env python3
"""
Debug unauthenticated access issue
"""

import requests

base_url = "https://bcd54ab1-eacf-4dd6-b947-589584660f93.preview.emergentagent.com"
api_url = f"{base_url}/api"

# Try to access audit-logs without authentication
response = requests.get(f"{api_url}/audit-logs")

print(f"📊 Status Code: {response.status_code}")
print(f"📊 Response: {response.text}")

if response.status_code == 401:
    print("✅ Unauthenticated access properly blocked")
else:
    print("❌ Unauthenticated access NOT properly blocked")