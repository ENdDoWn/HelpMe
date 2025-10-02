from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('main/', views.MainView.as_view(), name='main_user'),
    path('ticket/create/', views.CreateTicketView.as_view(), name='create_ticket'),
]
