from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

STATUS_CHOICES = [('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected'),('EXPIRED','Expired')]
ROLE_CHOICES = [('READ','Read'),('WRITE','Write')]

class LeaseRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_requested = models.CharField(max_length=5, choices=ROLE_CHOICES)
    reason = models.TextField()
    duration_seconds = models.PositiveIntegerField(default=3600)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    assumed_role_arn = models.CharField(max_length=255, blank=True)
    access_key = models.CharField(max_length=255, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)
    session_token = models.CharField(max_length=255, blank=True)
    expiration = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role_requested} - {self.status}"
