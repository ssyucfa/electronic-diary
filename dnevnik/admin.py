from django import forms
from django.contrib import admin
from .utils import MixinAdmin

from .models import Score, Subject, StudyClass, User, Group

from . import service


@admin.register(StudyClass)
class StudyClassAdmin(MixinAdmin, admin.ModelAdmin):
    name_of_field = 'teacher'
    teacher = True
    prepopulated_fields = {'slug': ('name',)}

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'students':
            return forms.ModelMultipleChoiceField(User.objects.filter(is_teacher=False))
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Score)
class ScoreAdmin(MixinAdmin, admin.ModelAdmin):
    name_of_field = 'student'
    teacher = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('first_name', 'last_name')}

    # ПОЧЕМУ ТО НЕ РАБОТАЕТ, не работает потому что не берет экземляр, как я понимаю
    # def save_model(self, request, obj, form, change) -> None:
    #     obj.save()
    #     if obj.is_teacher:
    #         print(obj.id)
    #         group = Group.objects.get(pk=1)
    #         group.user_set.add(obj)
    #     return super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change) -> None:
        super().save_related(request, form, formsets, change)
        if form.instance.is_teacher:
            group_teacher = Group.objects.get(name='Teacher')
            form.instance.groups.add(group_teacher)
            service.delete_another_group_for_user_if_has(form.instance, 'Student')
        else:
            group_student = Group.objects.get(name='Student')
            form.instance.groups.add(group_student)
            service.delete_another_group_for_user_if_has(form.instance, 'Teacher')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

