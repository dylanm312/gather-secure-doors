from django.contrib import admin
from .models import Workspace, Room, Door

# Register your models here.
admin.site.register(Workspace)
admin.site.register(Room)
admin.site.register(Door)