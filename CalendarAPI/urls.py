from django.urls import path
from . import views

urlpatterns = [
    path('init/', views.GoogleCalendarInitView, name='Google Calendar Init'),
    path('redirect/',  views.GoogleCalendarRedirectView, name='Google Calendar Redirect'),
]
