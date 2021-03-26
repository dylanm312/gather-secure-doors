from django.contrib import admin
from .models import Workspace, Room, Door

# Register your models here.
@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    readonly_fields = ['workspace_slug']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    readonly_fields = ['room_slug']

@admin.register(Door)
class DoorAdmin(admin.ModelAdmin):
    readonly_fields = ['door_slug']