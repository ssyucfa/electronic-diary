from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from .models import User


class SetLastVisitOnSiteMiddleware(MiddlewareMixin):
    """Ставит пользователю, который зашел на сайт, последнее посещение сайта"""
    def process_response(self, request, response):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(last_visit=timezone.now())
        return response
