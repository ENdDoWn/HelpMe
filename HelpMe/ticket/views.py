from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
import json
from .forms import LoginForm, RegisterForm, TicketForm
from .models import *

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Agents').exists():
                return redirect('main_agent')
            return redirect('main_user')
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            if user.groups.filter(name='Agents').exists() or user.groups.filter(name='Admin').exists():
                return redirect('main_agent')
            return redirect('main_user')
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'login.html', {'form': form})

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('main_user')
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('main_user')
        else:
            messages.error(request, 'Registration failed. Please check your input.')
            return render(request, 'register.html', {'form': form})

class LogoutView(View):

    def get(self, request):
        logout(request)
        messages.warning(request, "You have been logged out.")
        return redirect('login')


class MainView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        if request.user.groups.filter(name='Agents').exists():
            return redirect('main_agent')
        tickets = Ticket.objects.filter(creator=request.user).order_by('-created_at')
        form = TicketForm()
        return render(request, 'main_user.html', {
            'tickets': tickets,
            'form': form
        })

class AgentView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'

    def test_func(self):
        return self.request.user.groups.filter(name='Agents').exists()

    def handle_no_permission(self):
        messages.error(self.request, 'Access denied. Agent privileges required.')
        return redirect('login')

    def get(self, request):
        tickets = Ticket.objects.all().order_by('-created_at')
        return render(request, 'main_agent.html', {
            'tickets': tickets
        })

class CreateTicketView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creator = request.user
            ticket.save()
            return redirect('chat', ticket_id=ticket.id)
        else:
            tickets = Ticket.objects.filter(creator=request.user).order_by('-created_at')
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'main_user.html', {
                'tickets': tickets,
                'form': form
            })

class CloseTicketView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'

    def test_func(self):
        return self.request.user.groups.filter(name='Agents').exists()

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.status = 'closed'
            ticket.save()
            messages.success(request, 'Ticket has been closed successfully.')
            return redirect('chat', ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            messages.error(request, 'Ticket not found.')
            return redirect('main_agent')

class ChatView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            if not (request.user.groups.filter(name='Agents').exists() or ticket.creator == request.user):
                messages.error(request, 'Access denied. You do not have permission to view this ticket.')
                return redirect('main_user')
            chat_messages = ticket.messages.all().order_by('created_at')
            return render(request, 'chat.html', {
                'ticket': ticket,
                'messages': chat_messages
            })
        except Ticket.DoesNotExist:
            messages.error(request, 'Ticket not found.')
            return redirect('main_user')

class FAQView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        faqs = FAQ.objects.all().order_by('category', '-created_at')
        return render(request, 'FAQ.html', {
            'faqs': faqs,
            'is_agent': request.user.groups.filter(name='Agents').exists(),
            'category_choices': FAQ.CATEGORY_CHOICES
        })

    def post(self, request):
        if not request.user.groups.filter(name='Agents').exists():
            messages.error(request, 'Only agents can create FAQs')
            return redirect('faq')
        
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        category = request.POST.get('category')
        
        if question and answer and category:
            FAQ.objects.create(
                question=question,
                answer=answer,
                category=category,
                creator=request.user
            )
            messages.success(request, 'FAQ created successfully')
        else:
            messages.error(request, 'All fields are required')
        
        return redirect('faq')

class FAQDetailView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, faq_id):
        try:
            faq = FAQ.objects.get(id=faq_id)
            return render(request, 'faq_details.html', {'faq': faq})
        except FAQ.DoesNotExist:
            messages.error(request, 'FAQ not found')
            return redirect('faq')

class ProfileView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        return render(request, 'profile.html', {'user': request.user, 'profile': profile})

    def post(self, request):
        user = request.user
        profile = user.profile
        profile.address = request.POST.get('bio', profile.address)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('profile')


class FileUploadView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, ticket_id):
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            ticket = Ticket.objects.get(id=ticket_id)
            
            # Check if user has access to ticket
            if not (request.user.groups.filter(name='Agents').exists() or ticket.creator == request.user):
                return JsonResponse({'error': 'Access denied'}, status=403)
            
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            # Check file size (limit to 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if uploaded_file.size > max_size:
                return JsonResponse({'error': 'File size too large. Maximum 10MB allowed.'}, status=400)
            
            # Create message with file
            message = Message.objects.create(
                user=request.user,
                ticket=ticket,
                file=uploaded_file,
                file_name=uploaded_file.name,
                msg=f"📎 {uploaded_file.name}"
            )
            
            # Send message through WebSocket to avoid duplication
            channel_layer = get_channel_layer()
            room_group_name = f'chat_{ticket_id}'
            
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': f"📎 {uploaded_file.name}",
                    'username': request.user.username,
                    'timestamp': message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'is_file': True,
                    'file_name': uploaded_file.name,
                    'file_url': message.file.url
                }
            )
            
            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'file_name': uploaded_file.name
            })
            
        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
