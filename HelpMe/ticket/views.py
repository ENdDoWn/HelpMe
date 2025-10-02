from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.contrib import messages
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm, TicketForm
from .models import Ticket
from django.contrib.auth.mixins import LoginRequiredMixin

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('main_user')
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Successfully logged in!')
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

class MainView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        tickets = Ticket.objects.filter(creator=request.user).order_by('-created_at')
        form = TicketForm()
        return render(request, 'main_user.html', {
            'tickets': tickets,
            'form': form
        })

class CreateTicketView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creator = request.user
            ticket.save()
            
            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': 'Ticket created successfully',
                'ticket': {
                    'id': ticket.id,
                    'title': ticket.title,
                    'priority': ticket.get_priority_display(),
                    'status': ticket.get_status_display(),
                    'created_at': ticket.created_at.strftime('%Y-%m-%d')
                }
            })
        else:
            # Return form errors
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            })
