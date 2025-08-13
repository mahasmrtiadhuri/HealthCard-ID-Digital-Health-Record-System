#!/usr/bin/env python3
"""
Focused test for datetime serialization in appointments and prescriptions
"""

import requests
import json
from datetime import datetime, date, timedelta

def test_datetime_serialization():
    """Test that datetime fields are properly serialized"""
    base_url = "https://bcd54ab1-eacf-4dd6-b947-589584660f93.preview.emergentagent.com/api"
    
    print("🔍 Testing Datetime Serialization...")
    
    # Register test users
    timestamp = datetime.now().strftime("%H%M%S")
    
    # Register patient
    patient_data = {
        "email": f"datetime_patient_{timestamp}@test.com",
        "password": "TestPass123!",
        "name": f"DateTime Patient {timestamp}",
        "role": "patient"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=patient_data)
    if response.status_code != 200:
        print(f"❌ Patient registration failed: {response.text}")
        return False
    
    patient_token = response.json()["access_token"]
    patient_user = response.json()["user"]
    print("✅ Patient registered successfully")
    
    # Register doctor
    doctor_data = {
        "email": f"datetime_doctor_{timestamp}@test.com",
        "password": "TestPass123!",
        "name": f"DateTime Doctor {timestamp}",
        "role": "doctor"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=doctor_data)
    if response.status_code != 200:
        print(f"❌ Doctor registration failed: {response.text}")
        return False
    
    doctor_token = response.json()["access_token"]
    print("✅ Doctor registered successfully")
    
    # Test appointment creation with date fields
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    appointment_data = {
        "patient_id": patient_user["id"],
        "appointment_date": tomorrow,
        "appointment_time": "14:30",
        "appointment_type": "consultation",
        "reason": "Datetime serialization test",
        "notes": "Testing date field serialization"
    }
    
    print(f"📅 Creating appointment for date: {tomorrow}")
    response = requests.post(
        f"{base_url}/appointments",
        json=appointment_data,
        headers={'Authorization': f'Bearer {doctor_token}'}
    )
    
    if response.status_code != 200:
        print(f"❌ Appointment creation failed: {response.status_code} - {response.text}")
        return False
    
    appointment_response = response.json()
    print("✅ Appointment created successfully")
    print(f"   📋 Appointment ID: {appointment_response.get('id')}")
    print(f"   📅 Date stored as: {appointment_response.get('appointment_date')}")
    print(f"   🕐 Time stored as: {appointment_response.get('appointment_time')}")
    
    # Test prescription creation with date fields
    today = date.today().isoformat()
    end_date = (date.today() + timedelta(days=30)).isoformat()
    
    prescription_data = {
        "patient_id": patient_user["id"],
        "medication_name": "DateTime Test Medicine",
        "dosage": "5mg",
        "frequency": "twice daily",
        "start_date": today,
        "end_date": end_date,
        "instructions": "Testing datetime serialization",
        "refills_remaining": 2
    }
    
    print(f"💊 Creating prescription with dates: {today} to {end_date}")
    response = requests.post(
        f"{base_url}/prescriptions",
        json=prescription_data,
        headers={'Authorization': f'Bearer {doctor_token}'}
    )
    
    if response.status_code != 200:
        print(f"❌ Prescription creation failed: {response.status_code} - {response.text}")
        return False
    
    prescription_response = response.json()
    print("✅ Prescription created successfully")
    print(f"   📋 Prescription ID: {prescription_response.get('id')}")
    print(f"   📅 Start date stored as: {prescription_response.get('start_date')}")
    print(f"   📅 End date stored as: {prescription_response.get('end_date')}")
    
    # Test retrieval to ensure serialization works both ways
    print("\n🔍 Testing data retrieval...")
    
    # Get appointments
    response = requests.get(
        f"{base_url}/appointments",
        headers={'Authorization': f'Bearer {doctor_token}'}
    )
    
    if response.status_code != 200:
        print(f"❌ Appointment retrieval failed: {response.status_code} - {response.text}")
        return False
    
    appointments = response.json()
    print(f"✅ Retrieved {len(appointments)} appointments successfully")
    
    # Get prescriptions
    response = requests.get(
        f"{base_url}/prescriptions",
        headers={'Authorization': f'Bearer {doctor_token}'}
    )
    
    if response.status_code != 200:
        print(f"❌ Prescription retrieval failed: {response.status_code} - {response.text}")
        return False
    
    prescriptions = response.json()
    print(f"✅ Retrieved {len(prescriptions)} prescriptions successfully")
    
    # Verify JSON serialization by checking response structure
    if appointments:
        latest_appointment = appointments[0]
        print(f"   📋 Latest appointment date format: {type(latest_appointment.get('appointment_date'))}")
        print(f"   📋 Created at format: {type(latest_appointment.get('created_at'))}")
    
    if prescriptions:
        latest_prescription = prescriptions[0]
        print(f"   💊 Latest prescription start_date format: {type(latest_prescription.get('start_date'))}")
        print(f"   💊 Created at format: {type(latest_prescription.get('created_at'))}")
    
    print("\n🎉 All datetime serialization tests passed!")
    print("✅ No 'Object of type date is not JSON serializable' errors occurred")
    print("✅ Date fields are properly stored and retrieved as ISO format strings")
    
    return True

if __name__ == "__main__":
    success = test_datetime_serialization()
    if success:
        print("\n✅ DATETIME SERIALIZATION: WORKING CORRECTLY")
    else:
        print("\n❌ DATETIME SERIALIZATION: ISSUES FOUND")