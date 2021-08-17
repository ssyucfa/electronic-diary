from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView
from django.shortcuts import render

from .models import User, Subject, StudyClass, Score
from .utils import TeacherRequiredMixin


# Для авг оценки, вот так вот Score.objects.filter(student__username='patinik', subject__id=1).aggregate(
# avg_score=models.Avg('score'))
class HomeView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        if request.user.profile.is_teacher:
            class_ = StudyClass.objects.get(
                teacher_id=request.user.id
            ).values('name', )
            return render(request,
                          'dnevnik/home_for_teacher.html',
                          context={'class': class_})

        elif not request.user.profile.is_teacher:
            # scores = Score.objects.filter(student__id=request.user.id).select_related('subject').values(
            #     'score', 'comment',
            #     'date', 'subject__title', )
            subject = Subject.objects.all()
            return render(request,
                          'dnevnik/home_for_student.html',
                          context={'subject': subject})


class ClassesList(TeacherRequiredMixin, ListView):
    model = StudyClass
    queryset = StudyClass.objects.all().select_related(
        'teacher'
    ).values(
        'name', 'teacher__first_name',
        'teacher__profile__patronymic'
    )


