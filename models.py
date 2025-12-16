from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, String, DECIMAL, Integer, Boolean, Date, Time, JSON
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum
import uuid

# Initialize SQLAlchemy
db = SQLAlchemy()

# Enum definitions
class UserRole(enum.Enum):
    ADMIN = "admin"
    PHOTOGRAPHER = "photographer" 
    STAFF = "staff"

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class QuoteStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class EnrollmentStatus(enum.Enum):
    PENDING = "pending"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ENROLLED = "enrolled"
    COMPLETED = "completed"

class ServiceCategory(enum.Enum):
    PHOTOGRAPHY = "photography"
    VIDEOGRAPHY = "videography"

class PortfolioCategory(enum.Enum):
    WEDDINGS = "Weddings"
    PORTRAITS = "Portraits"
    EVENTS = "Events"
    COMMERCIAL = "Commercial"

class CohortStatus(enum.Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ContactMessageStatus(enum.Enum):
    UNREAD = "unread"
    READ = "read"
    REPLIED = "replied"

class EmailLogStatus(enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    PENDING = "pending"

# User Model (Admin/Staff)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STAFF)
    phone = db.Column(db.String(20), nullable=True)
    avatar_url = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    bookings = db.relationship('Booking', back_populates='assigned_to_user', foreign_keys='Booking.assigned_to', lazy=True)
    quote_requests = db.relationship('QuoteRequest', back_populates='assigned_to_user', foreign_keys='QuoteRequest.assigned_to', lazy=True)
    enrollments = db.relationship('Enrollment', back_populates='reviewed_by_user', foreign_keys='Enrollment.reviewed_by', lazy=True)
    portfolio_items = db.relationship('PortfolioItem', back_populates='instructor', foreign_keys='PortfolioItem.instructor_id', lazy=True)
    cohorts = db.relationship('Cohort', back_populates='instructor', foreign_keys='Cohort.instructor_id', lazy=True)
    email_logs = db.relationship('EmailLog', back_populates='user', foreign_keys='EmailLog.user_id', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_photographer(self):
        return self.role == UserRole.PHOTOGRAPHER

    def is_staff(self):
        return self.role in [UserRole.ADMIN, UserRole.STAFF, UserRole.PHOTOGRAPHER]

    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Client Information
    client_name = db.Column(db.String(255), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    client_email = db.Column(db.String(255), nullable=False)
    
    # Booking Details
    service_type = db.Column(db.String(255), nullable=False)
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.Time, nullable=True)
    location = db.Column(db.Text, nullable=True)
    budget_range = db.Column(db.String(50), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)
    
    # Management
    status = db.Column(db.Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    assigned_to = db.Column(String(36), db.ForeignKey('users.id'), nullable=True)
    internal_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    assigned_to_user = db.relationship('User', back_populates='bookings')

    def as_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "client_email": self.client_email,
            "service_type": self.service_type,
            "preferred_date": self.preferred_date.isoformat(),
            "preferred_time": self.preferred_time.isoformat() if self.preferred_time else None,
            "location": self.location,
            "budget_range": self.budget_range,
            "additional_notes": self.additional_notes,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "internal_notes": self.internal_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

# Quote Request Model
class QuoteRequest(db.Model):
    __tablename__ = 'quote_requests'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Client Information
    client_name = db.Column(db.String(255), nullable=False)
    client_email = db.Column(db.String(255), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(255), nullable=True)
    
    # Quote Details - Changed from JSONB to JSON
    selected_services = db.Column(JSON, nullable=False)  # Array of service IDs
    event_date = db.Column(db.Date, nullable=True)
    event_location = db.Column(db.Text, nullable=True)
    budget_range = db.Column(db.String(50), nullable=True)
    project_description = db.Column(db.Text, nullable=True)
    referral_source = db.Column(db.String(50), nullable=True)
    
    # Quote Response
    status = db.Column(db.Enum(QuoteStatus), nullable=False, default=QuoteStatus.PENDING)
    quoted_amount = db.Column(DECIMAL(10, 2), nullable=True)
    quote_details = db.Column(db.Text, nullable=True)
    quote_sent_at = db.Column(db.DateTime, nullable=True)
    valid_until = db.Column(db.Date, nullable=True)
    
    # Management
    assigned_to = db.Column(String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assigned_to_user = db.relationship('User', back_populates='quote_requests')

    def as_dict(self):
        return {
            "id": self.id,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "client_phone": self.client_phone,
            "company_name": self.company_name,
            "selected_services": self.selected_services,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "event_location": self.event_location,
            "budget_range": self.budget_range,
            "project_description": self.project_description,
            "referral_source": self.referral_source,
            "status": self.status.value,
            "quoted_amount": float(self.quoted_amount) if self.quoted_amount else None,
            "quote_details": self.quote_details,
            "quote_sent_at": self.quote_sent_at.isoformat() if self.quote_sent_at else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Enrollment Model
class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Student Information
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(Integer, nullable=True)
    
    # Background
    education_occupation = db.Column(db.Text, nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)
    has_own_camera = db.Column(Boolean, default=False, nullable=False)
    learning_goals = db.Column(db.Text, nullable=True)
    
    # Enrollment
    preferred_intake = db.Column(db.String(50), nullable=True)
    cohort_id = db.Column(String(36), db.ForeignKey('cohorts.id'), nullable=True)
    status = db.Column(db.Enum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.PENDING)
    
    # Payment
    registration_fee_paid = db.Column(Boolean, default=False, nullable=False)
    payment_reference = db.Column(db.String(100), nullable=True)
    
    # Management
    reviewed_by = db.Column(String(36), db.ForeignKey('users.id'), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    reviewed_by_user = db.relationship('User', back_populates='enrollments')
    cohort = db.relationship('Cohort', back_populates='enrollments')

    def as_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "age": self.age,
            "education_occupation": self.education_occupation,
            "experience_level": self.experience_level,
            "has_own_camera": self.has_own_camera,
            "learning_goals": self.learning_goals,
            "preferred_intake": self.preferred_intake,
            "cohort_id": self.cohort_id,
            "status": self.status.value,
            "registration_fee_paid": self.registration_fee_paid,
            "payment_reference": self.payment_reference,
            "reviewed_by": self.reviewed_by,
            "admin_notes": self.admin_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Services Model
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category = db.Column(db.Enum(ServiceCategory), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Pricing
    price_min = db.Column(DECIMAL(10, 2), nullable=True)
    price_max = db.Column(DECIMAL(10, 2), nullable=True)
    price_display = db.Column(db.String(100), nullable=True)  # "Ksh 40,000 – 150,000"
    
    # Features - Changed from JSONB to JSON
    features = db.Column(JSON, nullable=True)  # ["4K Video", "Drone Coverage", "Same-day Edit"]
    
    # Display
    is_active = db.Column(Boolean, default=True, nullable=False)
    is_featured = db.Column(Boolean, default=False, nullable=False)
    display_order = db.Column(Integer, default=0, nullable=False)
    icon_name = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "category": self.category.value,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "price_min": float(self.price_min) if self.price_min else None,
            "price_max": float(self.price_max) if self.price_max else None,
            "price_display": self.price_display,
            "features": self.features,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "display_order": self.display_order,
            "icon_name": self.icon_name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Portfolio Model
class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_items'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.Enum(PortfolioCategory), nullable=False)
    
    # Media
    image_url = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.Text, nullable=True)
    
    # Details
    description = db.Column(db.Text, nullable=True)
    client_name = db.Column(db.String(255), nullable=True)
    shoot_date = db.Column(db.Date, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    
    # Display
    is_featured = db.Column(Boolean, default=False, nullable=False)
    is_published = db.Column(Boolean, default=True, nullable=False)
    display_order = db.Column(Integer, default=0, nullable=False)
    
    # SEO
    alt_text = db.Column(db.Text, nullable=True)
    tags = db.Column(JSON, nullable=True)  # ["outdoor", "golden-hour", "candid"] - Changed from JSONB to JSON
    
    # Management
    instructor_id = db.Column(String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    instructor = db.relationship('User', back_populates='portfolio_items')

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category.value,
            "image_url": self.image_url,
            "thumbnail_url": self.thumbnail_url,
            "description": self.description,
            "client_name": self.client_name,
            "shoot_date": self.shoot_date.isoformat() if self.shoot_date else None,
            "location": self.location,
            "is_featured": self.is_featured,
            "is_published": self.is_published,
            "display_order": self.display_order,
            "alt_text": self.alt_text,
            "tags": self.tags,
            "instructor_id": self.instructor_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Cohort Model
class Cohort(db.Model):
    __tablename__ = 'cohorts'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)  # "January 2025 Intake"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    max_students = db.Column(Integer, default=20, nullable=False)
    current_enrollment = db.Column(Integer, default=0, nullable=False)
    
    status = db.Column(db.Enum(CohortStatus), nullable=False, default=CohortStatus.UPCOMING)
    
    # Pricing
    course_fee = db.Column(DECIMAL(10, 2), nullable=False, default=15000.00)
    registration_fee = db.Column(DECIMAL(10, 2), default=2000.00, nullable=False)
    
    # Details
    schedule_details = db.Column(db.Text, nullable=True)  # "Mon-Fri, 2pm-5pm"
    instructor_id = db.Column(String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    instructor = db.relationship('User', back_populates='cohorts')
    enrollments = db.relationship('Enrollment', back_populates='cohort')

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "max_students": self.max_students,
            "current_enrollment": self.current_enrollment,
            "status": self.status.value,
            "course_fee": float(self.course_fee),
            "registration_fee": float(self.registration_fee),
            "schedule_details": self.schedule_details,
            "instructor_id": self.instructor_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Business Info Model
class BusinessInfo(db.Model):
    __tablename__ = 'business_info'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Contact
    business_name = db.Column(db.String(255), nullable=False, default='Lenny Media Kenya')
    address = db.Column(db.Text, nullable=False)
    phone_primary = db.Column(db.String(20), nullable=False)
    phone_secondary = db.Column(db.String(20), nullable=True)
    email_primary = db.Column(db.String(255), nullable=False)
    email_support = db.Column(db.String(255), nullable=True)
    
    # Hours - Changed from JSONB to JSON
    hours_of_operation = db.Column(JSON, nullable=False)
    # Example: {"monday": "8:00 AM - 6:00 PM", "tuesday": "8:00 AM - 6:00 PM", ...}
    
    # Social Media - Changed from JSONB to JSON
    social_media = db.Column(JSON, nullable=True)
    # Example: {"instagram": "https://instagram.com/lennymedia", "facebook": "https://facebook.com/lennymedia"}
    
    # Map
    google_maps_embed_url = db.Column(db.Text, nullable=True)
    latitude = db.Column(DECIMAL(10, 8), nullable=True)
    longitude = db.Column(DECIMAL(11, 8), nullable=True)
    
    # Only one active record
    is_active = db.Column(Boolean, default=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "business_name": self.business_name,
            "address": self.address,
            "phone_primary": self.phone_primary,
            "phone_secondary": self.phone_secondary,
            "email_primary": self.email_primary,
            "email_support": self.email_support,
            "hours_of_operation": self.hours_of_operation,
            "social_media": self.social_media,
            "google_maps_embed_url": self.google_maps_embed_url,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "is_active": self.is_active,
            "updated_at": self.updated_at.isoformat()
        }

# Contact Message Model
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(ContactMessageStatus), nullable=False, default=ContactMessageStatus.UNREAD)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "subject": self.subject,
            "message": self.message,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }

# Email Log Model
class EmailLog(db.Model):
    __tablename__ = 'email_logs'

    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    template_name = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum(EmailLogStatus), nullable=False, default=EmailLogStatus.PENDING)
    user_id = db.Column(String(36), db.ForeignKey('users.id'), nullable=True)
    related_booking_id = db.Column(String(36), db.ForeignKey('bookings.id'), nullable=True)
    related_quote_id = db.Column(String(36), db.ForeignKey('quote_requests.id'), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='email_logs')

    def as_dict(self):
        return {
            "id": self.id,
            "recipient_email": self.recipient_email,
            "subject": self.subject,
            "template_name": self.template_name,
            "status": self.status.value,
            "user_id": self.user_id,
            "related_booking_id": self.related_booking_id,
            "related_quote_id": self.related_quote_id,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat()
        }