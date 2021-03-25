from django import http
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from .models import Workspace, Room, Door

# Create your views here.
def index(request):
    return HttpResponse('Hello world!')

def doorLogin(request):
    try:
        workspaceId = request.GET['workspaceId']
        roomId = request.GET['roomId']
        doorId = request.GET['doorId']
    except KeyError:
        return HttpResponseBadRequest('Error: GET parameters not found. Check your URL and try again')
        
    workspace = get_object_or_404(Workspace, workspace_id=workspaceId)
    room = get_object_or_404(Room, room_id=roomId)
    door = get_object_or_404(Door, door_id=doorId)
    return render(request, 'door_management/doorLogin.html', {'workspace': workspace, 'room': room, 'door': door})