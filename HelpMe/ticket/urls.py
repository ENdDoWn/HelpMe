from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('main/', views.MainView.as_view(), name='main_user'),
    path('ticket/create/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('ticket/<int:ticket_id>/chat/', views.ChatView.as_view(), name='chat'),
    path('agent/', views.AgentView.as_view(), name='main_agent'),
]
