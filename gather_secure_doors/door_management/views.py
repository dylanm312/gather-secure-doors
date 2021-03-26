from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse

from .models import Workspace, Room, Door
from .gather_door_updater import unlock_door

# Create your views here.
def index(request):
    return HttpResponse('Hello world!')

def door_login(request):
    try:
        workspace_id = request.GET['workspaceId']
        room_id = request.GET['roomId']
        door_id = request.GET['doorId']
    except KeyError:
        return HttpResponseBadRequest('Error: GET parameters not found. Check your URL and try again')
        
    workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
    room = get_object_or_404(Room, room_id=room_id)
    door = get_object_or_404(Door, door_id=door_id)
    return render(request, 'door_management/doorLogin.html', {'workspace': workspace, 'room': room, 'door': door})

def check_password(request):
    try:
        workspace_id = request.POST['workspaceId']
        room_id = request.POST['roomId']
        door_id = request.POST['doorId']
        password = request.POST['password']
    except KeyError:
        return HttpResponseBadRequest('Error: GET parameters not found. Check your URL and try again')

    workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
    room = get_object_or_404(Room, room_id=room_id)
    door = get_object_or_404(Door, door_id=door_id)

    if password == door.password:
        passwordOk = True
        unlock_door(workspace_id, room_id, door_id)
    else:
        passwordOk = False

    return render(request, 'door_management/doorLogin.html', {'workspace': workspace, 'room': room, 'door': door, 'passwordOk': passwordOk})