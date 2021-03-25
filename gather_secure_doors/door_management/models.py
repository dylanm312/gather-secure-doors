from django.db import models

# Create your models here.
class Workspace(models.Model):
    workspace_name = models.CharField(max_length=200)
    workspace_id = models.CharField(max_length=200)
    api_key = models.CharField(max_length=200)

    def __str__(self):
        return self.workspace_name

class Room(models.Model):
    room_name = models.CharField(max_length=200)
    room_id = models.CharField(max_length=200)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    def __str__(self):
        return self.room_name

class Door(models.Model):
    door_name = models.CharField(max_length=200)
    open_image = models.ImageField()
    closed_image = models.ImageField()
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=2)
    x_position = models.IntegerField(default=0)
    y_position = models.IntegerField(default=0)
    password = models.CharField(max_length=200)
    door_url = models.URLField(max_length=200)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return self.door_name