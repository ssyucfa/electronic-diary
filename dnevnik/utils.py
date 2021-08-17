from django import forms
from django.contrib.auth.mixins import AccessMixin

from .models import User


class MixinAdmin:
    """Миксин для выборочного показа
    GenericForeignKey"""
    name_of_field = None
    teacher = None

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == self.name_of_field:
            return forms.ModelChoiceField(User.objects.filter(profile__is_teacher=self.teacher))
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class TeacherRequiredMixin(AccessMixin):
    pass


class StudentRequiredMixin(AccessMixin):
    pass