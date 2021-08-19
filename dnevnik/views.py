import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.views.generic import View, ListView, DetailView, CreateView
from django.shortcuts import render, redirect

from .forms import ScoreAddForm
from .models import User, Subject, StudyClass, Score
from .utils import TeacherRequiredMixin, StudentRequiredMixin

logger = logging.getLogger(__name__)


class HomeView(LoginRequiredMixin, View):
    """Начальная вьюха,
     для ученика одна, для учителя другая"""
    login_url = 'login'

    def get(self, request):
        if request.user.profile.is_teacher:
            class_ = StudyClass.objects.filter(
                teacher=request.user.id
            ).prefetch_related(
                'students'
            )
            return render(request,
                          'dnevnik/home_for_teacher.html',
                          context={'myclasses': class_})

        elif not request.user.profile.is_teacher:
            # scores = Score.objects.filter(student__id=request.user.id).select_related('subject').values(
            #     'score', 'comment',
            #     'date', 'subject__title', )
            subjects = Subject.objects.all()

            return render(
                request,
                'dnevnik/home_for_student.html',
                context={'subjects': subjects}
            )


class ClassesList(TeacherRequiredMixin, ListView):
    """Все классы, только для учителя"""
    model = StudyClass
    queryset = StudyClass.objects.prefetch_related(
        'students').select_related(
        'teacher',
        'teacher__profile'
    )
    template_name = 'dnevnik/classes_list.html'
    context_object_name = 'classes'


class ClassDetail(TeacherRequiredMixin, DetailView):
    """Детали каждого класса, только для учителя"""
    model = StudyClass
    queryset = StudyClass.objects.all()
    template_name = 'dnevnik/class_detail.html'
    context_object_name = 'class'

    def get_queryset(self):
        return self.queryset.filter(
            pk=self.kwargs['pk']).prefetch_related(
            'students').select_related(
            'teacher__profile',
            'teacher'
        )


class StudentDetail(TeacherRequiredMixin, DetailView):
    """Ученик детально,
     показываются все оценки, только для учителя"""
    model = User
    template_name = 'dnevnik/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scores'] = Score.objects.filter(
            student__slug=self.kwargs['slug']).select_related(
            'student',
            'subject',
        )
        context['avg_scores'] = Score.objects.filter(
            student__slug=self.kwargs['slug']).select_related(
            'subject', 'student').values(
            'subject__title').annotate(
            avg_score=models.Avg('score'))
        context['subjects'] = Subject.objects.all()
        return context


class ScoreAddView(TeacherRequiredMixin, View):
    """Установка оценки для ученика,
     ученику можно установить оценку только если ты его учителя,
      только для учителя"""

    def get(self, request, slug):
        teachers = User.objects.get(
            slug=slug
        ).class_for_student.all().select_related(
            'teacher'
        ).values_list('teacher')[0]
        if request.user.id not in teachers:
            return redirect('home')
        form = ScoreAddForm()
        return render(
            request,
            'dnevnik/add_score.html',
            context={'form': form}
        )

    def post(self, request, slug):
        form = ScoreAddForm(request.POST)
        if form.is_valid():
            score = form.save(commit=False)
            score.student = User.objects.get(slug=slug)
            score.save()
            return redirect('home')
        return render(
            request,
            'dnevnik/add_score.html',
            context={'form': form}
        )


class SubjectDetail(StudentRequiredMixin, View):
    """Каждый урок отдельно,
     показываются для каждого урока, только для ученика"""

    def get(self, request, subject_slug):
        scores = Score.objects.filter(
            student_id=request.user.id,
            subject__slug=subject_slug
        ).select_related(
            'student',
            'subject',
        )
        avg_score = Score.objects.filter(
            student_id=request.user.id,
            subject__slug=subject_slug
        ).select_related(
            'subject',
            'student'
        ).aggregate(
            avg_score=models.Avg('score'))
        subject = Subject.objects.get(slug=subject_slug)

        context = {
            'scores': scores,
            'avg_score': avg_score,
            'subject': subject,
        }

        return render(request, 'dnevnik/subject_detail.html', context=context)
