from django.urls import path
from .views import first_page

urlpatterns = [
    path('', first_page),
]