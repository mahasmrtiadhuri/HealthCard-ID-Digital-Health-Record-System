#!/usr/bin/env python3
"""
Debug the patient access restriction issue
"""

import requests
import json

# Test the specific endpoint that's failing
base_url = "https://bcd54ab1-eacf-4dd6-b947-589584660f93.preview.emergentagent.com"
api_url = f"{base_url}/api"

# Register a test patient
patient_data = {
    "email": "debug_patient@test.com",
    "password": "TestPass123!",
    "name": "Debug Patient",
    "role": "patient"
}

response = requests.post(f"{api_url}/auth/register", json=patient_data)
if response.status_code == 200:
    patient_token = response.json()["access_token"]
    print("✅ Patient registered successfully")
    
    # Get patient profile to get patient ID
    response = requests.get(f"{api_url}/patients/me", headers={'Authorization': f'Bearer {patient_token}'})
    if response.status_code == 200:
        patient_id = response.json()["id"]
        print(f"✅ Patient ID: {patient_id}")
        
        # Try to access the doctor-only endpoint
        response = requests.get(
            f"{api_url}/audit-logs/patient/{patient_id}",
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 403:
            print("✅ Access restriction working correctly")
        else:
            print("❌ Access restriction NOT working - patient can access doctor endpoint")
    else:
        print(f"❌ Failed to get patient profile: {response.text}")
else:
    print(f"❌ Failed to register patient: {response.text}")