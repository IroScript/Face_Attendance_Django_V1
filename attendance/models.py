

# Create your models here.
# models.py (in attendance app)
from django.db import models
from django.contrib.auth.models import User
import os

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_encoding = models.BinaryField()
    registration_video = models.FileField(upload_to='registration_videos/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    video_in = models.FileField(upload_to='attendance_videos/in/', null=True)
    video_out = models.FileField(upload_to='attendance_videos/out/', null=True)

    class Meta:
        unique_together = ['employee', 'date']