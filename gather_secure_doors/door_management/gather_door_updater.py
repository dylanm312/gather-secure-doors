from django.shortcuts import get_object_or_404, render
import json
from .models import Workspace, Room, Door

import requests
import logging

def unlock_door(workspace_id, room_id, door_id):

    logging.basicConfig(filename='door_updater.log', level=logging.DEBUG)

    # Get all our variables
    workspace = Workspace.objects.get(workspace_id=workspace_id)
    room = Room.objects.get(room_id=room_id)
    door = Door.objects.get(door_id=door_id)
    api_key = workspace.api_key
    door_images = [
        door.open_image,
        door.closed_image
    ]
    door_pos = [
        door.x_position,
        door.y_position
    ]
    door_url = door.door_url

    logging.debug('Got workspace, room, door, api key, images, door position, and door url.')

    # Get the current map state
    map_data = get_map(workspace_id, room_id, api_key)
    old_map_data = json.loads(json.dumps(map_data))

    logging.debug('Got current map state')

    # Find the door object, change its image, and store the old object
    map_data, old_map_data = find_and_change_door_image(door, map_data, old_map_data)

    # Get rid of the impassable tile
    map_data, old_map_data = change_impassable_tile(door, map_data, old_map_data)

    return {
        'workspace': workspace.workspace_id,
        'room': room.room_id,
        'door': door.door_id,
        'api_key': api_key,
        #'door_images': door_images,
        'door_pos': door_pos,
        'door_url': door_url
    }

def get_map(workspace_id, room_id, api_key):
    payload = {
        'spaceId': workspace_id,
        'mapId': room_id,
        'apiKey': api_key
    }
    r = requests.get('https://gather.town/api/getMap', params=payload)
    return r.json()

def find_and_change_door_image(door, map_data, old_map_data):
    
    # Look for the door on the map. If we find it, open it in map_data, and cache the closed door in old_map_data
    found = False
    for i, obj in enumerate(map_data['objects']):
        if (obj['x'] == door.x_position and obj['y'] == door.y_position):
            found = True
            logging.debug('Found door at X: %d, Y: %d' % (obj['x'], obj['y']))
            map_data['objects'][i]['normal'] = door.open_image
            old_map_data['objects'][i]['normal'] = door.closed_image

    # If we couldn't find the door, create it
    if found == False:
        open_door = {
            'type': 1,
            'x': door.x_position,
            'y': door.y_position,
            'properties': {
                'url': door.door_url
            },
            'width': door.width,
            'height': door.height,
            'normal': door.open_image,
        }
        closed_door = {
            'type': 1,
            'x': door.x_position,
            'y': door.y_position,
            'properties': {
                'url': door.door_url
            },
            'width': door.width,
            'height': door.height,
            'normal': door.closed_image
        }

        map_data['objects'].append(open_door)
        old_map_data['objects'].append(closed_door)

        logging.debug('Door not found; created at X: %d, Y: %d' % (door.x_position, door.y_position))

    # Return the updated map data objects
    return map_data, old_map_data

def change_impassable_tile(door, map_data, old_map_data):
    pass