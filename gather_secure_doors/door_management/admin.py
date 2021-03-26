from django.contrib import admin
from .models import Workspace, Room, Door

# Register your models here.
admin.site.register(Workspace)
admin.site.register(Room)

@admin.register(Door)
class DoorAdmin(admin.ModelAdmin):
    readonly_fields = ['door_slug']
