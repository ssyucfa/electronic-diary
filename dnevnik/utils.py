import logging

from django import forms
from django.contrib.auth.mixins import AccessMixin

from .models import User

logger = logging.getLogger(__name__)


class MixinAdmin:
    """Миксин для выборочного показа
    GenericForeignKey"""
    name_of_field = None
    teacher = None

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Устанавливаем выборочный показ,
         для какого то поля,
          чтобы там показывались либо учителя, либо ученики, только"""
        if db_field.name == self.name_of_field:
            return forms.ModelChoiceField(
                User.objects.filter(profile__is_teacher=self.teacher))
        return super().formfield_for_dbfield(
            db_field,
            request,
            **kwargs
        )


class TeacherRequiredMixin(AccessMixin):
    """Миксин для того,
     чтобы на страничку могли только зарегистрированные учителя"""
    login_url = 'home'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated
                or not
                request.user.profile.is_teacher):
            return self.handle_no_permission()
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f'Ошибка: {e}')
            logger.debug(f'Ошибка: {e}')


class StudentRequiredMixin(AccessMixin):
    """Миксин для того,
     чтобы на страничку могли только зарегистрированные ученики"""
    login_url = 'home'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated
                or
                request.user.profile.is_teacher):
            return self.handle_no_permission()
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f'Ошибка: {e}')
            logger.debug(f'Ошибка: {e}')
