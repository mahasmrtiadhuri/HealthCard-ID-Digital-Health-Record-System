from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, ClassVar
from enum import Enum
import os
import logging
import uuid
import bcrypt
import jwt
import aiofiles
import shutil
from datetime import datetime, timedelta, date, time
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# File storage configuration
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MEDICAL_REPORTS_DIR = UPLOAD_DIR / "medical_reports"
PROFILE_IMAGES_DIR = UPLOAD_DIR / "profile_images"
MEDICAL_REPORTS_DIR.mkdir(exist_ok=True)
PROFILE_IMAGES_DIR.mkdir(exist_ok=True)

# File constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg", 
    "image/jpg",
    "image/png", 
    "image/gif"
}

# MongoDB connection - will be initialized in startup event
mongo_url = os.environ['MONGO_URL']
client = None
db = None

# Security
security = HTTPBearer()
JWT_SECRET = os.environ['JWT_SECRET']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"

class PrescriptionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"
    EXPIRED = "expired"

# Models
class UserRole(BaseModel):
    PATIENT: ClassVar[str] = "patient"
    DOCTOR: ClassVar[str] = "doctor"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    role: str  # "patient" or "doctor"
    password_hash: Optional[str] = None  # Include password_hash field
    specialization: Optional[str] = None  # For doctors
    license_number: Optional[str] = None  # For doctors
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

# Insurance Details Model
class InsuranceDetails(BaseModel):
    provider: Optional[str] = None
    policy_number: Optional[str] = None
    plan_type: Optional[str] = None  # "Basic", "Premium", "Family"
    coverage_amount: Optional[str] = None
    expiry_date: Optional[str] = None
    notes: Optional[str] = None

class Patient(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    allergies: Optional[List[str]] = []
    chronic_conditions: Optional[List[str]] = []
    current_medications: Optional[List[str]] = []
    emergency_contact: Optional[str] = None
    insurance_details: Optional[InsuranceDetails] = None

class PatientUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    emergency_contact: Optional[str] = None
    insurance_details: Optional[InsuranceDetails] = None

class MedicalRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    doctor_id: str
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_path: Optional[str] = None  # Local file path
    file_name: Optional[str] = None  # Original filename
    file_type: Optional[str] = None  # File MIME type
    record_type: str  # "report", "prescription", "notes"
    ai_summary: Optional[str] = None  # AI-generated summary
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MedicalRecordCreate(BaseModel):
    patient_id: str
    title: str
    description: Optional[str] = None
    record_type: str

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    doctor_id: str
    appointment_date: str  # Store as ISO string for MongoDB compatibility
    appointment_time: str  # Format: "09:30"
    duration_minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    appointment_type: str = "consultation"  # consultation, follow_up, check_up
    notes: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AppointmentCreate(BaseModel):
    patient_id: str
    appointment_date: str  # Accept as string
    appointment_time: str
    duration_minutes: int = 30
    appointment_type: str = "consultation"
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[str] = None  # Store as string
    appointment_time: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    reason: Optional[str] = None

class Prescription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    doctor_id: str
    medication_name: str
    dosage: str  # "10mg", "2 tablets"
    frequency: str  # "twice daily", "once before meals"
    start_date: str  # Store as ISO string for MongoDB compatibility
    end_date: Optional[str] = None  # Store as ISO string
    instructions: Optional[str] = None
    status: PrescriptionStatus = PrescriptionStatus.ACTIVE
    refills_remaining: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PrescriptionCreate(BaseModel):
    patient_id: str
    medication_name: str
    dosage: str
    frequency: str
    start_date: str  # Accept as string
    end_date: Optional[str] = None  # Accept as string
    instructions: Optional[str] = None
    refills_remaining: int = 0

class PrescriptionUpdate(BaseModel):
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    end_date: Optional[str] = None  # Store as string
    instructions: Optional[str] = None
    status: Optional[PrescriptionStatus] = None
    refills_remaining: Optional[int] = None

# Multi-Medicine Prescription Models
class Medicine(BaseModel):
    name: str
    dosage: str  # "10mg", "2 tablets"
    frequency: str  # "twice daily", "once before meals"
    duration: str  # "7 days", "2 weeks", "1 month"
    notes: Optional[str] = None

class MultiPrescription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    doctor_id: str
    medicines: List[Medicine]
    start_date: str  # Store as ISO string for MongoDB compatibility
    general_instructions: Optional[str] = None
    status: PrescriptionStatus = PrescriptionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MultiPrescriptionCreate(BaseModel):
    patient_id: str
    medicines: List[Medicine]
    start_date: str  # Accept as string
    general_instructions: Optional[str] = None


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    message: str
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # ID of user who made the change
    user_name: str  # Name of user who made the change
    user_role: str  # Role of user (doctor/patient)
    action: str  # Type of action (create, update, delete, view)
    resource_type: str  # Type of resource (patient_profile, medical_record, appointment, prescription, etc.)
    resource_id: str  # ID of the resource that was changed
    patient_id: Optional[str] = None  # ID of patient whose record was affected
    old_values: Optional[dict] = None  # Previous values (for updates)
    new_values: Optional[dict] = None  # New values (for updates/creates)
    description: str  # Human-readable description of the change
    ip_address: Optional[str] = None  # IP address of the user
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationType(str, Enum):
    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_BOOKED = "appointment_booked"
    APPOINTMENT_MODIFIED = "appointment_modified"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    PRESCRIPTION_UPDATE = "prescription_update"
    MEDICAL_RECORD_ADDED = "medical_record_added"
    SYSTEM_MESSAGE = "system_message"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # ID of user who will receive the notification
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    read: bool = False
    resource_type: Optional[str] = None  # appointment, prescription, medical_record, etc.
    resource_id: Optional[str] = None  # ID of related resource
    metadata: Optional[dict] = None  # Additional data (appointment time, doctor name, etc.)
    scheduled_for: Optional[datetime] = None  # When to send the notification
    sent_at: Optional[datetime] = None  # When the notification was actually sent
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    metadata: Optional[dict] = None
    scheduled_for: Optional[datetime] = None

class EmailNotificationTemplate(BaseModel):
    """Mock email notification structure - for future email integration"""
    to_email: str
    to_name: str
    subject: str
    template_type: NotificationType
    template_data: dict
    scheduled_for: Optional[datetime] = None

class FileUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: str
    file_size: int
    upload_type: str  # "medical_report", "profile_image"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Helper Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        # Convert ObjectId to string if it exists
        if "_id" in doc:
            doc.pop("_id")  # Remove MongoDB's _id field
        return {key: serialize_doc(value) for key, value in doc.items()}
    # Handle datetime objects
    if isinstance(doc, datetime):
        return doc.isoformat()
    if isinstance(doc, date):
        return doc.isoformat()
    if isinstance(doc, time):
        return doc.isoformat()
    return doc

async def create_audit_log(
    user: User,
    action: str,
    resource_type: str,
    resource_id: str,
    description: str,
    patient_id: str = None,
    old_values: dict = None,
    new_values: dict = None,
    request: Request = None
):
    """Create an audit log entry"""
    try:
        ip_address = None
        if request:
            # Try to get real IP from headers (in case of proxy/load balancer)
            ip_address = request.headers.get("X-Forwarded-For")
            if not ip_address:
                ip_address = request.headers.get("X-Real-IP")
            if not ip_address:
                ip_address = request.client.host if request.client else None
        
        audit_entry = AuditLog(
            user_id=user.id,
            user_name=user.name,
            user_role=user.role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            patient_id=patient_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip_address
        )
        
        audit_dict = serialize_doc(audit_entry.dict())
        await db.audit_logs.insert_one(audit_dict)
        
        # Log to console for development/debugging
        print(f"🔍 AUDIT: {user.name} ({user.role}) {action} {resource_type} {resource_id}: {description}")
        
    except Exception as e:
        # Don't let audit logging failures break the main operation
        print(f"⚠️ Audit logging failed: {str(e)}")

async def create_notification(
    user_id: str,
    notification_type: NotificationType,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    resource_type: str = None,
    resource_id: str = None,
    metadata: dict = None,
    scheduled_for: datetime = None
):
    """Create a notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            scheduled_for=scheduled_for
        )
        
        notification_dict = serialize_doc(notification.dict())
        await db.notifications.insert_one(notification_dict)
        
        # If not scheduled, mark as sent immediately
        if not scheduled_for:
            await db.notifications.update_one(
                {"id": notification.id},
                {"$set": {"sent_at": datetime.utcnow()}}
            )
        
        print(f"🔔 NOTIFICATION: Created {notification_type} for user {user_id}: {title}")
        return notification
        
    except Exception as e:
        print(f"⚠️ Notification creation failed: {str(e)}")
        return None

async def create_mock_email_notification(
    to_email: str,
    to_name: str,
    subject: str,
    template_type: NotificationType,
    template_data: dict,
    scheduled_for: datetime = None
):
    """Create a mock email notification (logs to console for now)"""
    try:
        email_notification = EmailNotificationTemplate(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            template_type=template_type,
            template_data=template_data,
            scheduled_for=scheduled_for
        )
        
        # For now, just log the email notification
        scheduled_text = f" (scheduled for {scheduled_for})" if scheduled_for else ""
        print(f"📧 MOCK EMAIL: To {to_name} <{to_email}> - {subject}{scheduled_text}")
        print(f"   Template: {template_type}")
        print(f"   Data: {template_data}")
        
        # Store in database for future email integration
        email_dict = serialize_doc(email_notification.dict())
        await db.email_notifications.insert_one(email_dict)
        
        return email_notification
        
    except Exception as e:
        print(f"⚠️ Mock email creation failed: {str(e)}")
        return None

async def schedule_appointment_reminder(appointment_id: str, appointment_date: str, appointment_time: str):
    """Schedule an appointment reminder 24 hours before the appointment"""
    try:
        # Parse appointment datetime
        appointment_datetime = datetime.fromisoformat(f"{appointment_date} {appointment_time}")
        reminder_time = appointment_datetime - timedelta(hours=24)
        
        # Only schedule if reminder time is in the future
        if reminder_time > datetime.utcnow():
            # Get appointment details
            appointment = await db.appointments.find_one({"id": appointment_id})
            if not appointment:
                return
            
            appointment = serialize_doc(appointment)
            
            # Get patient and doctor info
            patient = await db.patients.find_one({"id": appointment["patient_id"]})
            patient_user = await db.users.find_one({"id": patient["user_id"]}) if patient else None
            doctor = await db.users.find_one({"id": appointment["doctor_id"]})
            
            if patient_user and doctor:
                patient_user = serialize_doc(patient_user)
                doctor = serialize_doc(doctor)
                
                # Create notification for patient
                await create_notification(
                    user_id=patient_user["id"],
                    notification_type=NotificationType.APPOINTMENT_REMINDER,
                    title="Appointment Reminder",
                    message=f"You have an appointment with Dr. {doctor['name']} tomorrow at {appointment_time}",
                    priority=NotificationPriority.HIGH,
                    resource_type="appointment",
                    resource_id=appointment_id,
                    metadata={
                        "appointment_date": appointment_date,
                        "appointment_time": appointment_time,
                        "doctor_name": doctor["name"],
                        "appointment_type": appointment.get("appointment_type", "consultation")
                    },
                    scheduled_for=reminder_time
                )
                
                # Create mock email reminder
                await create_mock_email_notification(
                    to_email=patient_user["email"],
                    to_name=patient_user["name"],
                    subject=f"Appointment Reminder - Tomorrow at {appointment_time}",
                    template_type=NotificationType.APPOINTMENT_REMINDER,
                    template_data={
                        "patient_name": patient_user["name"],
                        "doctor_name": doctor["name"],
                        "appointment_date": appointment_date,
                        "appointment_time": appointment_time,
                        "appointment_type": appointment.get("appointment_type", "consultation"),
                        "reason": appointment.get("reason", "")
                    },
                    scheduled_for=reminder_time
                )
                
                print(f"⏰ Appointment reminder scheduled for {reminder_time}")
            
    except Exception as e:
        print(f"⚠️ Failed to schedule appointment reminder: {str(e)}")

def validate_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded file"""
    # Check file size
    if hasattr(file.file, 'seek'):
        file.file.seek(0, 2)  # Move to end of file
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        if size > MAX_FILE_SIZE:
            return False, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File extension {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"File type {file.content_type} not allowed"
    
    return True, "Valid"

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    file_ext = Path(original_filename).suffix.lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_ext}"

async def save_file(file: UploadFile, upload_type: str) -> tuple[str, str]:
    """Save uploaded file and return (file_path, stored_filename)"""
    stored_filename = generate_unique_filename(file.filename)
    
    if upload_type == "medical_report":
        file_path = MEDICAL_REPORTS_DIR / stored_filename
    elif upload_type == "profile_image":
        file_path = PROFILE_IMAGES_DIR / stored_filename
    else:
        raise ValueError(f"Invalid upload_type: {upload_type}")
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return str(file_path), stored_filename

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        user = serialize_doc(user)
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_patient_by_user_id(user_id: str):
    """Get patient record by user ID"""
    patient = await db.patients.find_one({"user_id": user_id})
    return serialize_doc(patient) if patient else None

async def get_doctor_patients(doctor_id: str):
    """Get all patients associated with a doctor (through appointments or records)"""
    # Get unique patient IDs from appointments and medical records
    appointment_patients = await db.appointments.distinct("patient_id", {"doctor_id": doctor_id})
    record_patients = await db.medical_records.distinct("patient_id", {"doctor_id": doctor_id})
    
    # Combine and deduplicate
    all_patient_ids = list(set(appointment_patients + record_patients))
    
    # Get patient user IDs
    patients = await db.patients.find({"id": {"$in": all_patient_ids}}).to_list(100)
    return serialize_doc(patients)

# Authentication Routes
@api_router.post("/auth/register")
async def register(user_create: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_create.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_create.password)
    user_dict = user_create.dict()
    user_dict.pop("password")
    user_dict["password_hash"] = hashed_password
    user_obj = User(**user_dict)
    
    user_dict = serialize_doc(user_obj.dict())
    await db.users.insert_one(user_dict)
    
    # Create patient profile if role is patient
    if user_create.role == "patient":
        patient = Patient(user_id=user_obj.id)
        patient_dict = serialize_doc(patient.dict())
        await db.patients.insert_one(patient_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_obj.id, "role": user_obj.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_obj.id,
            "email": user_obj.email,
            "name": user_obj.name,
            "role": user_obj.role,
            "specialization": user_obj.specialization,
            "phone": user_obj.phone
        }
    }

@api_router.post("/auth/login")
async def login(user_login: UserLogin):
    user = await db.users.find_one({"email": user_login.email})
    if not user or not verify_password(user_login.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Serialize the user document
    user = serialize_doc(user)
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "specialization": user.get("specialization"),
            "phone": user.get("phone")
        }
    }

# Patient Routes
@api_router.get("/patients/me", response_model=Patient)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = await db.patients.find_one({"user_id": current_user.id})
    if not patient:
        # Create patient profile if doesn't exist
        patient = Patient(user_id=current_user.id)
        patient_dict = serialize_doc(patient.dict())
        await db.patients.insert_one(patient_dict)
        return patient
    
    patient = serialize_doc(patient)
    return Patient(**patient)

@api_router.put("/patients/me", response_model=Patient)
async def update_my_profile(patient_update: PatientUpdate, current_user: User = Depends(get_current_user), request: Request = None):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get current patient data for audit logging
    old_patient = await db.patients.find_one({"user_id": current_user.id})
    old_patient = serialize_doc(old_patient) if old_patient else {}
    
    update_dict = {k: v for k, v in patient_update.dict().items() if v is not None}
    
    await db.patients.update_one(
        {"user_id": current_user.id},
        {"$set": update_dict}
    )
    
    # Get updated patient data
    patient = await db.patients.find_one({"user_id": current_user.id})
    patient = serialize_doc(patient)
    
    # Create audit log for profile update
    if update_dict:  # Only log if there were actual changes
        await create_audit_log(
            user=current_user,
            action="update",
            resource_type="patient_profile",
            resource_id=patient["id"],
            patient_id=patient["id"],
            old_values=old_patient,
            new_values=update_dict,
            description=f"Patient {current_user.name} updated their profile with fields: {', '.join(update_dict.keys())}",
            request=request
        )
    
    return Patient(**patient)

@api_router.get("/patients/search")
async def search_patients(q: str = "", current_user: User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Search users with patient role
    query = {"role": "patient"}
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"email": {"$regex": q, "$options": "i"}}
        ]
    
    users = await db.users.find(query).to_list(50)
    users = serialize_doc(users)
    patients_data = []
    
    for user in users:
        patient = await db.patients.find_one({"user_id": user["id"]})
        if patient:
            patient = serialize_doc(patient)
            patients_data.append({
                "id": patient["id"],
                "user_id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user.get("phone"),
                **{k: v for k, v in patient.items() if k not in ["id", "user_id"]}
            })
    
    return patients_data

@api_router.get("/patients/{patient_user_id}/full-profile")
async def get_patient_full_profile(patient_user_id: str, current_user: User = Depends(get_current_user)):
    """Get complete patient profile including records, prescriptions, and appointments"""
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get patient basic info
    patient = await db.patients.find_one({"user_id": patient_user_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    user = await db.users.find_one({"id": patient_user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    patient = serialize_doc(patient)
    user = serialize_doc(user)
    
    # Get medical records
    records = await db.medical_records.find({"patient_id": patient["id"]}).sort("created_at", -1).to_list(50)
    records = serialize_doc(records)
    
    # Get prescriptions
    prescriptions = await db.prescriptions.find({"patient_id": patient["id"]}).sort("created_at", -1).to_list(50)
    prescriptions = serialize_doc(prescriptions)
    
    # Get appointments
    appointments = await db.appointments.find({"patient_id": patient["id"]}).sort("appointment_date", -1).to_list(50)
    appointments = serialize_doc(appointments)
    
    # Get uploaded files
    files = await db.file_uploads.find({"user_id": patient_user_id}).sort("created_at", -1).to_list(20)
    files = serialize_doc(files)
    
    return {
        "patient_info": {
            "id": patient["id"],
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "phone": user.get("phone"),
            **{k: v for k, v in patient.items() if k not in ["id", "user_id"]}
        },
        "medical_records": records,
        "prescriptions": prescriptions,
        "appointments": appointments,
        "uploaded_files": files,
        "stats": {
            "total_records": len(records),
            "total_prescriptions": len(prescriptions),
            "total_appointments": len(appointments),
            "total_files": len(files)
        }
    }

# Appointment Routes
@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(
    appointment: AppointmentCreate, 
    current_user: User = Depends(get_current_user), 
    request: Request = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create appointments")
    
    # Verify patient exists
    patient = await db.patients.find_one({"user_id": appointment.patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = serialize_doc(patient)
    appointment_data = appointment.dict()
    appointment_data["doctor_id"] = current_user.id
    appointment_data["patient_id"] = patient["id"]  # Use patient record ID, not user ID
    appointment_obj = Appointment(**appointment_data)
    
    appointment_dict = serialize_doc(appointment_obj.dict())
    await db.appointments.insert_one(appointment_dict)
    
    # Get patient user info for audit log and notifications
    patient_user = await db.users.find_one({"id": appointment.patient_id})
    patient_user = serialize_doc(patient_user) if patient_user else {}
    patient_name = patient_user.get("name", "Unknown Patient")
    
    # Create audit log for appointment creation
    await create_audit_log(
        user=current_user,
        action="create",
        resource_type="appointment",
        resource_id=appointment_obj.id,
        patient_id=patient["id"],
        new_values=appointment_dict,
        description=f"Dr. {current_user.name} scheduled a {appointment.appointment_type} appointment with {patient_name} on {appointment.appointment_date}",
        request=request
    )
    
    # Create immediate notification for patient about new appointment
    await create_notification(
        user_id=patient_user["id"],
        notification_type=NotificationType.APPOINTMENT_BOOKED,
        title="New Appointment Scheduled",
        message=f"Dr. {current_user.name} has scheduled a {appointment.appointment_type} appointment for {appointment.appointment_date} at {appointment.appointment_time}",
        priority=NotificationPriority.HIGH,
        resource_type="appointment",
        resource_id=appointment_obj.id,
        metadata={
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "doctor_name": current_user.name,
            "appointment_type": appointment.appointment_type
        }
    )
    
    # Create mock email confirmation
    await create_mock_email_notification(
        to_email=patient_user["email"],
        to_name=patient_name,
        subject=f"Appointment Confirmed - {appointment.appointment_date} at {appointment.appointment_time}",
        template_type=NotificationType.APPOINTMENT_BOOKED,
        template_data={
            "patient_name": patient_name,
            "doctor_name": current_user.name,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "appointment_type": appointment.appointment_type,
            "reason": appointment.reason or ""
        }
    )
    
    # Schedule appointment reminder (24 hours before)
    background_tasks.add_task(
        schedule_appointment_reminder,
        appointment_obj.id,
        appointment.appointment_date,
        appointment.appointment_time
    )
    
    return appointment_obj

@api_router.get("/appointments")
async def get_appointments(current_user: User = Depends(get_current_user)):
    if current_user.role == "patient":
        # Get patient's appointments
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient:
            return []
        
        patient = serialize_doc(patient)
        appointments = await db.appointments.find({"patient_id": patient["id"]}).sort("appointment_date", -1).to_list(100)
    else:
        # Get doctor's appointments
        appointments = await db.appointments.find({"doctor_id": current_user.id}).sort("appointment_date", -1).to_list(100)
    
    appointments = serialize_doc(appointments)
    
    # Enhance appointments with patient/doctor names
    for appointment in appointments:
        if current_user.role == "doctor":
            # Add patient name
            patient = await db.patients.find_one({"id": appointment["patient_id"]})
            if patient:
                patient = serialize_doc(patient)
                user = await db.users.find_one({"id": patient["user_id"]})
                if user:
                    user = serialize_doc(user)
                    appointment["patient_name"] = user["name"]
        else:
            # Add doctor name
            doctor = await db.users.find_one({"id": appointment["doctor_id"]})
            if doctor:
                doctor = serialize_doc(doctor)
                appointment["doctor_name"] = doctor["name"]
                appointment["doctor_specialization"] = doctor.get("specialization")
    
    return [Appointment(**appointment) for appointment in appointments]

@api_router.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: str, current_user: User = Depends(get_current_user)):
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment = serialize_doc(appointment)
    
    # Check access permissions
    if current_user.role == "patient":
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient or appointment["patient_id"] != patient["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "doctor":
        if appointment["doctor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return Appointment(**appointment)

@api_router.put("/appointments/{appointment_id}")
async def update_appointment(appointment_id: str, appointment_update: AppointmentUpdate, current_user: User = Depends(get_current_user)):
    # Check if appointment exists and user has access
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment = serialize_doc(appointment)
    
    # Check permissions
    can_update = False
    if current_user.role == "doctor" and appointment["doctor_id"] == current_user.id:
        can_update = True
    elif current_user.role == "patient":
        patient = await db.patients.find_one({"user_id": current_user.id})
        if patient and appointment["patient_id"] == patient["id"]:
            # Patients can only update status (e.g., cancel)
            if appointment_update.status == AppointmentStatus.CANCELED:
                can_update = True
    
    if not can_update:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_dict = {k: v for k, v in appointment_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": update_dict}
    )
    
    updated_appointment = await db.appointments.find_one({"id": appointment_id})
    updated_appointment = serialize_doc(updated_appointment)
    return Appointment(**updated_appointment)

# Prescription Routes
@api_router.post("/prescriptions", response_model=Prescription)
async def create_prescription(prescription: PrescriptionCreate, current_user: User = Depends(get_current_user), request: Request = None):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create prescriptions")
    
    # Verify patient exists
    patient = await db.patients.find_one({"user_id": prescription.patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = serialize_doc(patient)
    prescription_data = prescription.dict()
    prescription_data["doctor_id"] = current_user.id
    prescription_data["patient_id"] = patient["id"]  # Use patient record ID, not user ID
    prescription_obj = Prescription(**prescription_data)
    
    prescription_dict = serialize_doc(prescription_obj.dict())
    await db.prescriptions.insert_one(prescription_dict)
    
    # Get patient user info for audit log
    patient_user = await db.users.find_one({"id": prescription.patient_id})
    patient_user = serialize_doc(patient_user) if patient_user else {}
    patient_name = patient_user.get("name", "Unknown Patient")
    
    # Create audit log for prescription creation
    await create_audit_log(
        user=current_user,
        action="create",
        resource_type="prescription",
        resource_id=prescription_obj.id,
        patient_id=patient["id"],
        new_values=prescription_dict,
        description=f"Dr. {current_user.name} prescribed {prescription.medication_name} ({prescription.dosage}) to {patient_name}",
        request=request
    )
    
    return prescription_obj

@api_router.get("/prescriptions")
async def get_prescriptions(current_user: User = Depends(get_current_user)):
    if current_user.role == "patient":
        # Get patient's prescriptions
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient:
            return []
        
        patient = serialize_doc(patient)
        prescriptions = await db.prescriptions.find({"patient_id": patient["id"]}).sort("created_at", -1).to_list(100)
    else:
        # Get doctor's prescriptions
        prescriptions = await db.prescriptions.find({"doctor_id": current_user.id}).sort("created_at", -1).to_list(100)
    
    prescriptions = serialize_doc(prescriptions)
    
    # Enhance prescriptions with patient/doctor names
    for prescription in prescriptions:
        if current_user.role == "doctor":
            # Add patient name
            patient = await db.patients.find_one({"id": prescription["patient_id"]})
            if patient:
                patient = serialize_doc(patient)
                user = await db.users.find_one({"id": patient["user_id"]})
                if user:
                    user = serialize_doc(user)
                    prescription["patient_name"] = user["name"]
        else:
            # Add doctor name
            doctor = await db.users.find_one({"id": prescription["doctor_id"]})
            if doctor:
                doctor = serialize_doc(doctor)
                prescription["doctor_name"] = doctor["name"]
                prescription["doctor_specialization"] = doctor.get("specialization")
    
    return [Prescription(**prescription) for prescription in prescriptions]

@api_router.put("/prescriptions/{prescription_id}")
async def update_prescription(prescription_id: str, prescription_update: PrescriptionUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can update prescriptions")
    
    # Check if prescription exists and belongs to current doctor
    prescription = await db.prescriptions.find_one({"id": prescription_id, "doctor_id": current_user.id})
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    update_dict = {k: v for k, v in prescription_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    await db.prescriptions.update_one(
        {"id": prescription_id},
        {"$set": update_dict}
    )
    
    updated_prescription = await db.prescriptions.find_one({"id": prescription_id})
    updated_prescription = serialize_doc(updated_prescription)
    return Prescription(**updated_prescription)

# Multi-Medicine Prescription Routes
@api_router.post("/multi-prescriptions", response_model=MultiPrescription)
async def create_multi_prescription(
    prescription: MultiPrescriptionCreate, 
    current_user: User = Depends(get_current_user), 
    request: Request = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a prescription with multiple medicines"""
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create prescriptions")
    
    # Verify patient exists
    patient = await db.patients.find_one({"user_id": prescription.patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = serialize_doc(patient)
    prescription_data = prescription.dict()
    prescription_data["doctor_id"] = current_user.id
    prescription_data["patient_id"] = patient["id"]  # Use patient record ID, not user ID
    prescription_obj = MultiPrescription(**prescription_data)
    
    prescription_dict = serialize_doc(prescription_obj.dict())
    await db.multi_prescriptions.insert_one(prescription_dict)
    
    # Get patient user info for audit log and notifications
    patient_user = await db.users.find_one({"id": prescription.patient_id})
    patient_user = serialize_doc(patient_user) if patient_user else {}
    patient_name = patient_user.get("name", "Unknown Patient")
    
    # Create audit log
    medicine_names = [med.name for med in prescription.medicines]
    await create_audit_log(
        user=current_user,
        action="create",
        resource_type="multi_prescription",
        resource_id=prescription_obj.id,
        patient_id=patient["id"],
        new_values=prescription_dict,
        description=f"Dr. {current_user.name} prescribed {len(prescription.medicines)} medicines to {patient_name}: {', '.join(medicine_names)}",
        request=request
    )
    
    # Create notification for patient
    await create_notification(
        user_id=patient_user["id"],
        notification_type=NotificationType.PRESCRIPTION_UPDATE,
        title="New Prescription",
        message=f"Dr. {current_user.name} has prescribed {len(prescription.medicines)} new medicines for you",
        priority=NotificationPriority.HIGH,
        resource_type="multi_prescription",
        resource_id=prescription_obj.id,
        metadata={
            "doctor_name": current_user.name,
            "medicine_count": len(prescription.medicines),
            "medicine_names": medicine_names
        }
    )
    
    return prescription_obj

@api_router.get("/multi-prescriptions")
async def get_multi_prescriptions(current_user: User = Depends(get_current_user)):
    """Get multi-medicine prescriptions"""
    if current_user.role == "patient":
        # Get patient's multi-prescriptions
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient:
            return []
        
        patient = serialize_doc(patient)
        prescriptions = await db.multi_prescriptions.find({"patient_id": patient["id"]}).sort("created_at", -1).to_list(100)
    else:
        # Get doctor's multi-prescriptions
        prescriptions = await db.multi_prescriptions.find({"doctor_id": current_user.id}).sort("created_at", -1).to_list(100)
    
    prescriptions = serialize_doc(prescriptions)
    
    # Enhance prescriptions with patient/doctor names
    for prescription in prescriptions:
        if current_user.role == "doctor":
            # Add patient name
            patient = await db.patients.find_one({"id": prescription["patient_id"]})
            if patient:
                patient = serialize_doc(patient)
                user = await db.users.find_one({"id": patient["user_id"]})
                if user:
                    user = serialize_doc(user)
                    prescription["patient_name"] = user["name"]
        else:
            # Add doctor name
            doctor = await db.users.find_one({"id": prescription["doctor_id"]})
            if doctor:
                doctor = serialize_doc(doctor)
                prescription["doctor_name"] = doctor["name"]
                prescription["doctor_specialization"] = doctor.get("specialization")
    
    return [MultiPrescription(**prescription) for prescription in prescriptions]

# Audit Logs Routes
@api_router.get("/audit-logs")
async def get_audit_logs(
    patient_id: str = None,
    resource_type: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get audit logs - doctors can see logs for their patients, patients can see their own logs"""
    query = {}
    
    if current_user.role == "patient":
        # Patients can only see logs related to their own records
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient:
            return []
        patient = serialize_doc(patient)
        query["patient_id"] = patient["id"]
    elif current_user.role == "doctor":
        # Doctors can see logs for specific patients or all their interactions
        if patient_id:
            # Verify doctor has access to this patient
            patient = await db.patients.find_one({"id": patient_id})
            if patient:
                query["patient_id"] = patient_id
            else:
                raise HTTPException(status_code=404, detail="Patient not found")
        else:
            # Show logs where doctor was involved
            query["user_id"] = current_user.id
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Filter by resource type if provided
    if resource_type:
        query["resource_type"] = resource_type
    
    # Get audit logs
    audit_logs = await db.audit_logs.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    audit_logs = serialize_doc(audit_logs)
    
    return audit_logs

@api_router.get("/audit-logs/patient/{patient_id}")
async def get_patient_audit_logs(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all audit logs for a specific patient (doctors only)"""
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can view patient audit logs")
    
    # Verify patient exists
    patient = await db.patients.find_one({"id": patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all audit logs for this patient
    audit_logs = await db.audit_logs.find({"patient_id": patient_id}).sort("created_at", -1).to_list(100)
    audit_logs = serialize_doc(audit_logs)
    
    return {
        "patient_id": patient_id,
        "audit_logs": audit_logs,
        "total_logs": len(audit_logs)
    }

# Notification Routes
@api_router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get notifications for the current user"""
    query = {"user_id": current_user.id}
    
    if unread_only:
        query["read"] = False
    
    # Only show notifications that are due to be sent or already sent
    query["$or"] = [
        {"sent_at": {"$exists": True}},
        {"scheduled_for": {"$lte": datetime.utcnow()}}
    ]
    
    notifications = await db.notifications.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    notifications = serialize_doc(notifications)
    
    return notifications

@api_router.get("/notifications/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_user)):
    """Get count of unread notifications"""
    count = await db.notifications.count_documents({
        "user_id": current_user.id,
        "read": False,
        "$or": [
            {"sent_at": {"$exists": True}},
            {"scheduled_for": {"$lte": datetime.utcnow()}}
        ]
    })
    
    return {"unread_count": count}

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user.id},
        {"$set": {"read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True}

@api_router.put("/notifications/mark-all-read")
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    """Mark all notifications as read for the current user"""
    result = await db.notifications.update_many(
        {"user_id": current_user.id, "read": False},
        {"$set": {"read": True}}
    )
    
    return {"success": True, "updated_count": result.modified_count}

@api_router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    result = await db.notifications.delete_one({
        "id": notification_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True}

@api_router.post("/notifications/test")
async def create_test_notification(current_user: User = Depends(get_current_user)):
    """Create a test notification (for development)"""
    await create_notification(
        user_id=current_user.id,
        notification_type=NotificationType.SYSTEM_MESSAGE,
        title="Test Notification",
        message="This is a test notification to verify the system is working.",
        priority=NotificationPriority.MEDIUM
    )
    
    return {"success": True, "message": "Test notification created"}

# Background Tasks for Notifications
async def process_scheduled_notifications():
    """Process notifications that are scheduled to be sent"""
    try:
        # Find notifications that should be sent now
        current_time = datetime.utcnow()
        scheduled_notifications = await db.notifications.find({
            "scheduled_for": {"$lte": current_time},
            "sent_at": {"$exists": False}
        }).to_list(100)
        
        for notification in scheduled_notifications:
            # Mark as sent
            await db.notifications.update_one(
                {"id": notification["id"]},
                {"$set": {"sent_at": current_time}}
            )
            print(f"🔔 Sent scheduled notification: {notification['title']} to user {notification['user_id']}")
    
    except Exception as e:
        print(f"⚠️ Failed to process scheduled notifications: {str(e)}")

# File Upload Routes (Enhanced)
@api_router.post("/upload/medical-report")
async def upload_medical_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Upload medical report (PDFs/Images)"""
    # Validate file
    is_valid, message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    try:
        # Save file
        file_path, stored_filename = await save_file(file, "medical_report")
        
        # Store metadata in database
        file_upload = FileUpload(
            user_id=current_user.id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file.content_type,
            file_size=os.path.getsize(file_path),
            upload_type="medical_report"
        )
        
        file_upload_dict = serialize_doc(file_upload.dict())
        await db.file_uploads.insert_one(file_upload_dict)
        
        # Get patient ID for audit logging (if user is a patient)
        patient_id = None
        if current_user.role == "patient":
            patient = await db.patients.find_one({"user_id": current_user.id})
            if patient:
                patient = serialize_doc(patient)
                patient_id = patient["id"]
        
        # Create audit log for file upload
        await create_audit_log(
            user=current_user,
            action="create",
            resource_type="file_upload",
            resource_id=file_upload.id,
            patient_id=patient_id,
            new_values={"filename": file.filename, "file_type": file.content_type, "file_size": file_upload.file_size},
            description=f"{current_user.name} uploaded medical report: {file.filename}",
            request=request
        )
        
        # Generate AI summary for the uploaded file
        try:
            ai_summary = await generate_file_summary(file.filename, file.content_type, current_user.id)
            # Update file record with AI summary
            await db.file_uploads.update_one(
                {"id": file_upload.id},
                {"$set": {"ai_summary": ai_summary}}
            )
        except Exception as e:
            logging.warning(f"Failed to generate AI summary for file: {str(e)}")
        
        return {
            "file_id": file_upload.id,
            "filename": file.filename,
            "file_type": file.content_type,
            "file_size": file_upload.file_size,
            "upload_url": f"/api/files/{file_upload.id}"
        }
        
    except Exception as e:
        logging.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@api_router.post("/upload/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload profile image (Images only)"""
    # Validate file (only images for profile)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed for profile pictures")
    
    is_valid, message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    try:
        # Save file
        file_path, stored_filename = await save_file(file, "profile_image")
        
        # Store metadata in database
        file_upload = FileUpload(
            user_id=current_user.id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file.content_type,
            file_size=os.path.getsize(file_path),
            upload_type="profile_image"
        )
        
        file_upload_dict = serialize_doc(file_upload.dict())
        await db.file_uploads.insert_one(file_upload_dict)
        
        return {
            "file_id": file_upload.id,
            "filename": file.filename,
            "file_type": file.content_type,
            "file_size": file_upload.file_size,
            "upload_url": f"/api/files/{file_upload.id}"
        }
        
    except Exception as e:
        logging.error(f"Profile image upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload profile image")

@api_router.get("/files/{file_id}")
async def get_file(file_id: str, current_user: User = Depends(get_current_user)):
    """Download/view uploaded file with authentication"""
    # Get file metadata
    file_record = await db.file_uploads.find_one({"id": file_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_record = serialize_doc(file_record)
    
    # Check permissions
    if current_user.role == "patient":
        # Patients can only access their own files
        if file_record["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == "doctor":
        # Doctors can access files uploaded by their patients or themselves
        # For now, allowing doctors to access any file (could be refined based on doctor-patient relationships)
        pass
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists on disk
    file_path = Path(file_record["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=file_path,
        filename=file_record["original_filename"],
        media_type=file_record["file_type"]
    )

@api_router.get("/files")
async def list_user_files(current_user: User = Depends(get_current_user)):
    """List all files uploaded by current user"""
    files = await db.file_uploads.find({"user_id": current_user.id}).to_list(100)
    files = serialize_doc(files)
    
    return [
        {
            "file_id": f["id"],
            "original_filename": f["original_filename"],
            "file_type": f["file_type"],
            "file_size": f["file_size"],
            "upload_type": f["upload_type"],
            "ai_summary": f.get("ai_summary"),
            "created_at": f["created_at"],
            "download_url": f"/api/files/{f['id']}"
        }
        for f in files
    ]

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str, current_user: User = Depends(get_current_user)):
    """Delete uploaded file"""
    # Get file metadata
    file_record = await db.file_uploads.find_one({"id": file_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_record = serialize_doc(file_record)
    
    # Check permissions (only owner can delete)
    if file_record["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Delete file from disk
        file_path = Path(file_record["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # Delete record from database
        await db.file_uploads.delete_one({"id": file_id})
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logging.error(f"File deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete file")

# Medical Records Routes (Enhanced)
@api_router.post("/medical-records", response_model=MedicalRecord)
async def create_medical_record(record: MedicalRecordCreate, current_user: User = Depends(get_current_user), request: Request = None):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify patient exists
    patient = await db.patients.find_one({"user_id": record.patient_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = serialize_doc(patient)
    record_data = record.dict()
    record_data["doctor_id"] = current_user.id
    record_data["patient_id"] = patient["id"]  # Use patient record ID, not user ID
    record_obj = MedicalRecord(**record_data)
    
    record_dict = serialize_doc(record_obj.dict())
    await db.medical_records.insert_one(record_dict)
    
    # Create audit log for medical record creation
    await create_audit_log(
        user=current_user,
        action="create",
        resource_type="medical_record",
        resource_id=record_obj.id,
        patient_id=patient["id"],
        new_values=record_dict,
        description=f"Dr. {current_user.name} created a new {record.record_type} record: {record.title}",
        request=request
    )
    
    return record_obj

@api_router.put("/medical-records/{record_id}/attach-file")
async def attach_file_to_record(
    record_id: str,
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Attach an uploaded file to a medical record"""
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify record exists and belongs to current doctor
    record = await db.medical_records.find_one({"id": record_id, "doctor_id": current_user.id})
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    # Verify file exists
    file_record = await db.file_uploads.find_one({"id": file_id})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_record = serialize_doc(file_record)
    
    # Update medical record with file information
    await db.medical_records.update_one(
        {"id": record_id},
        {
            "$set": {
                "file_url": f"/api/files/{file_id}",
                "file_path": file_record["file_path"],
                "file_name": file_record["original_filename"],
                "file_type": file_record["file_type"]
            }
        }
    )
    
    return {"message": "File attached to medical record successfully"}

@api_router.get("/medical-records")
async def get_medical_records(current_user: User = Depends(get_current_user)):
    if current_user.role == "patient":
        # Get records for this patient
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient:
            return []
        patient = serialize_doc(patient)
        records = await db.medical_records.find({"patient_id": patient["id"]}).sort("created_at", -1).to_list(100)
    else:
        # Doctor can see all their created records
        records = await db.medical_records.find({"doctor_id": current_user.id}).sort("created_at", -1).to_list(100)
    
    records = serialize_doc(records)
    
    # Enhance records with patient/doctor names
    for record in records:
        if current_user.role == "doctor":
            # Add patient name
            patient = await db.patients.find_one({"id": record["patient_id"]})
            if patient:
                patient = serialize_doc(patient)
                user = await db.users.find_one({"id": patient["user_id"]})
                if user:
                    user = serialize_doc(user)
                    record["patient_name"] = user["name"]
        else:
            # Add doctor name
            doctor = await db.users.find_one({"id": record["doctor_id"]})
            if doctor:
                doctor = serialize_doc(doctor)
                record["doctor_name"] = doctor["name"]
    
    return [MedicalRecord(**record) for record in records]

@api_router.get("/medical-records/{patient_user_id}")
async def get_patient_records(patient_user_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = await db.patients.find_one({"user_id": patient_user_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient = serialize_doc(patient)
    records = await db.medical_records.find({"patient_id": patient["id"]}).sort("created_at", -1).to_list(100)
    records = serialize_doc(records)
    return [MedicalRecord(**record) for record in records]

# AI Helper Functions
async def generate_file_summary(filename: str, file_type: str, user_id: str):
    """Generate AI summary for uploaded medical files"""
    try:
        # Get user context
        user = await db.users.find_one({"id": user_id})
        if not user:
            return "Unable to generate summary - user not found"
        
        user = serialize_doc(user)
        context = f"Medical file uploaded by {user['name']} ({user['role']}): {filename}"
        
        if file_type == "application/pdf":
            context += "\n\nThis appears to be a PDF medical document. Please provide a general summary of what this type of medical document typically contains and suggest what the patient should discuss with their doctor."
        elif file_type.startswith("image/"):
            context += "\n\nThis appears to be a medical image or scan. Please provide guidance on what medical images are typically used for and suggest follow-up actions."
        
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"file-summary-{user_id}-{datetime.now().isoformat()}",
            system_message="You are a medical file assistant. Provide helpful summaries and guidance for uploaded medical documents."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=context)
        response = await chat.send_message(user_message)
        
        return response
        
    except Exception as e:
        logging.error(f"File summary generation error: {str(e)}")
        return "AI summary temporarily unavailable. Please consult with your healthcare provider about this document."

# AI Chat Routes (Enhanced)
@api_router.post("/chat")
async def chat_with_ai(chat_request: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        # Get comprehensive user context
        user_context = ""
        if current_user.role == "patient":
            patient = await db.patients.find_one({"user_id": current_user.id})
            if patient:
                patient = serialize_doc(patient)
                user_context = f"""
                Patient Profile:
                - Age: {patient.get('age', 'Not specified')}
                - Gender: {patient.get('gender', 'Not specified')}
                - Blood Group: {patient.get('blood_group', 'Not specified')}
                - Weight: {patient.get('weight', 'Not specified')} kg
                - Height: {patient.get('height', 'Not specified')} cm
                - Allergies: {', '.join(patient.get('allergies', [])) or 'None'}
                - Chronic Conditions: {', '.join(patient.get('chronic_conditions', [])) or 'None'}
                - Current Medications: {', '.join(patient.get('current_medications', [])) or 'None'}
                """
            
            # Get recent medical records
            if patient:
                records = await db.medical_records.find({"patient_id": patient["id"]}).sort("created_at", -1).limit(5).to_list(5)
                records = serialize_doc(records)
                if records:
                    user_context += "\nRecent Medical Records:\n"
                    for record in records:
                        user_context += f"- {record['title']} ({record['record_type']}): {record.get('description', 'No description')}\n"
                        if record.get('file_name'):
                            user_context += f"  Attached file: {record['file_name']}\n"
                
                # Get recent prescriptions
                prescriptions = await db.prescriptions.find({"patient_id": patient["id"], "status": "active"}).limit(5).to_list(5)
                prescriptions = serialize_doc(prescriptions)
                if prescriptions:
                    user_context += "\nCurrent Prescriptions:\n"
                    for prescription in prescriptions:
                        user_context += f"- {prescription['medication_name']}: {prescription['dosage']} {prescription['frequency']}\n"
                
                # Get upcoming appointments
                today = datetime.now().date()
                appointments = await db.appointments.find({
                    "patient_id": patient["id"],
                    "appointment_date": {"$gte": today},
                    "status": "scheduled"
                }).limit(3).to_list(3)
                appointments = serialize_doc(appointments)
                if appointments:
                    user_context += "\nUpcoming Appointments:\n"
                    for appointment in appointments:
                        user_context += f"- {appointment['appointment_date']} at {appointment['appointment_time']} ({appointment['appointment_type']})\n"
            
            # Get recent uploaded files
            files = await db.file_uploads.find({"user_id": current_user.id}).sort("created_at", -1).limit(3).to_list(3)
            files = serialize_doc(files)
            if files:
                user_context += "\nRecently Uploaded Files:\n"
                for file in files:
                    user_context += f"- {file['original_filename']} ({file['upload_type']})\n"
                    if file.get('ai_summary'):
                        user_context += f"  Summary: {file['ai_summary'][:100]}...\n"
        
        # Set system message based on role
        if current_user.role == "patient":
            system_message = f"""You are a helpful health assistant for a patient. You have access to their complete medical profile and records. 
            
            {user_context}
            
            Guidelines:
            - Provide helpful information about their health data
            - Explain medical terms in simple language
            - Give general health advice and reminders
            - Help them understand their prescriptions and appointments
            - Suggest when to consult with doctors
            - NEVER provide diagnosis or critical medical advice
            - Always encourage consulting healthcare professionals for serious concerns
            - Be supportive and encouraging
            - Reference their uploaded files, prescriptions, and appointments when relevant
            """
        else:
            system_message = f"""You are a medical AI assistant for healthcare professionals. You can help with:
            - Summarizing patient histories
            - Suggesting common treatment approaches
            - Providing medical reference information
            - Helping with documentation
            - Appointment and prescription management guidance
            
            Guidelines:
            - Provide professional medical insights
            - Suggest evidence-based treatments when appropriate
            - Help with clinical documentation
            - Always emphasize clinical judgment and patient evaluation
            - Support decision-making but don't replace clinical expertise
            """
        
        try:
            # Initialize chat with emergentintegrations
            chat = LlmChat(
                api_key=OPENAI_API_KEY,
                session_id=f"{current_user.id}-{datetime.now().isoformat()}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            # Send message
            user_message = UserMessage(text=chat_request.message)
            response = await chat.send_message(user_message)
            
            # Save chat message
            chat_obj = ChatMessage(
                user_id=current_user.id,
                message=chat_request.message,
                response=response
            )
            chat_dict = serialize_doc(chat_obj.dict())
            await db.chat_messages.insert_one(chat_dict)
            
            return {"response": response}
            
        except Exception as ai_error:
            logging.error(f"AI Chat error: {str(ai_error)}")
            # Provide a fallback response instead of failing completely
            fallback_response = f"""I apologize, but I'm currently experiencing technical difficulties with the AI service. 
            
            In the meantime, here are some general suggestions:
            
            {"For health-related questions, please consult with your healthcare provider directly. You can also review your medical records, prescriptions, and upcoming appointments in your dashboard for reference. If you've uploaded any medical documents, make sure to discuss them with your doctor during your next appointment." if current_user.role == "patient" else "For clinical assistance, please refer to your medical references or consult with colleagues. Patient data can be reviewed in the records section, and uploaded files can be accessed through the file management system."}
            
            Please try again later when the AI service is restored."""
            
            # Still save the interaction for logging purposes
            chat_obj = ChatMessage(
                user_id=current_user.id,
                message=chat_request.message,
                response=fallback_response
            )
            chat_dict = serialize_doc(chat_obj.dict())
            await db.chat_messages.insert_one(chat_dict)
            
            return {"response": fallback_response}
        
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

@api_router.get("/chat/history")
async def get_chat_history(current_user: User = Depends(get_current_user)):
    messages = await db.chat_messages.find({"user_id": current_user.id}).sort("created_at", -1).limit(50).to_list(50)
    messages = serialize_doc(messages)
    return [ChatMessage(**msg) for msg in messages]

# Dashboard Stats (Enhanced with appointments and prescriptions)
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == "patient":
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient:
            return {
                "records_count": 0, 
                "files_count": 0, 
                "appointments_count": 0,
                "prescriptions_count": 0,
                "profile_complete": False
            }
        
        patient = serialize_doc(patient)
        records_count = await db.medical_records.count_documents({"patient_id": patient["id"]})
        files_count = await db.file_uploads.count_documents({"user_id": current_user.id})
        appointments_count = await db.appointments.count_documents({"patient_id": patient["id"]})
        prescriptions_count = await db.prescriptions.count_documents({"patient_id": patient["id"]})
        
        # Get upcoming appointments
        today = datetime.now().date().isoformat()
        upcoming_appointments = await db.appointments.count_documents({
            "patient_id": patient["id"],
            "appointment_date": {"$gte": today},
            "status": "scheduled"
        })
        
        # Get active prescriptions
        active_prescriptions = await db.prescriptions.count_documents({
            "patient_id": patient["id"],
            "status": "active"
        })
        
        return {
            "records_count": records_count,
            "files_count": files_count,
            "appointments_count": appointments_count,
            "prescriptions_count": prescriptions_count,
            "upcoming_appointments": upcoming_appointments,
            "active_prescriptions": active_prescriptions,
            "profile_complete": bool(patient.get("age") and patient.get("gender") and patient.get("blood_group"))
        }
    else:
        patients_count = await db.users.count_documents({"role": "patient"})
        records_count = await db.medical_records.count_documents({"doctor_id": current_user.id})
        appointments_count = await db.appointments.count_documents({"doctor_id": current_user.id})
        prescriptions_count = await db.prescriptions.count_documents({"doctor_id": current_user.id})
        total_files = await db.file_uploads.count_documents({})
        
        # Get today's appointments
        today = datetime.now().date().isoformat()
        today_appointments = await db.appointments.count_documents({
            "doctor_id": current_user.id,
            "appointment_date": today
        })
        
        return {
            "patients_count": patients_count,
            "records_count": records_count,
            "appointments_count": appointments_count,
            "prescriptions_count": prescriptions_count,
            "today_appointments": today_appointments,
            "total_files": total_files
        }

# AI Summary Routes (Enhanced)
@api_router.post("/ai/summarize-reports")
async def ai_summarize_reports(current_user: User = Depends(get_current_user)):
    """Generate comprehensive AI summary of patient's health data"""
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied - Patients only")
    
    try:
        # Get patient profile
        patient = await db.patients.find_one({"user_id": current_user.id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        patient = serialize_doc(patient)
        
        # Get comprehensive health data
        records = await db.medical_records.find({"patient_id": patient["id"]}).sort("created_at", -1).limit(10).to_list(10)
        records = serialize_doc(records)
        
        files = await db.file_uploads.find({"user_id": current_user.id, "upload_type": "medical_report"}).sort("created_at", -1).limit(5).to_list(5)
        files = serialize_doc(files)
        
        prescriptions = await db.prescriptions.find({"patient_id": patient["id"]}).sort("created_at", -1).limit(10).to_list(10)
        prescriptions = serialize_doc(prescriptions)
        
        appointments = await db.appointments.find({"patient_id": patient["id"]}).sort("appointment_date", -1).limit(5).to_list(5)
        appointments = serialize_doc(appointments)
        
        # Prepare comprehensive context for AI
        summary_context = f"""
        Comprehensive Health Summary Request for {current_user.name}:
        
        Patient Profile:
        - Age: {patient.get('age', 'Not specified')}
        - Gender: {patient.get('gender', 'Not specified')}
        - Blood Group: {patient.get('blood_group', 'Not specified')}
        - Weight: {patient.get('weight', 'Not specified')} kg
        - Height: {patient.get('height', 'Not specified')} cm
        - Current Medications: {', '.join(patient.get('current_medications', [])) or 'None listed'}
        - Chronic Conditions: {', '.join(patient.get('chronic_conditions', [])) or 'None listed'}
        - Allergies: {', '.join(patient.get('allergies', [])) or 'None listed'}
        
        Recent Medical Records ({len(records)} records):
        """
        
        for record in records:
            summary_context += f"""
        - {record['title']} ({record['record_type']}) - {record['created_at'][:10]}
          Description: {record.get('description', 'No description')}
          {'File attached: ' + record.get('file_name', '') if record.get('file_name') else 'No file attached'}
        """
        
        if prescriptions:
            summary_context += f"""
        
        Current Prescriptions ({len([p for p in prescriptions if p['status'] == 'active'])} active):
        """
            for prescription in prescriptions:
                status_indicator = "✓ ACTIVE" if prescription['status'] == 'active' else f"({prescription['status'].upper()})"
                summary_context += f"- {prescription['medication_name']}: {prescription['dosage']} {prescription['frequency']} {status_indicator}\n"
        
        if appointments:
            summary_context += f"""
        
        Recent/Upcoming Appointments ({len(appointments)} total):
        """
            for appointment in appointments:
                summary_context += f"- {appointment['appointment_date']} at {appointment['appointment_time']} - {appointment['status']} ({appointment['appointment_type']})\n"
        
        if files:
            summary_context += f"""
        
        Recently Uploaded Medical Files ({len(files)} files):
        """
            for file in files:
                summary_context += f"- {file['original_filename']} (uploaded {file['created_at'][:10]})\n"
                if file.get('ai_summary'):
                    summary_context += f"  AI Summary: {file['ai_summary']}\n"
        
        summary_context += """
        
        Please provide a comprehensive, personalized health summary including:
        1. Current Health Status Overview
        2. Key Medical Findings and Trends
        3. Medication Management & Reminders
        4. Appointment Follow-up Recommendations
        5. Health Maintenance Suggestions
        6. Questions to Discuss with Your Doctor
        
        Keep the summary clear, encouraging, and actionable for the patient.
        """
        
        try:
            # Generate comprehensive AI summary
            chat = LlmChat(
                api_key=OPENAI_API_KEY,
                session_id=f"comprehensive-summary-{current_user.id}-{datetime.now().isoformat()}",
                system_message="You are a comprehensive health assistant providing detailed, personalized health summaries for patients based on their complete medical profile, records, prescriptions, and appointments."
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text=summary_context)
            ai_summary = await chat.send_message(user_message)
            
            return {
                "summary": ai_summary,
                "records_analyzed": len(records),
                "files_analyzed": len(files),
                "prescriptions_analyzed": len(prescriptions),
                "appointments_analyzed": len(appointments),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as ai_error:
            logging.error(f"AI Summary error: {str(ai_error)}")
            # Provide comprehensive fallback summary
            fallback_summary = f"""
            📋 Comprehensive Health Summary (Generated {datetime.now().strftime('%B %d, %Y')})
            
            👤 PATIENT PROFILE
            • Name: {current_user.name}
            • Age: {patient.get('age', 'Not specified')}
            • Blood Group: {patient.get('blood_group', 'Not specified')}
            • Current Medications: {', '.join(patient.get('current_medications', [])) or 'None listed'}
            
            📊 HEALTH DATA OVERVIEW
            • Medical Records: {len(records)} on file
            • Uploaded Files: {len(files)} medical documents
            • Prescriptions: {len(prescriptions)} total ({len([p for p in prescriptions if p['status'] == 'active'])} active)
            • Appointments: {len(appointments)} tracked
            
            💊 CURRENT MEDICATIONS
            """
            
            active_prescriptions = [p for p in prescriptions if p['status'] == 'active']
            if active_prescriptions:
                for prescription in active_prescriptions[:5]:
                    fallback_summary += f"• {prescription['medication_name']}: {prescription['dosage']} {prescription['frequency']}\n"
            else:
                fallback_summary += "• No active prescriptions on record\n"
            
            fallback_summary += """
            
            📅 RECENT ACTIVITY
            """
            
            for record in records[:3]:
                fallback_summary += f"• {record['title']} - {record['created_at'][:10]}\n"
            
            if appointments:
                upcoming_appointments = [a for a in appointments if a['status'] == 'scheduled']
                if upcoming_appointments:
                    fallback_summary += f"\n🗓️  UPCOMING APPOINTMENTS\n"
                    for appointment in upcoming_appointments[:2]:
                        fallback_summary += f"• {appointment['appointment_date']} at {appointment['appointment_time']} ({appointment['appointment_type']})\n"
            
            fallback_summary += """
            
            📝 RECOMMENDATIONS
            • Keep your medical records up to date
            • Upload new test results and reports as you receive them
            • Take medications as prescribed by your doctor
            • Maintain regular check-ups and follow-up appointments
            • Discuss any concerns with your healthcare provider
            
            ⚠️  Note: AI summary service is temporarily unavailable. This is a comprehensive overview of your health records.
            For detailed medical advice, please consult with your healthcare provider.
            """
            
            return {
                "summary": fallback_summary,
                "records_analyzed": len(records),
                "files_analyzed": len(files),
                "prescriptions_analyzed": len(prescriptions),
                "appointments_analyzed": len(appointments),
                "generated_at": datetime.now().isoformat(),
                "fallback": True
            }
            
    except Exception as e:
        logging.error(f"Comprehensive summary generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate health summary")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task for processing scheduled notifications
import asyncio
import threading

notification_scheduler_running = False

async def notification_scheduler():
    """Simple scheduler to process notifications every 5 minutes"""
    global notification_scheduler_running
    if notification_scheduler_running:
        return
    
    notification_scheduler_running = True
    print("🔔 Notification scheduler started")
    
    while True:
        try:
            await process_scheduled_notifications()
            # Wait 5 minutes before next check
            await asyncio.sleep(300)
        except Exception as e:
            print(f"⚠️ Notification scheduler error: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute on error

def start_background_scheduler():
    """Start the notification scheduler in a separate thread"""
    def run_scheduler():
        asyncio.run(notification_scheduler())
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    global client, db
    print("🚀 HealthCard ID Backend starting up...")
    
    # Initialize MongoDB connection
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'healthcard_db')]
    
    # Test the connection
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection established")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
    
    # Start the notification scheduler
    start_background_scheduler()
    
    print("✅ Background services initialized")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    if client:
        client.close()
        print("✅ MongoDB connection closed")