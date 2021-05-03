import logging

from django.conf import settings
from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import Workspace, Room, Door
from .gather_door_updater import unlock_door


logging.basicConfig(filename=settings.LOG_FILE, level=logging.DEBUG)


class WorkspaceIndexView(generic.ListView):
    model = Workspace


class RoomIndexView(generic.ListView):
    model = Room


class DoorIndexView(generic.ListView):
    model = Door


@csrf_exempt
@xframe_options_exempt
def door_login(request, workspace_slug, room_slug, door_slug):
    workspace = get_object_or_404(Workspace, workspace_slug=workspace_slug)
    room = get_object_or_404(Room, room_slug=room_slug)
    door = get_object_or_404(Door, door_slug=door_slug)
    return render(request, 'door_management/doorLogin.html', {
        'workspace': workspace,
        'room': room,
        'door': door})


@csrf_exempt
@xframe_options_exempt
def check_password(request):
    logging.debug('check_password data:{}'.format(request.POST))

    try:
        workspace_id = request.POST['workspaceId']
        room_id = request.POST['roomId']
        door_id = request.POST['doorId']
        password = request.POST['password']
    except KeyError:
        return HttpResponseBadRequest('Error: POST parameters not found. Check your URL and try again')

    workspace = get_object_or_404(Workspace, pk=workspace_id)
    room = get_object_or_404(Room, pk=room_id)
    door = get_object_or_404(Door, pk=door_id)

    if password.lower().replace(" ", "") == door.password.lower().replace(" ", ""):
        passwordOk = True
        logging.debug('unlocking door: {}'.format(door.id))
        unlock_door(door)
    else:
        passwordOk = False

    return render(request, 'door_management/doorLogin.html', {
        'workspace': workspace,
        'room': room,
        'door': door,
        'passwordOk': passwordOk})
