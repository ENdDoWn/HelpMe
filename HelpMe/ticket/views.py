from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm, TicketForm
from .models import Ticket
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm, TicketForm
from .models import Ticket, Message

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
            if user.groups.filter(name='Agents').exists():
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
        messages.success(request, "You have been logged out successfully.")
        return redirect('login')

from django.contrib.auth.mixins import UserPassesTestMixin

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
            messages.success(request, 'Ticket created successfully!')
            return redirect('chat', ticket_id=ticket.id)
        else:
            tickets = Ticket.objects.filter(creator=request.user).order_by('-created_at')
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'main_user.html', {
                'tickets': tickets,
                'form': form
            })

class ChatView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            
            # Check if user has permission to access this ticket
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
