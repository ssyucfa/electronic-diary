from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from .models import User


class SetLastVisitOnSiteMiddleware(MiddlewareMixin):
    """С каждым входом на сайт
    пользователю будет ставиться последний вход"""
    def process_response(self, request, response):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(last_visit=timezone.now())
        return response
