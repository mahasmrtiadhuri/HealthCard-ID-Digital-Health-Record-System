#!/usr/bin/env python3
"""
Test file upload audit logging
"""

import requests
import io

base_url = "https://bcd54ab1-eacf-4dd6-b947-589584660f93.preview.emergentagent.com"
api_url = f"{base_url}/api"

# Register a test patient
patient_data = {
    "email": "file_audit_patient@test.com",
    "password": "TestPass123!",
    "name": "File Audit Patient",
    "role": "patient"
}

response = requests.post(f"{api_url}/auth/register", json=patient_data)
if response.status_code == 200:
    patient_token = response.json()["access_token"]
    print("✅ Patient registered successfully")
    
    # Create a test PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
    
    # Upload file
    files = {'file': ('audit_test_report.pdf', io.BytesIO(pdf_content), 'application/pdf')}
    response = requests.post(
        f"{api_url}/upload/medical-report",
        files=files,
        headers={'Authorization': f'Bearer {patient_token}'}
    )
    
    if response.status_code == 200:
        print("✅ File uploaded successfully")
        
        # Wait a moment for audit log to be created
        import time
        time.sleep(2)
        
        # Check audit logs for file upload
        response = requests.get(
            f"{api_url}/audit-logs",
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        
        if response.status_code == 200:
            audit_logs = response.json()
            file_upload_logs = [log for log in audit_logs if log.get("resource_type") == "file_upload"]
            
            if file_upload_logs:
                print("✅ File upload audit log found")
                log = file_upload_logs[0]
                print(f"   📝 Description: {log.get('description')}")
                print(f"   📝 User: {log.get('user_name')} ({log.get('user_role')})")
                print(f"   📝 Action: {log.get('action')}")
                print(f"   📝 New values: {log.get('new_values', {}).keys()}")
            else:
                print("❌ No file upload audit log found")
                print(f"   📊 Found {len(audit_logs)} total audit logs")
                resource_types = [log.get("resource_type") for log in audit_logs]
                print(f"   📊 Resource types: {set(resource_types)}")
        else:
            print(f"❌ Failed to get audit logs: {response.text}")
    else:
        print(f"❌ File upload failed: {response.text}")
else:
    print(f"❌ Failed to register patient: {response.text}")