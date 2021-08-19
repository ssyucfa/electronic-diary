from django import forms
from django.contrib import admin

from django_reverse_admin import ReverseModelAdmin

from .utils import MixinAdmin

from .models import Score, Subject, StudyClass, User, Group, Profile

from . import service


@admin.register(StudyClass)
class StudyClassAdmin(MixinAdmin, admin.ModelAdmin):
    """Админка для класса"""
    name_of_field = 'teacher'
    teacher = True
    prepopulated_fields = {'slug': ('name',)}

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Делаем выборку,
         чтобы в поле students показывались только ученики,
          которые находятся не в классе """
        if db_field.name == 'students':
            return forms.ModelMultipleChoiceField(
                User.objects.filter(profile__is_teacher=False,
                                    is_in_class=False
                                    )
            )
        return super().formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )


@admin.register(Score)
class ScoreAdmin(MixinAdmin, admin.ModelAdmin):
    """Админка для оценок"""
    name_of_field = 'student'
    teacher = False


@admin.register(User)
class UserAdmin(ReverseModelAdmin):
    """Админка для пользователя"""
    prepopulated_fields = {'slug': ('first_name', 'last_name')}
    inline_type = 'tabular'
    inline_reverse = [
        ('profile', {'fields': ['age', 'patronymic', 'is_teacher']})
    ]

    def save_related(self, request, form, formsets, change) -> None:
        """Сохраняем группу пермишинов для пользователя,
         с каждым сохранением"""
        super().save_related(request, form, formsets, change)
        if form.instance.profile.is_teacher:
            group_teacher = Group.objects.get(name='Teacher')
            form.instance.groups.add(group_teacher)
            service.delete_another_group_for_user_if_has(
                form.instance,
                'Student'
            )
        else:
            group_student = Group.objects.get(name='Student')
            form.instance.groups.add(group_student)
            service.delete_another_group_for_user_if_has(
                form.instance,
                'Teacher'
            )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Админка для предметов"""
    prepopulated_fields = {'slug': ('title',)}
