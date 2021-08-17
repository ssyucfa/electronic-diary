from django.contrib.auth.views import LoginView
from django.urls import path

from .views import HomeView, ClassesList


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('classes/', ClassesList.as_view(), name='classes')
]