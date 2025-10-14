from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Organization, Profile, Ticket, Attachment, Message, Notification, FAQ


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your username',
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'class': 'form-control'
    }))


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your firstname',
        'class': 'form-control'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your lastname',
        'class': 'form-control'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your username',
        'class': 'form-control'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Create a password',
        'class': 'form-control'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
        'class': 'form-control'
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your Address',
        'class': 'form-control'
    }))
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'existing-org'
        }),
        required=False,
        label='Select Existing Organization'
    )
    new_organization = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter new organization name',
            'class': 'form-control',
            'id': 'new-org'
        }),
        required=False,
        label='Or Create New Organization'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        organization = cleaned_data.get('organization')
        new_organization = cleaned_data.get('new_organization')

        if not organization and not new_organization:
            raise forms.ValidationError('Please either select an existing organization or create a new one.')
        
        if organization and new_organization:
            raise forms.ValidationError('Please either select an existing organization or create a new one, not both.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            organization = self.cleaned_data.get('organization')
            if not organization:
                organization = Organization.objects.create(
                    name=self.cleaned_data['new_organization']
                )

            Profile.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                organization=organization
            )
        return user

# User Update Form
class UserForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter current password',
        'class': 'form-control'
    }), required=False, label='Current Password')

    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter new password (optional)',
        'class': 'form-control'
    }), required=False, label='New Password')

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm new password',
        'class': 'form-control'
    }), required=False, label='Confirm New Password')

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name not in ['old_password', 'new_password', 'confirm_password']:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        password_fields = [old_password, new_password, confirm_password]
        filled_fields = [field for field in password_fields if field]

        if filled_fields and len(filled_fields) != len(password_fields):
            if not old_password:
                self.add_error('old_password', 'Current password is required to change password.')
            if not new_password:
                self.add_error('new_password', 'New password is required.')
            if not confirm_password:
                self.add_error('confirm_password', 'Please confirm your new password.')

        if old_password and new_password and confirm_password:
            if self.user and not self.user.check_password(old_password):
                self.add_error('old_password', 'Current password is incorrect.')

            if new_password != confirm_password:
                self.add_error('confirm_password', 'New passwords do not match.')

            if len(new_password) < 8:
                self.add_error('new_password', 'Password must be at least 8 characters long.')

        return cleaned_data


# Profile Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone_number", "address", "organization"]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your address',
                'rows': 3
            }),
            'organization': forms.Select(attrs={
                'class': 'form-control'
            })
        }


# Organization Form
class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name"]


# Ticket Form
class TicketForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter ticket subject'
    }))
    description = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter ticket description'
    }))
    priority = forms.ChoiceField(
        choices=Ticket.Priority.choices,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority']

    def save(self, commit=True):
        ticket = super().save(commit=False)
        ticket.status = Ticket.Status.OPEN 
        if commit:
            ticket.save()
        return ticket


# Attachment Form
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ["file"]


# Message Form
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["msg"]


# Notification Form
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["msg", "read"]

# FAQ Form
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["question", "answer", "category"]
