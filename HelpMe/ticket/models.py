from django.db import models
from django.contrib.auth.models import AbstractUser


# Organization
class Organization(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# User
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        USER = "USER", "User"
        AGENT = "AGENT", "Agent"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

# Profile
class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

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
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self):
        return f"{self.title} ({self.status})"

# Attachment
class Attachment(models.Model):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Message
class Message(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages"
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="messages"
    )
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Notification
class Notification(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="notifications"
    )
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# FAQ
class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="faqs"
    )

    def __str__(self):
        return self.question[:50]
