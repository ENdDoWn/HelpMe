from django.db import models
from django.contrib.auth.models import User


# Organization
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name="organizations", blank=True)

    def __str__(self):
        return self.name


# Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="profiles", blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Ticket
class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        CLOSED = "CLOSED", "Closed"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.OPEN)
    description = models.TextField()
    priority = models.CharField(max_length=50, choices=Priority.choices, default=Priority.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.OneToOneField(User, on_delete=models.CASCADE, related_name="created_ticket")

    def __str__(self):
        return f"{self.title} ({self.status})"


# Attachment
class Attachment(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="attachment")
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket.title}"


# Message
class Message(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="message")
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="message")
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.user.username} on {self.ticket.title}"


# Notification
class Notification(models.Model):
    recipients = models.ManyToManyField(User, related_name="notifications")
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="notification")
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {', '.join([u.username for u in self.recipients.all()])}"


# FAQ
class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('COMMON', 'Common Questions'),
        ('ACCOUNT', 'Account Related'),
        ('DOCUMENT', 'Documentation'),
        ('TECHNICAL', 'Technical Issues'),
        ('OTHER', 'Other'),
    ]

    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='COMMON')
    creator = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faq")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]
