from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('subject/<slug:subject_slug>/', views.SubjectDetail.as_view(), name='subject'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('classes/', views.ClassesList.as_view(), name='classes'),
    path('classes/class/<int:pk>/', views.ClassDetail.as_view(), name='class'),
    path('student/<slug:slug>', views.StudentDetail.as_view(), name='student'),
    path('student/<slug:slug>/add_score/', views.ScoreAddView.as_view(), name='score_add'),
]