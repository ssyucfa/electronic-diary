from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group

from .models import *


# Register your models here.


class StudyClassAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'is_teacher':
            return forms.ModelChoiceField(User.objects.filter(is_teacher=True))
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'students':
                return forms.ModelMultipleChoiceField(User.objects.filter(is_teacher=False))
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class ScoreAdmin(admin.ModelAdmin):
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs ):
        if db_field.name == 'student':
            return forms.ModelChoiceField(User.objects.filter(is_teacher=False))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class UserAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('first_name', 'last_name')}

    #ПОЧЕМУ ТО НЕ РАБОТАЕТ, не работает потому что не берет экземляр, как я понимаю
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
            group_teacher = Group.objects.get(pk=1)
            form.instance.groups.add(group_teacher)
        else:
            group_student = Group.objects.get(pk=2)
            form.instance.groups.add(group_student)


class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', )}


admin.site.register(User, UserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(StudyClass, StudyClassAdmin)
admin.site.register(Score, ScoreAdmin)
