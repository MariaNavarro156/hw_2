"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""

from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                               # allows using logger.warning(), logger.error(), 
                                                               # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

class InstructorProfile(models.Model):
    """InstructorProfile extends the built-in User model with instructor-specific data."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class StudentProfile(models.Model):
    """StudentProfile extends the built-in User model with student-specific data."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

class Course(models.Model):
    """Course represents a course taught by one instructor."""
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    day_mon = models.BooleanField(default=False)
    day_tue = models.BooleanField(default=False)
    day_wed = models.BooleanField(default=False)
    day_thu = models.BooleanField(default=False)
    day_fri = models.BooleanField(default=False)

    def meets_on_day(self, weekday_int):
        """Return True if the course meets on the given weekday (0=Mon)."""
        return [self.day_mon, self.day_tue, self.day_wed,
                self.day_thu, self.day_fri][weekday_int]

    def __str__(self):
        return self.name

# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------

class Enrollment(models.Model):
    """Enrollment links a student to a course (many to many)"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

def _random_qr_data(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class Lecture(models.Model):
    """Lecture represents a single course meeting"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    qr_code = models.CharField(max_length=100, unique=True, default=_random_qr_data)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} on {self.date}"



# ---------------------------------------------------------------------------
# QR Code Upload
# ---------------------------------------------------------------------------

class QRCodeUpload(models.Model):
    """QRCodeUpload represents a student's uploaded QR code photograph."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='qr_uploads/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    decoded_data = models.CharField(max_length=256, blank=True, default='')
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f"Upload by {self.student} for {self.lecture} at {self.uploaded_at}"


# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------

def is_instructor(user):
    """Return True if the user has an InstructorProfile."""
    return hasattr(user, 'instructor_profile')


def is_student(user):
    """Return True if the user has a StudentProfile."""
    return hasattr(user, 'student_profile')



