from django.contrib.auth.views import LoginView
from django.urls import path

from .views import HomeView, ClassesList, ClassDetail, StudentDetail, ScoreAddView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('classes/', ClassesList.as_view(), name='classes'),
    path('classes/class/<int:pk>/', ClassDetail.as_view(), name='class'),
    path('student/<slug:slug>', StudentDetail.as_view(), name='student'),
    path('student/<slug:slug>/add_score/', ScoreAddView.as_view(), name='score_add'),

]