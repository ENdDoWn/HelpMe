from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import RegisterForm
from .models import User


class LoginView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "login.html", {"form": form, "active_tab": "login"})

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {user.username}!")
            print("yes")
            return redirect("home")  # แก้เป็นหน้าที่คุณต้องการ
        else:
            messages.error(request, "Invalid username or password")
        return render(request, "login.html", {"form": RegisterForm(), "active_tab": "login"})


class RegisterView(View):
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.role:
                user.role = User.Role.USER  # ค่า default role
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login")
        return render(request, "login.html", {"form": form, "active_tab": "register"})
