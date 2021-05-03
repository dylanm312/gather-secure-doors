from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from . import gather_door_updater


# Create your models here.
class Workspace(models.Model):
    workspace_name = models.CharField(max_length=200)
    workspace_slug = models.SlugField()
    workspace_id = models.CharField(max_length=200,help_text=mark_safe('Last two segments of gather URL separated by one backslash. ie. BMcBcCSENP5Duahv\\testdoor'))
    api_key = models.CharField(max_length=200,help_text='Get one here: https://gather.town/apiKeys')

    def __str__(self):
        return self.workspace_name

    # Auto-generate workspace slug
    def save(self, *args, **kwargs):
        if not self.id:
            self.workspace_slug = slugify(self.workspace_name)

        super(Workspace, self).save(*args, **kwargs)


class Room(models.Model):
    room_name = models.CharField(max_length=200)
    room_slug = models.SlugField()
    room_id = models.CharField(max_length=200)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def __str__(self):
        return self.room_name

    # Auto-generate room slug
    def save(self, *args, **kwargs):
        if not self.id:
            self.room_slug = slugify(self.room_name)

        super(Room, self).save(*args, **kwargs)


class Door(models.Model):
    door_name = models.CharField(max_length=200)
    door_slug = models.SlugField()
    open_image = models.ImageField(upload_to='doors', blank=True, null=True)
    closed_image = models.ImageField(upload_to='doors', blank=True, null=True)
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=2)
    x_position = models.IntegerField(default=0)
    y_position = models.IntegerField(default=0)
    password = models.CharField(max_length=200)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return self.door_name

    # Auto-generate door slug and init door in Gather map
    def save(self, *args, **kwargs):
        # Only generate slug for brand new doors, else we risk breaking links
        if not self.id:
            self.door_slug = slugify(self.door_name)
            gather_door_updater.init_door(self)

        super(Door, self).save(*args, **kwargs)

    # Delete door from Gather map when deleted from Django Admin
    def delete(self, *args, **kwargs):
        gather_door_updater.delete_door(self)

        super(Door, self).delete(*args, **kwargs)
