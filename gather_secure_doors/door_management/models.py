from django.db import models
from django.template.defaultfilters import slugify
#from .gather_door_updater import delete_door

# Create your models here.
class Workspace(models.Model):
    workspace_name = models.CharField(max_length=200)
    workspace_slug = models.SlugField()
    workspace_id = models.CharField(max_length=200)
    api_key = models.CharField(max_length=200)

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
    open_image = models.ImageField(upload_to='door_management/static/door_images')
    closed_image = models.ImageField(upload_to='door_management/static/door_images')
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=2)
    x_position = models.IntegerField(default=0)
    y_position = models.IntegerField(default=0)
    password = models.CharField(max_length=200)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return self.door_name

    # Auto-generate door slug
    def save(self, *args, **kwargs):
        # Only generate slug for brand new doors, else we risk breaking links
        if not self.id:
            self.door_slug = slugify(self.door_name)

        super(Door, self).save(*args, **kwargs)

    # Delete door from Gather when deleted from Django Admin
    # def delete(self, *args, **kwargs):
    #     delete_door(self.room.workspace.id, self.room.id, self.id)

    #     super(Door, self).delete(*args, **kwargs)