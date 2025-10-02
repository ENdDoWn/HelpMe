from django.db import models
from django.contrib.auth.models import User


# Organization
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# Profile (extends Django User)
class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="members"
    )

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

    def __str__(self):
        return f"Attachment for {self.ticket.title}"


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

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.user.username} on {self.ticket.title}"


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
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}"


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
