from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('doorLogin/<str:workspace_slug>/<str:room_slug>/<str:door_slug>/', views.door_login, name='doorLogin'),
    path('checkPassword', views.check_password, name='checkPassword')
]
