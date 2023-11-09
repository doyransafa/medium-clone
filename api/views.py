from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def first_page():
    return JsonResponse({'data': 'first page'})