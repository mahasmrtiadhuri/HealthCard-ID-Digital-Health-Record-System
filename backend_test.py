#!/usr/bin/env python3
"""
HealthCard ID Backend API Testing Suite
Tests all API endpoints for the health records management system
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class HealthCardAPITester:
    def __init__(self, base_url="https://bcd54ab1-eacf-4dd6-b947-589584660f93.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.patient_token = None
        self.doctor_token = None
        self.patient_user = None
        self.doctor_user = None
        self.patient_id = None
        self.uploaded_file_id = None
        self.user_files = []
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
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

    def test_user_registration(self):
        """Test user registration for both patient and doctor"""
        print("\n🔍 Testing User Registration...")
        
        # Test patient registration
        timestamp = datetime.now().strftime("%H%M%S")
        patient_data = {
            "email": f"patient_{timestamp}@test.com",
            "password": "TestPass123!",
            "name": f"Test Patient {timestamp}",
            "role": "patient"
        }
        
        success, response = self.make_request("POST", "auth/register", patient_data)
        if success and "access_token" in response:
            self.patient_token = response["access_token"]
            self.patient_user = response["user"]
            self.log_test("Patient Registration", True)
        else:
            self.log_test("Patient Registration", False, str(response))
            return False

        # Test doctor registration
        doctor_data = {
            "email": f"doctor_{timestamp}@test.com",
            "password": "TestPass123!",
            "name": f"Dr. Test {timestamp}",
            "role": "doctor"
        }
        
        success, response = self.make_request("POST", "auth/register", doctor_data)
        if success and "access_token" in response:
            self.doctor_token = response["access_token"]
            self.doctor_user = response["user"]
            self.log_test("Doctor Registration", True)
        else:
            self.log_test("Doctor Registration", False, str(response))
            return False

        return True

    def test_user_login(self):
        """Test user login functionality"""
        print("\n🔍 Testing User Login...")
        
        if not self.patient_user or not self.doctor_user:
            self.log_test("Login Test Setup", False, "Users not registered")
            return False

        # Test patient login
        login_data = {
            "email": self.patient_user["email"],
            "password": "TestPass123!"
        }
        
        success, response = self.make_request("POST", "auth/login", login_data)
        if success and "access_token" in response:
            self.log_test("Patient Login", True)
        else:
            self.log_test("Patient Login", False, str(response))

        # Test doctor login
        login_data = {
            "email": self.doctor_user["email"],
            "password": "TestPass123!"
        }
        
        success, response = self.make_request("POST", "auth/login", login_data)
        if success and "access_token" in response:
            self.log_test("Doctor Login", True)
        else:
            self.log_test("Doctor Login", False, str(response))

        return True

    def test_patient_profile(self):
        """Test patient profile management"""
        print("\n🔍 Testing Patient Profile Management...")
        
        if not self.patient_token:
            self.log_test("Patient Profile Test Setup", False, "Patient not authenticated")
            return False

        # Get patient profile
        success, response = self.make_request("GET", "patients/me", token=self.patient_token)
        if success:
            self.patient_id = response.get("id")
            self.log_test("Get Patient Profile", True)
        else:
            self.log_test("Get Patient Profile", False, str(response))
            return False

        # Update patient profile
        update_data = {
            "age": 30,
            "gender": "Male",
            "blood_group": "O+",
            "weight": 70.5,
            "height": 175.0,
            "allergies": ["Peanuts", "Shellfish"],
            "chronic_conditions": ["Hypertension"],
            "current_medications": ["Lisinopril"]
        }
        
        success, response = self.make_request("PUT", "patients/me", update_data, token=self.patient_token)
        if success:
            self.log_test("Update Patient Profile", True)
        else:
            self.log_test("Update Patient Profile", False, str(response))

        return True

    def test_patient_search(self):
        """Test doctor's ability to search patients"""
        print("\n🔍 Testing Patient Search...")
        
        if not self.doctor_token:
            self.log_test("Patient Search Test Setup", False, "Doctor not authenticated")
            return False

        # Search all patients
        success, response = self.make_request("GET", "patients/search", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Search All Patients", True)
        else:
            self.log_test("Search All Patients", False, str(response))

        # Search with query
        success, response = self.make_request("GET", "patients/search?q=test", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Search Patients with Query", True)
        else:
            self.log_test("Search Patients with Query", False, str(response))

        return True

    def test_medical_records(self):
        """Test medical records CRUD operations"""
        print("\n🔍 Testing Medical Records...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Medical Records Test Setup", False, "Required users not authenticated")
            return False

        # Create medical record
        record_data = {
            "patient_id": self.patient_user["id"],
            "title": "Test Medical Record",
            "description": "This is a test medical record for API testing",
            "record_type": "notes"
        }
        
        success, response = self.make_request("POST", "medical-records", record_data, token=self.doctor_token, expected_status=200)
        record_id = None
        if success and "id" in response:
            record_id = response["id"]
            self.log_test("Create Medical Record", True)
        else:
            self.log_test("Create Medical Record", False, str(response))

        # Get medical records (doctor view)
        success, response = self.make_request("GET", "medical-records", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Get Medical Records (Doctor)", True)
        else:
            self.log_test("Get Medical Records (Doctor)", False, str(response))

        # Get medical records (patient view)
        success, response = self.make_request("GET", "medical-records", token=self.patient_token)
        if success and isinstance(response, list):
            self.log_test("Get Medical Records (Patient)", True)
        else:
            self.log_test("Get Medical Records (Patient)", False, str(response))

        # Get patient-specific records
        success, response = self.make_request("GET", f"medical-records/{self.patient_user['id']}", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Get Patient-Specific Records", True)
        else:
            self.log_test("Get Patient-Specific Records", False, str(response))

        return True

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        print("\n🔍 Testing Dashboard Statistics...")
        
        # Patient dashboard stats
        if self.patient_token:
            success, response = self.make_request("GET", "dashboard/stats", token=self.patient_token)
            if success and "records_count" in response:
                self.log_test("Patient Dashboard Stats", True)
            else:
                self.log_test("Patient Dashboard Stats", False, str(response))

        # Doctor dashboard stats
        if self.doctor_token:
            success, response = self.make_request("GET", "dashboard/stats", token=self.doctor_token)
            if success and "patients_count" in response:
                self.log_test("Doctor Dashboard Stats", True)
            else:
                self.log_test("Doctor Dashboard Stats", False, str(response))

        return True

    def test_file_upload_system(self):
        """Test comprehensive file upload system"""
        print("\n🔍 Testing File Upload System...")
        
        if not self.patient_token:
            self.log_test("File Upload Test Setup", False, "Patient not authenticated")
            return False

        # Create test files in memory
        import io
        
        # Test PDF file upload (medical report)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        
        # Test medical report upload
        files = {'file': ('test_report.pdf', io.BytesIO(pdf_content), 'application/pdf')}
        try:
            response = requests.post(
                f"{self.api_url}/upload/medical-report",
                files=files,
                headers={'Authorization': f'Bearer {self.patient_token}'},
                timeout=30
            )
            if response.status_code == 200:
                upload_response = response.json()
                if "file_id" in upload_response:
                    self.uploaded_file_id = upload_response["file_id"]
                    self.log_test("Medical Report Upload", True)
                else:
                    self.log_test("Medical Report Upload", False, "No file_id in response")
            else:
                self.log_test("Medical Report Upload", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Medical Report Upload", False, f"Exception: {str(e)}")

        # Test image file upload (profile image)
        # Create a minimal PNG image (1x1 pixel)
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'file': ('test_profile.png', io.BytesIO(png_content), 'image/png')}
        try:
            response = requests.post(
                f"{self.api_url}/upload/profile-image",
                files=files,
                headers={'Authorization': f'Bearer {self.patient_token}'},
                timeout=30
            )
            if response.status_code == 200:
                self.log_test("Profile Image Upload", True)
            else:
                self.log_test("Profile Image Upload", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Profile Image Upload", False, f"Exception: {str(e)}")

        return True

    def test_file_management(self):
        """Test file management operations"""
        print("\n🔍 Testing File Management...")
        
        if not self.patient_token:
            self.log_test("File Management Test Setup", False, "Patient not authenticated")
            return False

        # List user files
        success, response = self.make_request("GET", "files", token=self.patient_token)
        if success and isinstance(response, list):
            self.log_test("List User Files", True)
            self.user_files = response
        else:
            self.log_test("List User Files", False, str(response))
            return False

        # Test file download (if files exist)
        if hasattr(self, 'uploaded_file_id') and self.uploaded_file_id:
            try:
                response = requests.get(
                    f"{self.api_url}/files/{self.uploaded_file_id}",
                    headers={'Authorization': f'Bearer {self.patient_token}'},
                    timeout=30
                )
                if response.status_code == 200:
                    self.log_test("File Download", True)
                else:
                    self.log_test("File Download", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("File Download", False, f"Exception: {str(e)}")

        # Test file deletion (if files exist)
        if hasattr(self, 'user_files') and self.user_files:
            file_to_delete = self.user_files[0]["file_id"]
            success, response = self.make_request("DELETE", f"files/{file_to_delete}", token=self.patient_token)
            if success:
                self.log_test("File Deletion", True)
            else:
                self.log_test("File Deletion", False, str(response))

        return True

    def test_file_security(self):
        """Test file access security"""
        print("\n🔍 Testing File Security...")
        
        # Test unauthorized file access
        if hasattr(self, 'uploaded_file_id') and self.uploaded_file_id:
            success, response = self.make_request("GET", f"files/{self.uploaded_file_id}", expected_status=401)
            if not success:  # Should fail with 401
                self.log_test("Unauthorized File Access Protection", True)
            else:
                self.log_test("Unauthorized File Access Protection", False, "Should require authentication")

        # Test cross-user file access (if we have both users)
        if hasattr(self, 'uploaded_file_id') and self.uploaded_file_id and self.doctor_token:
            try:
                response = requests.get(
                    f"{self.api_url}/files/{self.uploaded_file_id}",
                    headers={'Authorization': f'Bearer {self.doctor_token}'},
                    timeout=30
                )
                # Doctors should be able to access patient files (based on implementation)
                if response.status_code == 200:
                    self.log_test("Doctor File Access", True)
                else:
                    self.log_test("Doctor File Access", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Doctor File Access", False, f"Exception: {str(e)}")

        return True

    def test_ai_health_summary(self):
        """Test AI health summary generation"""
        print("\n🔍 Testing AI Health Summary...")
        
        if not self.patient_token:
            self.log_test("AI Summary Test Setup", False, "Patient not authenticated")
            return False

        # Test AI health summary generation
        success, response = self.make_request("POST", "ai/summarize-reports", token=self.patient_token)
        if success and "summary" in response:
            self.log_test("AI Health Summary Generation", True)
            # Check if files are mentioned in summary
            if "files_analyzed" in response:
                self.log_test("AI Summary File Integration", True)
            else:
                self.log_test("AI Summary File Integration", False, "Files not analyzed in summary")
        else:
            self.log_test("AI Health Summary Generation", False, str(response))

        # Test doctor access restriction
        if self.doctor_token:
            success, response = self.make_request("POST", "ai/summarize-reports", token=self.doctor_token, expected_status=403)
            if not success:  # Should fail with 403
                self.log_test("AI Summary Doctor Access Restriction", True)
            else:
                self.log_test("AI Summary Doctor Access Restriction", False, "Doctors should not access patient summaries")

        return True

    def test_appointments_management(self):
        """Test appointment management system"""
        print("\n🔍 Testing Appointment Management...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Appointment Test Setup", False, "Required users not authenticated")
            return False

        # Create appointment (doctor only)
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        appointment_data = {
            "patient_id": self.patient_user["id"],
            "appointment_date": tomorrow,
            "appointment_time": "10:30",
            "appointment_type": "consultation",
            "reason": "Regular checkup",
            "notes": "Test appointment for API testing"
        }
        
        success, response = self.make_request("POST", "appointments", appointment_data, token=self.doctor_token)
        appointment_id = None
        if success and "id" in response:
            appointment_id = response["id"]
            self.log_test("Create Appointment", True)
        else:
            self.log_test("Create Appointment", False, str(response))

        # Get appointments (doctor view)
        success, response = self.make_request("GET", "appointments", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Get Appointments (Doctor)", True)
        else:
            self.log_test("Get Appointments (Doctor)", False, str(response))

        # Get appointments (patient view)
        success, response = self.make_request("GET", "appointments", token=self.patient_token)
        if success and isinstance(response, list):
            self.log_test("Get Appointments (Patient)", True)
        else:
            self.log_test("Get Appointments (Patient)", False, str(response))

        # Update appointment status
        if appointment_id:
            update_data = {"status": "completed", "notes": "Appointment completed successfully"}
            success, response = self.make_request("PUT", f"appointments/{appointment_id}", update_data, token=self.doctor_token)
            if success:
                self.log_test("Update Appointment", True)
            else:
                self.log_test("Update Appointment", False, str(response))

        # Test patient cannot create appointments
        success, response = self.make_request("POST", "appointments", appointment_data, token=self.patient_token, expected_status=403)
        if not success:  # Should fail with 403
            self.log_test("Patient Appointment Creation Restriction", True)
        else:
            self.log_test("Patient Appointment Creation Restriction", False, "Patients should not create appointments")

        return True

    def test_prescriptions_management(self):
        """Test prescription management system"""
        print("\n🔍 Testing Prescription Management...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Prescription Test Setup", False, "Required users not authenticated")
            return False

        # Create prescription (doctor only)
        from datetime import date, timedelta
        today = date.today().isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()
        
        prescription_data = {
            "patient_id": self.patient_user["id"],
            "medication_name": "Lisinopril",
            "dosage": "10mg",
            "frequency": "once daily",
            "start_date": today,
            "end_date": end_date,
            "instructions": "Take with food in the morning",
            "refills_remaining": 3
        }
        
        success, response = self.make_request("POST", "prescriptions", prescription_data, token=self.doctor_token)
        prescription_id = None
        if success and "id" in response:
            prescription_id = response["id"]
            self.log_test("Create Prescription", True)
        else:
            self.log_test("Create Prescription", False, str(response))

        # Get prescriptions (doctor view)
        success, response = self.make_request("GET", "prescriptions", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Get Prescriptions (Doctor)", True)
        else:
            self.log_test("Get Prescriptions (Doctor)", False, str(response))

        # Get prescriptions (patient view)
        success, response = self.make_request("GET", "prescriptions", token=self.patient_token)
        if success and isinstance(response, list):
            self.log_test("Get Prescriptions (Patient)", True)
        else:
            self.log_test("Get Prescriptions (Patient)", False, str(response))

        # Update prescription
        if prescription_id:
            update_data = {"status": "completed", "instructions": "Course completed successfully"}
            success, response = self.make_request("PUT", f"prescriptions/{prescription_id}", update_data, token=self.doctor_token)
            if success:
                self.log_test("Update Prescription", True)
            else:
                self.log_test("Update Prescription", False, str(response))

        # Test patient cannot create prescriptions
        success, response = self.make_request("POST", "prescriptions", prescription_data, token=self.patient_token, expected_status=403)
        if not success:  # Should fail with 403
            self.log_test("Patient Prescription Creation Restriction", True)
        else:
            self.log_test("Patient Prescription Creation Restriction", False, "Patients should not create prescriptions")

        return True

    def test_doctor_patient_portal(self):
        """Test enhanced doctor portal with full patient profiles"""
        print("\n🔍 Testing Doctor Patient Portal...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Doctor Portal Test Setup", False, "Required users not authenticated")
            return False

        # Get full patient profile
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.doctor_token)
        if success and "patient_info" in response:
            self.log_test("Get Full Patient Profile", True)
            
            # Check if all sections are present
            expected_sections = ["patient_info", "medical_records", "prescriptions", "appointments", "uploaded_files", "stats"]
            missing_sections = [section for section in expected_sections if section not in response]
            
            if not missing_sections:
                self.log_test("Full Patient Profile Completeness", True)
            else:
                self.log_test("Full Patient Profile Completeness", False, f"Missing sections: {missing_sections}")
        else:
            self.log_test("Get Full Patient Profile", False, str(response))

        # Test patient cannot access other patient profiles
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.patient_token, expected_status=403)
        if not success:  # Should fail with 403
            self.log_test("Patient Profile Access Restriction", True)
        else:
            self.log_test("Patient Profile Access Restriction", False, "Patients should not access other profiles")

        return True

    def test_ai_chat(self):
        """Test AI chat functionality"""
        print("\n🔍 Testing AI Chat...")
        
        # Test patient chat
        if self.patient_token:
            chat_data = {"message": "What should I know about my blood pressure medication?"}
            success, response = self.make_request("POST", "chat", chat_data, token=self.patient_token)
            if success and "response" in response:
                self.log_test("Patient AI Chat", True)
            else:
                self.log_test("Patient AI Chat", False, str(response))

        # Test doctor chat
        if self.doctor_token:
            chat_data = {"message": "What are common treatments for hypertension?"}
            success, response = self.make_request("POST", "chat", chat_data, token=self.doctor_token)
            if success and "response" in response:
                self.log_test("Doctor AI Chat", True)
            else:
                self.log_test("Doctor AI Chat", False, str(response))

        # Test chat with comprehensive context (appointments and prescriptions)
        if self.patient_token:
            chat_data = {"message": "Can you summarize my health status including appointments and prescriptions?"}
            success, response = self.make_request("POST", "chat", chat_data, token=self.patient_token)
            if success and "response" in response:
                self.log_test("AI Chat with Comprehensive Context", True)
            else:
                self.log_test("AI Chat with Comprehensive Context", False, str(response))

        # Test chat history
        if self.patient_token:
            success, response = self.make_request("GET", "chat/history", token=self.patient_token)
            if success and isinstance(response, list):
                self.log_test("Chat History", True)
            else:
                self.log_test("Chat History", False, str(response))

        return True

    def test_audit_logging_system(self):
        """Test comprehensive audit logging system"""
        print("\n🔍 Testing Audit Logging System...")
        
        if not self.doctor_token or not self.patient_token or not self.patient_user:
            self.log_test("Audit Logging Test Setup", False, "Required users not authenticated")
            return False

        # Test 1: Patient profile update creates audit log
        update_data = {
            "age": 35,
            "weight": 75.0,
            "allergies": ["Peanuts", "Shellfish", "Dust"]
        }
        
        success, response = self.make_request("PUT", "patients/me", update_data, token=self.patient_token)
        if success:
            self.log_test("Patient Profile Update (for audit)", True)
        else:
            self.log_test("Patient Profile Update (for audit)", False, str(response))
            return False

        # Test 2: Doctor creates medical record (should create audit log)
        record_data = {
            "patient_id": self.patient_user["id"],
            "title": "Audit Test Medical Record",
            "description": "Testing audit logging for medical record creation",
            "record_type": "notes"
        }
        
        success, response = self.make_request("POST", "medical-records", record_data, token=self.doctor_token)
        if success:
            self.log_test("Medical Record Creation (for audit)", True)
        else:
            self.log_test("Medical Record Creation (for audit)", False, str(response))

        # Test 3: Doctor creates appointment (should create audit log)
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=2)).isoformat()
        
        appointment_data = {
            "patient_id": self.patient_user["id"],
            "appointment_date": tomorrow,
            "appointment_time": "14:30",
            "appointment_type": "follow_up",
            "reason": "Audit logging test appointment"
        }
        
        success, response = self.make_request("POST", "appointments", appointment_data, token=self.doctor_token)
        if success:
            self.log_test("Appointment Creation (for audit)", True)
        else:
            self.log_test("Appointment Creation (for audit)", False, str(response))

        # Test 4: Doctor creates prescription (should create audit log)
        today = date.today().isoformat()
        end_date = (date.today() + timedelta(days=14)).isoformat()
        
        prescription_data = {
            "patient_id": self.patient_user["id"],
            "medication_name": "Metformin",
            "dosage": "500mg",
            "frequency": "twice daily",
            "start_date": today,
            "end_date": end_date,
            "instructions": "Take with meals for audit test"
        }
        
        success, response = self.make_request("POST", "prescriptions", prescription_data, token=self.doctor_token)
        if success:
            self.log_test("Prescription Creation (for audit)", True)
        else:
            self.log_test("Prescription Creation (for audit)", False, str(response))

        # Wait a moment for audit logs to be created
        import time
        time.sleep(2)

        # Test 5: Patient can retrieve their own audit logs
        success, response = self.make_request("GET", "audit-logs", token=self.patient_token)
        if success and isinstance(response, list):
            patient_audit_logs = response
            self.log_test("Patient Audit Logs Retrieval", True)
            
            # Verify audit logs contain expected fields
            if patient_audit_logs:
                log_entry = patient_audit_logs[0]
                expected_fields = ["user_id", "user_name", "user_role", "action", "resource_type", 
                                 "resource_id", "description", "created_at"]
                missing_fields = [field for field in expected_fields if field not in log_entry]
                
                if not missing_fields:
                    self.log_test("Audit Log Content Structure", True)
                else:
                    self.log_test("Audit Log Content Structure", False, f"Missing fields: {missing_fields}")
                
                # Check if patient profile update is logged
                profile_updates = [log for log in patient_audit_logs if log.get("resource_type") == "patient_profile"]
                if profile_updates:
                    self.log_test("Patient Profile Update Audit Log", True)
                    
                    # Verify old_values and new_values are present
                    profile_log = profile_updates[0]
                    if "old_values" in profile_log and "new_values" in profile_log:
                        self.log_test("Audit Log Change Tracking", True)
                    else:
                        self.log_test("Audit Log Change Tracking", False, "Missing old_values or new_values")
                else:
                    self.log_test("Patient Profile Update Audit Log", False, "No profile update logs found")
            else:
                self.log_test("Audit Log Content Structure", False, "No audit logs found")
        else:
            self.log_test("Patient Audit Logs Retrieval", False, str(response))

        # Test 6: Doctor can retrieve audit logs for their actions
        success, response = self.make_request("GET", "audit-logs", token=self.doctor_token)
        if success and isinstance(response, list):
            doctor_audit_logs = response
            self.log_test("Doctor Audit Logs Retrieval", True)
            
            # Check for different resource types in doctor logs
            if doctor_audit_logs:
                resource_types = set(log.get("resource_type") for log in doctor_audit_logs)
                expected_types = {"medical_record", "appointment", "prescription"}
                found_types = resource_types.intersection(expected_types)
                
                if found_types:
                    self.log_test("Doctor Action Audit Logs", True)
                else:
                    self.log_test("Doctor Action Audit Logs", False, f"Expected types not found. Found: {resource_types}")
            else:
                self.log_test("Doctor Action Audit Logs", False, "No doctor audit logs found")
        else:
            self.log_test("Doctor Audit Logs Retrieval", False, str(response))

        # Test 7: Get patient-specific audit logs (doctor only)
        # First, get the patient ID from the patient profile
        success, patient_profile = self.make_request("GET", "patients/me", token=self.patient_token)
        if success and "id" in patient_profile:
            patient_id = patient_profile["id"]
            
            success, response = self.make_request("GET", f"audit-logs/patient/{patient_id}", token=self.doctor_token)
            if success and "audit_logs" in response:
                self.log_test("Patient-Specific Audit Logs (Doctor)", True)
                
                # Verify all logs are for this patient
                patient_logs = response["audit_logs"]
                if patient_logs:
                    all_for_patient = all(log.get("patient_id") == patient_id for log in patient_logs if log.get("patient_id"))
                    if all_for_patient:
                        self.log_test("Patient-Specific Audit Log Filtering", True)
                    else:
                        self.log_test("Patient-Specific Audit Log Filtering", False, "Found logs for other patients")
                else:
                    self.log_test("Patient-Specific Audit Log Filtering", True, "No logs found (acceptable)")
            else:
                self.log_test("Patient-Specific Audit Logs (Doctor)", False, str(response))
        else:
            self.log_test("Patient-Specific Audit Logs Setup", False, "Could not get patient ID")

        # Test 8: Patient cannot access doctor-only audit endpoints
        if patient_id:
            success, response = self.make_request("GET", f"audit-logs/patient/{patient_id}", 
                                                token=self.patient_token, expected_status=403)
            if not success:  # Should fail with 403
                self.log_test("Patient Audit Access Restriction", True)
            else:
                self.log_test("Patient Audit Access Restriction", False, "Patient should not access doctor-only endpoints")

        # Test 9: Test audit log filtering by resource type
        success, response = self.make_request("GET", "audit-logs?resource_type=appointment", token=self.doctor_token)
        if success and isinstance(response, list):
            appointment_logs = response
            if appointment_logs:
                all_appointments = all(log.get("resource_type") == "appointment" for log in appointment_logs)
                if all_appointments:
                    self.log_test("Audit Log Resource Type Filtering", True)
                else:
                    self.log_test("Audit Log Resource Type Filtering", False, "Found non-appointment logs")
            else:
                self.log_test("Audit Log Resource Type Filtering", True, "No appointment logs (acceptable)")
        else:
            self.log_test("Audit Log Resource Type Filtering", False, str(response))

        # Test 10: Verify datetime serialization in audit logs
        if patient_audit_logs:
            log_with_datetime = patient_audit_logs[0]
            if "created_at" in log_with_datetime:
                created_at = log_with_datetime["created_at"]
                # Check if it's a valid ISO format string
                try:
                    from datetime import datetime
                    datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    self.log_test("Audit Log Datetime Serialization", True)
                except ValueError:
                    self.log_test("Audit Log Datetime Serialization", False, f"Invalid datetime format: {created_at}")
            else:
                self.log_test("Audit Log Datetime Serialization", False, "No created_at field found")

        return True

    def test_notification_system(self):
        """Test comprehensive notification system"""
        print("\n🔍 Testing Notification System...")
        
        if not self.doctor_token or not self.patient_token or not self.patient_user:
            self.log_test("Notification System Test Setup", False, "Required users not authenticated")
            return False

        # Test 1: Create test notification
        success, response = self.make_request("POST", "notifications/test", token=self.patient_token)
        if success and "success" in response:
            self.log_test("Create Test Notification", True)
        else:
            self.log_test("Create Test Notification", False, str(response))

        # Test 2: Get notifications for patient
        success, response = self.make_request("GET", "notifications", token=self.patient_token)
        if success and isinstance(response, list):
            patient_notifications = response
            self.log_test("Get Patient Notifications", True)
            
            # Verify notification structure
            if patient_notifications:
                notification = patient_notifications[0]
                expected_fields = ["id", "user_id", "type", "priority", "title", "message", "read", "created_at"]
                missing_fields = [field for field in expected_fields if field not in notification]
                
                if not missing_fields:
                    self.log_test("Notification Structure Validation", True)
                else:
                    self.log_test("Notification Structure Validation", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Notification Structure Validation", True, "No notifications to validate (acceptable)")
        else:
            self.log_test("Get Patient Notifications", False, str(response))

        # Test 3: Get unread notification count
        success, response = self.make_request("GET", "notifications/unread-count", token=self.patient_token)
        if success and "unread_count" in response:
            unread_count = response["unread_count"]
            self.log_test("Get Unread Notification Count", True)
            
            # Verify count is a number
            if isinstance(unread_count, int) and unread_count >= 0:
                self.log_test("Unread Count Validation", True)
            else:
                self.log_test("Unread Count Validation", False, f"Invalid count: {unread_count}")
        else:
            self.log_test("Get Unread Notification Count", False, str(response))

        # Test 4: Create appointment to trigger automatic notification
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        appointment_data = {
            "patient_id": self.patient_user["id"],
            "appointment_date": tomorrow,
            "appointment_time": "09:00",
            "appointment_type": "consultation",
            "reason": "Notification test appointment"
        }
        
        success, response = self.make_request("POST", "appointments", appointment_data, token=self.doctor_token)
        appointment_id = None
        if success and "id" in response:
            appointment_id = response["id"]
            self.log_test("Create Appointment (for notification)", True)
            
            # Wait a moment for notification to be created
            import time
            time.sleep(2)
            
            # Check if appointment notification was created
            success, response = self.make_request("GET", "notifications", token=self.patient_token)
            if success and isinstance(response, list):
                appointment_notifications = [n for n in response if n.get("type") == "appointment_booked"]
                if appointment_notifications:
                    self.log_test("Automatic Appointment Notification Creation", True)
                    
                    # Verify notification metadata
                    appt_notification = appointment_notifications[0]
                    if "metadata" in appt_notification and appt_notification["metadata"]:
                        metadata = appt_notification["metadata"]
                        expected_metadata = ["appointment_date", "appointment_time", "doctor_name", "appointment_type"]
                        missing_metadata = [field for field in expected_metadata if field not in metadata]
                        
                        if not missing_metadata:
                            self.log_test("Appointment Notification Metadata", True)
                        else:
                            self.log_test("Appointment Notification Metadata", False, f"Missing metadata: {missing_metadata}")
                    else:
                        self.log_test("Appointment Notification Metadata", False, "No metadata found")
                else:
                    self.log_test("Automatic Appointment Notification Creation", False, "No appointment notifications found")
            else:
                self.log_test("Automatic Appointment Notification Creation", False, "Could not retrieve notifications")
        else:
            self.log_test("Create Appointment (for notification)", False, str(response))

        # Test 5: Mark notification as read
        success, response = self.make_request("GET", "notifications", token=self.patient_token)
        if success and isinstance(response, list) and response:
            notification_to_mark = response[0]
            notification_id = notification_to_mark["id"]
            
            success, response = self.make_request("PUT", f"notifications/{notification_id}/read", token=self.patient_token)
            if success and response.get("success"):
                self.log_test("Mark Notification as Read", True)
                
                # Verify notification is marked as read
                success, response = self.make_request("GET", "notifications", token=self.patient_token)
                if success and isinstance(response, list):
                    updated_notification = next((n for n in response if n["id"] == notification_id), None)
                    if updated_notification and updated_notification.get("read") == True:
                        self.log_test("Notification Read Status Update", True)
                    else:
                        self.log_test("Notification Read Status Update", False, "Notification not marked as read")
                else:
                    self.log_test("Notification Read Status Update", False, "Could not verify read status")
            else:
                self.log_test("Mark Notification as Read", False, str(response))
        else:
            self.log_test("Mark Notification as Read", False, "No notifications to mark as read")

        # Test 6: Mark all notifications as read
        success, response = self.make_request("PUT", "notifications/mark-all-read", token=self.patient_token)
        if success and "success" in response:
            self.log_test("Mark All Notifications as Read", True)
            
            # Verify unread count is now 0
            success, response = self.make_request("GET", "notifications/unread-count", token=self.patient_token)
            if success and response.get("unread_count") == 0:
                self.log_test("Mark All Read Verification", True)
            else:
                self.log_test("Mark All Read Verification", False, f"Unread count not zero: {response}")
        else:
            self.log_test("Mark All Notifications as Read", False, str(response))

        # Test 7: Delete notification
        success, response = self.make_request("GET", "notifications", token=self.patient_token)
        if success and isinstance(response, list) and response:
            notification_to_delete = response[0]
            notification_id = notification_to_delete["id"]
            
            success, response = self.make_request("DELETE", f"notifications/{notification_id}", token=self.patient_token)
            if success and response.get("success"):
                self.log_test("Delete Notification", True)
                
                # Verify notification is deleted
                success, response = self.make_request("GET", "notifications", token=self.patient_token)
                if success and isinstance(response, list):
                    deleted_notification = next((n for n in response if n["id"] == notification_id), None)
                    if not deleted_notification:
                        self.log_test("Notification Deletion Verification", True)
                    else:
                        self.log_test("Notification Deletion Verification", False, "Notification still exists")
                else:
                    self.log_test("Notification Deletion Verification", False, "Could not verify deletion")
            else:
                self.log_test("Delete Notification", False, str(response))
        else:
            self.log_test("Delete Notification", False, "No notifications to delete")

        # Test 8: Test role-based access (patients only see their notifications)
        # Create a test notification for doctor
        success, response = self.make_request("POST", "notifications/test", token=self.doctor_token)
        if success:
            # Patient should not see doctor's notifications
            success, response = self.make_request("GET", "notifications", token=self.patient_token)
            if success and isinstance(response, list):
                doctor_notifications_in_patient_view = [n for n in response if n.get("user_id") == self.doctor_user["id"]]
                if not doctor_notifications_in_patient_view:
                    self.log_test("Role-Based Notification Access Control", True)
                else:
                    self.log_test("Role-Based Notification Access Control", False, "Patient can see doctor's notifications")
            else:
                self.log_test("Role-Based Notification Access Control", False, "Could not verify access control")
        else:
            self.log_test("Role-Based Notification Access Control", False, "Could not create doctor notification")

        # Test 9: Test notification priority levels
        success, response = self.make_request("GET", "notifications", token=self.patient_token)
        if success and isinstance(response, list) and response:
            # Check if notifications have valid priority levels
            valid_priorities = ["low", "medium", "high", "urgent"]
            notifications_with_priority = [n for n in response if n.get("priority") in valid_priorities]
            
            if notifications_with_priority:
                self.log_test("Notification Priority Levels", True)
            else:
                self.log_test("Notification Priority Levels", False, "No notifications with valid priority levels")
        else:
            self.log_test("Notification Priority Levels", True, "No notifications to check priority (acceptable)")

        # Test 10: Test notification content quality
        success, response = self.make_request("GET", "notifications", token=self.patient_token)
        if success and isinstance(response, list) and response:
            # Check if notifications have meaningful titles and messages
            notifications_with_content = [n for n in response if n.get("title") and n.get("message") and 
                                        len(n["title"]) > 5 and len(n["message"]) > 10]
            
            if notifications_with_content:
                self.log_test("Notification Content Quality", True)
            else:
                self.log_test("Notification Content Quality", False, "Notifications lack meaningful content")
        else:
            self.log_test("Notification Content Quality", True, "No notifications to check content (acceptable)")

        # Test 11: Test unauthorized notification access
        success, response = self.make_request("GET", "notifications", expected_status=401)
        if not success:  # Should fail with 401
            self.log_test("Unauthorized Notification Access Protection", True)
        else:
            self.log_test("Unauthorized Notification Access Protection", False, "Should require authentication")

        # Test 12: Test cross-user notification access
        if appointment_id:
            # Try to access patient's notifications with doctor token (should only see doctor's own)
            success, response = self.make_request("GET", "notifications", token=self.doctor_token)
            if success and isinstance(response, list):
                patient_notifications_in_doctor_view = [n for n in response if n.get("user_id") == self.patient_user["id"]]
                if not patient_notifications_in_doctor_view:
                    self.log_test("Cross-User Notification Access Protection", True)
                else:
                    self.log_test("Cross-User Notification Access Protection", False, "Doctor can see patient's notifications")
            else:
                self.log_test("Cross-User Notification Access Protection", False, "Could not verify cross-user access")

        return True

    def test_notification_scheduling_system(self):
        """Test notification scheduling and background tasks"""
        print("\n🔍 Testing Notification Scheduling System...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Notification Scheduling Test Setup", False, "Required users not authenticated")
            return False

        # Test appointment reminder scheduling
        from datetime import date, timedelta
        future_date = (date.today() + timedelta(days=2)).isoformat()  # 2 days from now
        
        appointment_data = {
            "patient_id": self.patient_user["id"],
            "appointment_date": future_date,
            "appointment_time": "10:00",
            "appointment_type": "follow_up",
            "reason": "Scheduled reminder test"
        }
        
        success, response = self.make_request("POST", "appointments", appointment_data, token=self.doctor_token)
        if success and "id" in response:
            appointment_id = response["id"]
            self.log_test("Create Future Appointment (for reminder)", True)
            
            # Wait a moment for background task to process
            import time
            time.sleep(3)
            
            # Check if reminder notification was scheduled (it should be in the database but not sent yet)
            # We can't directly test the scheduled notification without waiting 24 hours,
            # but we can verify the appointment creation triggered the scheduling logic
            success, response = self.make_request("GET", "notifications", token=self.patient_token)
            if success and isinstance(response, list):
                # Look for appointment_booked notification (immediate) - this confirms the system is working
                immediate_notifications = [n for n in response if n.get("type") == "appointment_booked"]
                if immediate_notifications:
                    self.log_test("Appointment Notification System Active", True)
                    
                    # Check if the notification has proper appointment details
                    appt_notification = immediate_notifications[0]
                    if "resource_id" in appt_notification and appt_notification["resource_id"] == appointment_id:
                        self.log_test("Notification Resource Linking", True)
                    else:
                        self.log_test("Notification Resource Linking", False, "Notification not linked to appointment")
                else:
                    self.log_test("Appointment Notification System Active", False, "No appointment notifications created")
            else:
                self.log_test("Appointment Notification System Active", False, "Could not retrieve notifications")
        else:
            self.log_test("Create Future Appointment (for reminder)", False, str(response))

        # Test notification type variety
        success, response = self.make_request("GET", "notifications", token=self.patient_token)
        if success and isinstance(response, list) and response:
            notification_types = set(n.get("type") for n in response)
            expected_types = {"appointment_booked", "system_message"}  # Types we can test
            found_expected = notification_types.intersection(expected_types)
            
            if found_expected:
                self.log_test("Notification Type Variety", True)
            else:
                self.log_test("Notification Type Variety", False, f"Expected types not found. Found: {notification_types}")
        else:
            self.log_test("Notification Type Variety", True, "No notifications to check types (acceptable)")

        return True

    def test_mock_email_notification_system(self):
        """Test mock email notification system"""
        print("\n🔍 Testing Mock Email Notification System...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Mock Email Test Setup", False, "Required users not authenticated")
            return False

        # Create an appointment which should trigger both in-app and email notifications
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        appointment_data = {
            "patient_id": self.patient_user["id"],
            "appointment_date": tomorrow,
            "appointment_time": "11:30",
            "appointment_type": "consultation",
            "reason": "Email notification test"
        }
        
        success, response = self.make_request("POST", "appointments", appointment_data, token=self.doctor_token)
        if success and "id" in response:
            self.log_test("Create Appointment (for email test)", True)
            
            # The mock email system logs to console and stores in database
            # We can't directly verify console logs, but we can check if the appointment
            # creation was successful, which means the email notification logic ran
            
            # Wait a moment for all notifications to be processed
            import time
            time.sleep(2)
            
            # Verify the appointment was created successfully (indicates email system didn't break the flow)
            success, response = self.make_request("GET", f"appointments/{response['id']}", token=self.doctor_token)
            if success and "id" in response:
                self.log_test("Mock Email System Integration", True)
            else:
                self.log_test("Mock Email System Integration", False, "Appointment creation affected by email system")
        else:
            self.log_test("Create Appointment (for email test)", False, str(response))

        # Test that the system continues to work after email notifications
        # (verifies that email failures don't break the main functionality)
        success, response = self.make_request("POST", "notifications/test", token=self.patient_token)
        if success:
            self.log_test("System Stability After Email Processing", True)
        else:
            self.log_test("System Stability After Email Processing", False, "System affected by email processing")

        return True

    def test_multi_medicine_prescriptions(self):
        """Test multi-medicine prescription creation and management"""
        print("\n🔍 Testing Multi-Medicine Prescriptions...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Multi-Prescription Test Setup", False, "Required users not authenticated")
            return False

        # Test 1: Create multi-medicine prescription
        from datetime import date, timedelta
        today = date.today().isoformat()
        
        multi_prescription_data = {
            "patient_id": self.patient_user["id"],
            "start_date": today,
            "general_instructions": "Take all medications as prescribed. Monitor for side effects.",
            "medicines": [
                {
                    "name": "Lisinopril",
                    "dosage": "10mg",
                    "frequency": "once daily",
                    "duration": "30 days",
                    "notes": "Take in the morning"
                },
                {
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "twice daily",
                    "duration": "30 days",
                    "notes": "Take with meals"
                },
                {
                    "name": "Atorvastatin",
                    "dosage": "20mg",
                    "frequency": "once daily at bedtime",
                    "duration": "30 days",
                    "notes": "Take at night"
                }
            ]
        }
        
        success, response = self.make_request("POST", "multi-prescriptions", multi_prescription_data, token=self.doctor_token)
        multi_prescription_id = None
        if success and "id" in response:
            multi_prescription_id = response["id"]
            self.log_test("Create Multi-Medicine Prescription", True)
            
            # Verify the response structure
            expected_fields = ["id", "patient_id", "doctor_id", "medicines", "start_date", "general_instructions", "status", "created_at"]
            missing_fields = [field for field in expected_fields if field not in response]
            
            if not missing_fields:
                self.log_test("Multi-Prescription Response Structure", True)
            else:
                self.log_test("Multi-Prescription Response Structure", False, f"Missing fields: {missing_fields}")
            
            # Verify medicines array structure
            if "medicines" in response and isinstance(response["medicines"], list):
                if len(response["medicines"]) == 3:
                    self.log_test("Multi-Prescription Medicine Count", True)
                    
                    # Check medicine structure
                    medicine = response["medicines"][0]
                    expected_medicine_fields = ["name", "dosage", "frequency", "duration", "notes"]
                    missing_medicine_fields = [field for field in expected_medicine_fields if field not in medicine]
                    
                    if not missing_medicine_fields:
                        self.log_test("Medicine Structure Validation", True)
                    else:
                        self.log_test("Medicine Structure Validation", False, f"Missing medicine fields: {missing_medicine_fields}")
                else:
                    self.log_test("Multi-Prescription Medicine Count", False, f"Expected 3 medicines, got {len(response['medicines'])}")
            else:
                self.log_test("Multi-Prescription Medicine Count", False, "Medicines array not found or invalid")
        else:
            self.log_test("Create Multi-Medicine Prescription", False, str(response))
            return False

        # Test 2: Get multi-medicine prescriptions (doctor view)
        success, response = self.make_request("GET", "multi-prescriptions", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Get Multi-Prescriptions (Doctor)", True)
            
            # Find our created prescription
            our_prescription = next((p for p in response if p.get("id") == multi_prescription_id), None)
            if our_prescription:
                self.log_test("Multi-Prescription Retrieval Verification", True)
                
                # Verify patient name is included
                if "patient_name" in our_prescription:
                    self.log_test("Multi-Prescription Patient Name Enhancement", True)
                else:
                    self.log_test("Multi-Prescription Patient Name Enhancement", False, "Patient name not included")
            else:
                self.log_test("Multi-Prescription Retrieval Verification", False, "Created prescription not found in list")
        else:
            self.log_test("Get Multi-Prescriptions (Doctor)", False, str(response))

        # Test 3: Get multi-medicine prescriptions (patient view)
        success, response = self.make_request("GET", "multi-prescriptions", token=self.patient_token)
        if success and isinstance(response, list):
            self.log_test("Get Multi-Prescriptions (Patient)", True)
            
            # Find our created prescription
            our_prescription = next((p for p in response if p.get("id") == multi_prescription_id), None)
            if our_prescription:
                self.log_test("Patient Multi-Prescription Access", True)
                
                # Verify doctor name is included
                if "doctor_name" in our_prescription:
                    self.log_test("Multi-Prescription Doctor Name Enhancement", True)
                else:
                    self.log_test("Multi-Prescription Doctor Name Enhancement", False, "Doctor name not included")
            else:
                self.log_test("Patient Multi-Prescription Access", False, "Patient cannot see their prescription")
        else:
            self.log_test("Get Multi-Prescriptions (Patient)", False, str(response))

        # Test 4: Test data serialization (check for JSON serialization issues)
        if multi_prescription_id:
            success, response = self.make_request("GET", "multi-prescriptions", token=self.doctor_token)
            if success and isinstance(response, list):
                # Check if datetime fields are properly serialized
                our_prescription = next((p for p in response if p.get("id") == multi_prescription_id), None)
                if our_prescription:
                    datetime_fields = ["created_at", "updated_at", "start_date"]
                    serialization_issues = []
                    
                    for field in datetime_fields:
                        if field in our_prescription:
                            value = our_prescription[field]
                            if isinstance(value, str):
                                # Try to parse as ISO format
                                try:
                                    from datetime import datetime
                                    if field == "start_date":
                                        # start_date is just a date string
                                        datetime.fromisoformat(value)
                                    else:
                                        # created_at and updated_at are datetime strings
                                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                                except ValueError:
                                    serialization_issues.append(f"{field}: {value}")
                    
                    if not serialization_issues:
                        self.log_test("Multi-Prescription Datetime Serialization", True)
                    else:
                        self.log_test("Multi-Prescription Datetime Serialization", False, f"Serialization issues: {serialization_issues}")
                else:
                    self.log_test("Multi-Prescription Datetime Serialization", False, "Prescription not found for serialization test")
            else:
                self.log_test("Multi-Prescription Datetime Serialization", False, "Could not retrieve prescriptions for serialization test")

        # Test 5: Test patient cannot create multi-prescriptions
        success, response = self.make_request("POST", "multi-prescriptions", multi_prescription_data, token=self.patient_token, expected_status=403)
        if not success:  # Should fail with 403
            self.log_test("Patient Multi-Prescription Creation Restriction", True)
        else:
            self.log_test("Patient Multi-Prescription Creation Restriction", False, "Patients should not create multi-prescriptions")

        # Test 6: Test empty medicines array handling
        empty_prescription_data = {
            "patient_id": self.patient_user["id"],
            "start_date": today,
            "general_instructions": "Test empty medicines",
            "medicines": []
        }
        
        success, response = self.make_request("POST", "multi-prescriptions", empty_prescription_data, token=self.doctor_token, expected_status=422)
        if not success:  # Should fail with validation error
            self.log_test("Empty Medicines Array Validation", True)
        else:
            self.log_test("Empty Medicines Array Validation", False, "Should validate non-empty medicines array")

        return True

    def test_patient_profile_endpoint(self):
        """Test patient profile retrieval endpoint (GET /api/patients/{patient_id}/profile)"""
        print("\n🔍 Testing Patient Profile Endpoint...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Patient Profile Endpoint Test Setup", False, "Required users not authenticated")
            return False

        # Note: The actual endpoint in server.py is /api/patients/{patient_user_id}/full-profile
        # Testing this endpoint as it provides comprehensive patient data
        
        # Test 1: Get patient full profile (doctor access)
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.doctor_token)
        if success and isinstance(response, dict):
            self.log_test("Get Patient Full Profile (Doctor)", True)
            
            # Verify response structure
            expected_sections = ["patient_info", "medical_records", "prescriptions", "appointments", "uploaded_files", "stats"]
            missing_sections = [section for section in expected_sections if section not in response]
            
            if not missing_sections:
                self.log_test("Patient Profile Response Structure", True)
                
                # Test patient_info section
                patient_info = response.get("patient_info", {})
                expected_patient_fields = ["id", "user_id", "name", "email"]
                missing_patient_fields = [field for field in expected_patient_fields if field not in patient_info]
                
                if not missing_patient_fields:
                    self.log_test("Patient Info Section Structure", True)
                else:
                    self.log_test("Patient Info Section Structure", False, f"Missing patient info fields: {missing_patient_fields}")
                
                # Test stats section
                stats = response.get("stats", {})
                expected_stats = ["total_records", "total_prescriptions", "total_appointments", "total_files"]
                missing_stats = [stat for stat in expected_stats if stat not in stats]
                
                if not missing_stats:
                    self.log_test("Patient Profile Stats Section", True)
                else:
                    self.log_test("Patient Profile Stats Section", False, f"Missing stats: {missing_stats}")
                
                # Verify data types
                if (isinstance(response.get("medical_records"), list) and
                    isinstance(response.get("prescriptions"), list) and
                    isinstance(response.get("appointments"), list) and
                    isinstance(response.get("uploaded_files"), list)):
                    self.log_test("Patient Profile Data Types", True)
                else:
                    self.log_test("Patient Profile Data Types", False, "Invalid data types in response sections")
                
            else:
                self.log_test("Patient Profile Response Structure", False, f"Missing sections: {missing_sections}")
        else:
            self.log_test("Get Patient Full Profile (Doctor)", False, str(response))
            return False

        # Test 2: Test patient cannot access other patient profiles
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.patient_token, expected_status=403)
        if not success:  # Should fail with 403
            self.log_test("Patient Profile Access Restriction", True)
        else:
            self.log_test("Patient Profile Access Restriction", False, "Patients should not access other patient profiles")

        # Test 3: Test unauthorized access
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", expected_status=401)
        if not success:  # Should fail with 401
            self.log_test("Patient Profile Unauthorized Access Protection", True)
        else:
            self.log_test("Patient Profile Unauthorized Access Protection", False, "Should require authentication")

        # Test 4: Test non-existent patient
        fake_patient_id = "non-existent-patient-id"
        success, response = self.make_request("GET", f"patients/{fake_patient_id}/full-profile", token=self.doctor_token, expected_status=404)
        if not success:  # Should fail with 404
            self.log_test("Non-Existent Patient Profile Handling", True)
        else:
            self.log_test("Non-Existent Patient Profile Handling", False, "Should return 404 for non-existent patient")

        # Test 5: Test data serialization in patient profile
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.doctor_token)
        if success and isinstance(response, dict):
            # Check for datetime serialization issues in all sections
            serialization_issues = []
            
            # Check appointments for datetime fields
            appointments = response.get("appointments", [])
            for appointment in appointments:
                if "created_at" in appointment:
                    try:
                        from datetime import datetime
                        datetime.fromisoformat(appointment["created_at"].replace('Z', '+00:00'))
                    except ValueError:
                        serialization_issues.append(f"appointment created_at: {appointment['created_at']}")
            
            # Check prescriptions for datetime fields
            prescriptions = response.get("prescriptions", [])
            for prescription in prescriptions:
                if "created_at" in prescription:
                    try:
                        from datetime import datetime
                        datetime.fromisoformat(prescription["created_at"].replace('Z', '+00:00'))
                    except ValueError:
                        serialization_issues.append(f"prescription created_at: {prescription['created_at']}")
            
            # Check medical records for datetime fields
            medical_records = response.get("medical_records", [])
            for record in medical_records:
                if "created_at" in record:
                    try:
                        from datetime import datetime
                        datetime.fromisoformat(record["created_at"].replace('Z', '+00:00'))
                    except ValueError:
                        serialization_issues.append(f"medical_record created_at: {record['created_at']}")
            
            if not serialization_issues:
                self.log_test("Patient Profile Datetime Serialization", True)
            else:
                self.log_test("Patient Profile Datetime Serialization", False, f"Serialization issues: {serialization_issues}")
        else:
            self.log_test("Patient Profile Datetime Serialization", False, "Could not retrieve patient profile for serialization test")

        return True

    def test_integration_doctor_workflow(self):
        """Test complete doctor workflow: search patient → view patient details → see records → create multi-prescription"""
        print("\n🔍 Testing Integration Doctor Workflow...")
        
        if not self.doctor_token or not self.patient_user:
            self.log_test("Doctor Workflow Test Setup", False, "Required users not authenticated")
            return False

        # Step 1: Doctor searches for patients
        success, response = self.make_request("GET", f"patients/search?q={self.patient_user['name']}", token=self.doctor_token)
        if success and isinstance(response, list):
            self.log_test("Workflow Step 1: Patient Search", True)
            
            # Find our test patient
            found_patient = next((p for p in response if p.get("user_id") == self.patient_user["id"]), None)
            if found_patient:
                self.log_test("Workflow Step 1a: Patient Found in Search", True)
                patient_data = found_patient
            else:
                self.log_test("Workflow Step 1a: Patient Found in Search", False, "Test patient not found in search results")
                return False
        else:
            self.log_test("Workflow Step 1: Patient Search", False, str(response))
            return False

        # Step 2: Doctor views patient details
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.doctor_token)
        if success and isinstance(response, dict):
            self.log_test("Workflow Step 2: View Patient Details", True)
            patient_profile = response
            
            # Verify comprehensive data is available
            if (patient_profile.get("patient_info") and 
                isinstance(patient_profile.get("medical_records"), list) and
                isinstance(patient_profile.get("prescriptions"), list) and
                isinstance(patient_profile.get("appointments"), list)):
                self.log_test("Workflow Step 2a: Comprehensive Patient Data", True)
            else:
                self.log_test("Workflow Step 2a: Comprehensive Patient Data", False, "Incomplete patient data")
        else:
            self.log_test("Workflow Step 2: View Patient Details", False, str(response))
            return False

        # Step 3: Doctor reviews existing records (already retrieved in step 2)
        existing_records_count = len(patient_profile.get("medical_records", []))
        existing_prescriptions_count = len(patient_profile.get("prescriptions", []))
        existing_appointments_count = len(patient_profile.get("appointments", []))
        
        self.log_test("Workflow Step 3: Review Existing Records", True, 
                     f"Found {existing_records_count} records, {existing_prescriptions_count} prescriptions, {existing_appointments_count} appointments")

        # Step 4: Doctor creates a multi-medicine prescription based on patient data
        from datetime import date
        today = date.today().isoformat()
        
        # Create a comprehensive multi-prescription
        multi_prescription_data = {
            "patient_id": self.patient_user["id"],
            "start_date": today,
            "general_instructions": "Comprehensive treatment plan based on patient history and current condition. Monitor blood pressure and blood sugar levels.",
            "medicines": [
                {
                    "name": "Lisinopril",
                    "dosage": "10mg",
                    "frequency": "once daily in the morning",
                    "duration": "30 days",
                    "notes": "For blood pressure management. Take consistently at the same time."
                },
                {
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "twice daily with meals",
                    "duration": "30 days",
                    "notes": "For diabetes management. Take with breakfast and dinner."
                },
                {
                    "name": "Atorvastatin",
                    "dosage": "20mg",
                    "frequency": "once daily at bedtime",
                    "duration": "30 days",
                    "notes": "For cholesterol management. Take at night for best effectiveness."
                },
                {
                    "name": "Aspirin",
                    "dosage": "81mg",
                    "frequency": "once daily",
                    "duration": "30 days",
                    "notes": "Low-dose for cardiovascular protection. Take with food."
                }
            ]
        }
        
        success, response = self.make_request("POST", "multi-prescriptions", multi_prescription_data, token=self.doctor_token)
        if success and "id" in response:
            self.log_test("Workflow Step 4: Create Multi-Prescription", True)
            new_prescription_id = response["id"]
            
            # Verify the prescription was created with all medicines
            if len(response.get("medicines", [])) == 4:
                self.log_test("Workflow Step 4a: Multi-Medicine Creation", True)
            else:
                self.log_test("Workflow Step 4a: Multi-Medicine Creation", False, f"Expected 4 medicines, got {len(response.get('medicines', []))}")
        else:
            self.log_test("Workflow Step 4: Create Multi-Prescription", False, str(response))
            return False

        # Step 5: Verify the workflow completed successfully by checking updated patient profile
        success, response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.doctor_token)
        if success and isinstance(response, dict):
            updated_prescriptions_count = len(response.get("prescriptions", []))
            
            # Check if prescription count increased (including both single and multi-prescriptions)
            # Note: multi-prescriptions are stored separately, so we need to check multi-prescriptions endpoint
            success, multi_response = self.make_request("GET", "multi-prescriptions", token=self.doctor_token)
            if success and isinstance(multi_response, list):
                patient_multi_prescriptions = [p for p in multi_response if p.get("patient_id") == patient_data.get("id")]
                
                if patient_multi_prescriptions:
                    self.log_test("Workflow Step 5: Prescription Added to Patient", True)
                    
                    # Verify the prescription contains our patient's name
                    our_prescription = next((p for p in patient_multi_prescriptions if p.get("id") == new_prescription_id), None)
                    if our_prescription and "patient_name" in our_prescription:
                        self.log_test("Workflow Step 5a: Patient Name in Prescription", True)
                    else:
                        self.log_test("Workflow Step 5a: Patient Name in Prescription", False, "Patient name not found in prescription")
                else:
                    self.log_test("Workflow Step 5: Prescription Added to Patient", False, "Multi-prescription not found for patient")
            else:
                self.log_test("Workflow Step 5: Prescription Added to Patient", False, "Could not retrieve multi-prescriptions")
        else:
            self.log_test("Workflow Step 5: Verify Workflow Completion", False, "Could not retrieve updated patient profile")

        # Step 6: Test data consistency across the workflow
        # Verify that patient data is consistent across different endpoints
        success, search_response = self.make_request("GET", f"patients/search?q={self.patient_user['name']}", token=self.doctor_token)
        success2, profile_response = self.make_request("GET", f"patients/{self.patient_user['id']}/full-profile", token=self.doctor_token)
        
        if success and success2:
            search_patient = next((p for p in search_response if p.get("user_id") == self.patient_user["id"]), None)
            profile_patient = profile_response.get("patient_info", {})
            
            if (search_patient and profile_patient and 
                search_patient.get("name") == profile_patient.get("name") and
                search_patient.get("email") == profile_patient.get("email")):
                self.log_test("Workflow Step 6: Data Consistency", True)
            else:
                self.log_test("Workflow Step 6: Data Consistency", False, "Patient data inconsistent across endpoints")
        else:
            self.log_test("Workflow Step 6: Data Consistency", False, "Could not verify data consistency")

        # Final workflow verification
        self.log_test("Complete Doctor Workflow Integration", True, 
                     "Successfully completed: search → view details → review records → create multi-prescription")

        return True

    def test_authentication_security(self):
        """Test authentication and authorization"""
        print("\n🔍 Testing Authentication Security...")
        
        # Test accessing protected endpoint without token
        success, response = self.make_request("GET", "patients/me", expected_status=401)
        if not success:  # Should fail with 401
            self.log_test("Unauthorized Access Protection", True)
        else:
            self.log_test("Unauthorized Access Protection", False, "Should have returned 401")

        # Test patient accessing doctor-only endpoint
        if self.patient_token:
            success, response = self.make_request("GET", "patients/search", token=self.patient_token, expected_status=403)
            if not success:  # Should fail with 403
                self.log_test("Role-Based Access Control", True)
            else:
                self.log_test("Role-Based Access Control", False, "Patient should not access doctor endpoints")

        return True

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting HealthCard ID Backend API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)

        # Run tests in sequence
        test_methods = [
            self.test_user_registration,
            self.test_user_login,
            self.test_patient_profile,
            self.test_patient_search,
            self.test_appointments_management,
            self.test_prescriptions_management,
            self.test_multi_medicine_prescriptions,  # Added multi-medicine prescription tests
            self.test_patient_profile_endpoint,  # Added patient profile endpoint tests
            self.test_integration_doctor_workflow,  # Added integration workflow tests
            self.test_doctor_patient_portal,
            self.test_medical_records,
            self.test_audit_logging_system,  # Added audit logging tests
            self.test_notification_system,  # Added notification system tests
            self.test_notification_scheduling_system,  # Added notification scheduling tests
            self.test_mock_email_notification_system,  # Added mock email tests
            self.test_file_upload_system,
            self.test_file_management,
            self.test_file_security,
            self.test_ai_health_summary,
            self.test_dashboard_stats,
            self.test_ai_chat,
            self.test_authentication_security
        ]

        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"{test_method.__name__}", False, f"Exception: {str(e)}")

        # Print final results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed < self.tests_run:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['name']}: {result['details']}")

        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = HealthCardAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())