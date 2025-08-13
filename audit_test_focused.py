#!/usr/bin/env python3
"""
Focused Audit Logging System Test
Tests specifically the audit logging functionality
"""

import requests
import sys
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

class AuditLoggingTester:
    def __init__(self, base_url="https://bcd54ab1-eacf-4dd6-b947-589584660f93.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.patient_token = None
        self.doctor_token = None
        self.patient_user = None
        self.doctor_user = None
        self.patient_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    token: Optional[str] = None, expected_status: int = 200) -> tuple[bool, Dict]:
        """Make HTTP request and validate response"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text, "status_code": response.status_code}

            return success, response_data

        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    def setup_users(self):
        """Setup test users"""
        print("🔧 Setting up test users...")
        
        timestamp = datetime.now().strftime("%H%M%S")
        
        # Register patient
        patient_data = {
            "email": f"audit_patient_{timestamp}@test.com",
            "password": "TestPass123!",
            "name": f"Audit Test Patient {timestamp}",
            "role": "patient"
        }
        
        success, response = self.make_request("POST", "auth/register", patient_data)
        if success and "access_token" in response:
            self.patient_token = response["access_token"]
            self.patient_user = response["user"]
            print(f"✅ Patient registered: {self.patient_user['name']}")
        else:
            print(f"❌ Patient registration failed: {response}")
            return False

        # Register doctor
        doctor_data = {
            "email": f"audit_doctor_{timestamp}@test.com",
            "password": "TestPass123!",
            "name": f"Dr. Audit Test {timestamp}",
            "role": "doctor",
            "specialization": "Internal Medicine"
        }
        
        success, response = self.make_request("POST", "auth/register", doctor_data)
        if success and "access_token" in response:
            self.doctor_token = response["access_token"]
            self.doctor_user = response["user"]
            print(f"✅ Doctor registered: {self.doctor_user['name']}")
        else:
            print(f"❌ Doctor registration failed: {response}")
            return False

        # Get patient profile to get patient ID
        success, response = self.make_request("GET", "patients/me", token=self.patient_token)
        if success:
            self.patient_id = response.get("id")
            print(f"✅ Patient ID obtained: {self.patient_id}")
        else:
            print(f"❌ Failed to get patient profile: {response}")
            return False

        return True

    def test_audit_log_creation(self):
        """Test that audit logs are created for various operations"""
        print("\n🔍 Testing Audit Log Creation...")
        
        # 1. Patient profile update
        update_data = {
            "age": 28,
            "gender": "Female",
            "blood_group": "A+",
            "weight": 65.0,
            "height": 165.0,
            "allergies": ["Latex", "Penicillin"],
            "chronic_conditions": ["Asthma"],
            "current_medications": ["Albuterol"]
        }
        
        success, response = self.make_request("PUT", "patients/me", update_data, token=self.patient_token)
        if success:
            self.log_test("Patient Profile Update", True)
        else:
            self.log_test("Patient Profile Update", False, str(response))

        # 2. Medical record creation
        record_data = {
            "patient_id": self.patient_user["id"],
            "title": "Comprehensive Health Assessment",
            "description": "Annual health checkup with complete blood work and physical examination",
            "record_type": "report"
        }
        
        success, response = self.make_request("POST", "medical-records", record_data, token=self.doctor_token)
        if success:
            self.log_test("Medical Record Creation", True)
        else:
            self.log_test("Medical Record Creation", False, str(response))

        # 3. Appointment creation
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        appointment_data = {
            "patient_id": self.patient_user["id"],
            "appointment_date": tomorrow,
            "appointment_time": "09:00",
            "appointment_type": "consultation",
            "reason": "Follow-up for asthma management",
            "notes": "Patient reports improved breathing with current medication"
        }
        
        success, response = self.make_request("POST", "appointments", appointment_data, token=self.doctor_token)
        if success:
            self.log_test("Appointment Creation", True)
        else:
            self.log_test("Appointment Creation", False, str(response))

        # 4. Prescription creation
        today = date.today().isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()
        prescription_data = {
            "patient_id": self.patient_user["id"],
            "medication_name": "Albuterol Inhaler",
            "dosage": "90mcg",
            "frequency": "2 puffs as needed",
            "start_date": today,
            "end_date": end_date,
            "instructions": "Use as rescue inhaler for asthma symptoms",
            "refills_remaining": 2
        }
        
        success, response = self.make_request("POST", "prescriptions", prescription_data, token=self.doctor_token)
        if success:
            self.log_test("Prescription Creation", True)
        else:
            self.log_test("Prescription Creation", False, str(response))

        return True

    def test_audit_log_retrieval(self):
        """Test audit log retrieval endpoints"""
        print("\n🔍 Testing Audit Log Retrieval...")
        
        # Wait for audit logs to be created
        import time
        time.sleep(3)
        
        # 1. Patient retrieves their own audit logs
        success, response = self.make_request("GET", "audit-logs", token=self.patient_token)
        if success and isinstance(response, list):
            patient_logs = response
            self.log_test("Patient Audit Logs Retrieval", True)
            print(f"   📊 Found {len(patient_logs)} audit logs for patient")
            
            if patient_logs:
                # Display sample audit log
                sample_log = patient_logs[0]
                print(f"   📝 Sample log: {sample_log.get('user_name')} {sample_log.get('action')} {sample_log.get('resource_type')}")
                print(f"   📝 Description: {sample_log.get('description')}")
        else:
            self.log_test("Patient Audit Logs Retrieval", False, str(response))
            patient_logs = []

        # 2. Doctor retrieves their audit logs
        success, response = self.make_request("GET", "audit-logs", token=self.doctor_token)
        if success and isinstance(response, list):
            doctor_logs = response
            self.log_test("Doctor Audit Logs Retrieval", True)
            print(f"   📊 Found {len(doctor_logs)} audit logs for doctor")
            
            if doctor_logs:
                # Display sample audit log
                sample_log = doctor_logs[0]
                print(f"   📝 Sample log: {sample_log.get('user_name')} {sample_log.get('action')} {sample_log.get('resource_type')}")
                print(f"   📝 Description: {sample_log.get('description')}")
        else:
            self.log_test("Doctor Audit Logs Retrieval", False, str(response))
            doctor_logs = []

        # 3. Doctor retrieves patient-specific audit logs
        if self.patient_id:
            success, response = self.make_request("GET", f"audit-logs/patient/{self.patient_id}", token=self.doctor_token)
            if success and "audit_logs" in response:
                patient_specific_logs = response["audit_logs"]
                self.log_test("Patient-Specific Audit Logs", True)
                print(f"   📊 Found {len(patient_specific_logs)} patient-specific audit logs")
                print(f"   📊 Total logs reported: {response.get('total_logs', 'N/A')}")
            else:
                self.log_test("Patient-Specific Audit Logs", False, str(response))

        return patient_logs, doctor_logs

    def test_audit_log_content(self, patient_logs, doctor_logs):
        """Test audit log content and structure"""
        print("\n🔍 Testing Audit Log Content...")
        
        all_logs = patient_logs + doctor_logs
        
        if not all_logs:
            self.log_test("Audit Log Content Test", False, "No audit logs found")
            return False

        # Test required fields
        required_fields = ["user_id", "user_name", "user_role", "action", "resource_type", 
                          "resource_id", "description", "created_at"]
        
        sample_log = all_logs[0]
        missing_fields = [field for field in required_fields if field not in sample_log]
        
        if not missing_fields:
            self.log_test("Required Fields Present", True)
        else:
            self.log_test("Required Fields Present", False, f"Missing: {missing_fields}")

        # Test datetime serialization
        if "created_at" in sample_log:
            try:
                datetime.fromisoformat(sample_log["created_at"].replace('Z', '+00:00'))
                self.log_test("Datetime Serialization", True)
            except ValueError:
                self.log_test("Datetime Serialization", False, f"Invalid format: {sample_log['created_at']}")

        # Test change tracking (old_values, new_values)
        profile_updates = [log for log in all_logs if log.get("resource_type") == "patient_profile"]
        if profile_updates:
            profile_log = profile_updates[0]
            if "old_values" in profile_log and "new_values" in profile_log:
                self.log_test("Change Tracking (old/new values)", True)
                print(f"   📝 Old values keys: {list(profile_log.get('old_values', {}).keys())}")
                print(f"   📝 New values keys: {list(profile_log.get('new_values', {}).keys())}")
            else:
                self.log_test("Change Tracking (old/new values)", False, "Missing old_values or new_values")

        # Test resource type variety
        resource_types = set(log.get("resource_type") for log in all_logs)
        expected_types = {"patient_profile", "medical_record", "appointment", "prescription"}
        found_types = resource_types.intersection(expected_types)
        
        if len(found_types) >= 3:  # At least 3 different types
            self.log_test("Resource Type Variety", True)
            print(f"   📊 Resource types found: {sorted(resource_types)}")
        else:
            self.log_test("Resource Type Variety", False, f"Only found: {found_types}")

        # Test user information
        user_roles = set(log.get("user_role") for log in all_logs)
        if "patient" in user_roles and "doctor" in user_roles:
            self.log_test("User Role Tracking", True)
        else:
            self.log_test("User Role Tracking", False, f"Roles found: {user_roles}")

        return True

    def test_access_control(self):
        """Test audit log access control"""
        print("\n🔍 Testing Audit Log Access Control...")
        
        # 1. Patient cannot access doctor-only endpoint
        if self.patient_id:
            success, response = self.make_request("GET", f"audit-logs/patient/{self.patient_id}", 
                                                token=self.patient_token, expected_status=403)
            if success:  # Should succeed with 403 (access denied)
                self.log_test("Patient Access Restriction", True)
            else:
                self.log_test("Patient Access Restriction", False, "Patient accessed doctor-only endpoint")

        # 2. Unauthenticated access should fail
        success, response = self.make_request("GET", "audit-logs", expected_status=403)
        if success:  # Should succeed with 403 (not authenticated)
            self.log_test("Unauthenticated Access Protection", True)
        else:
            self.log_test("Unauthenticated Access Protection", False, "Unauthenticated access allowed")

        return True

    def test_audit_log_filtering(self):
        """Test audit log filtering capabilities"""
        print("\n🔍 Testing Audit Log Filtering...")
        
        # Test filtering by resource type
        success, response = self.make_request("GET", "audit-logs?resource_type=appointment", token=self.doctor_token)
        if success and isinstance(response, list):
            appointment_logs = response
            if appointment_logs:
                all_appointments = all(log.get("resource_type") == "appointment" for log in appointment_logs)
                if all_appointments:
                    self.log_test("Resource Type Filtering", True)
                    print(f"   📊 Found {len(appointment_logs)} appointment logs")
                else:
                    self.log_test("Resource Type Filtering", False, "Non-appointment logs in filtered results")
            else:
                self.log_test("Resource Type Filtering", True, "No appointment logs found (acceptable)")
        else:
            self.log_test("Resource Type Filtering", False, str(response))

        # Test filtering with limit
        success, response = self.make_request("GET", "audit-logs?limit=5", token=self.doctor_token)
        if success and isinstance(response, list):
            limited_logs = response
            if len(limited_logs) <= 5:
                self.log_test("Limit Parameter", True)
                print(f"   📊 Returned {len(limited_logs)} logs (limit=5)")
            else:
                self.log_test("Limit Parameter", False, f"Returned {len(limited_logs)} logs, expected ≤5")
        else:
            self.log_test("Limit Parameter", False, str(response))

        return True

    def run_comprehensive_audit_test(self):
        """Run comprehensive audit logging tests"""
        print("🚀 Starting Comprehensive Audit Logging Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)

        # Setup
        if not self.setup_users():
            print("❌ Failed to setup test users")
            return False

        # Run tests
        self.test_audit_log_creation()
        patient_logs, doctor_logs = self.test_audit_log_retrieval()
        self.test_audit_log_content(patient_logs, doctor_logs)
        self.test_access_control()
        self.test_audit_log_filtering()

        # Print results
        print("\n" + "=" * 60)
        print("📊 AUDIT LOGGING TEST RESULTS")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = AuditLoggingTester()
    success = tester.run_comprehensive_audit_test()
    
    if success:
        print("\n🎉 All audit logging tests passed!")
        return 0
    else:
        print("\n⚠️  Some audit logging tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())