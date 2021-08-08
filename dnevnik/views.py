from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.


def view(request):
    return JsonResponse({'success': True})