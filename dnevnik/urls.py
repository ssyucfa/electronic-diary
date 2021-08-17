from django.contrib.auth.views import LoginView
from django.urls import path

from .views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
]