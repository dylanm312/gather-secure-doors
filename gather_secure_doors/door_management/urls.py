from django.urls import path
from . import views

urlpatterns = [
    path('', views.WorkspaceIndexView.as_view(), name='workspaceIndex'),
    path('<str:workspace_slug>', views.RoomIndexView.as_view(), name='roomIndex'),
    path('<str:workspace_slug>/<str:room_slug>', views.DoorIndexView.as_view(), name='doorIndex'),
    path('doorLogin/<str:workspace_slug>/<str:room_slug>/<str:door_slug>/', views.door_login, name='doorLogin'),
    path('checkPassword', views.check_password, name='checkPassword')
]
