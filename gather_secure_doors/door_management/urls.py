from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('doorLogin', views.doorLogin, name='doorLogin')
]
