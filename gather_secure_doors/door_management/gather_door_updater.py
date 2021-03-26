from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from threading import Thread
import json
from time import sleep

import requests
import logging
import base64

def init_door(workspace, room, door):

    logging.basicConfig(filename='door_updater.log', level=logging.DEBUG)

    # Get all our variables in order
    api_key = workspace.api_key
    door_image_urls = {
        'open': 'https://i.imgur.com/VqQ9w3q.png',
        'closed': 'https://i.imgur.com/xh6zKMd.png'
    }
    door_url = "http://localhost:8000" + reverse('doorLogin', kwargs={'workspace_slug': workspace.workspace_slug, 'room_slug': room.room_slug, 'door_slug': door.door_slug})

    logging.debug('Got workspace, room, door, and API key')
    logging.debug('Door image urls: ')
    logging.debug(door_image_urls)
    
    logging.debug('Door url:')
    logging.debug(door_url)

    # Get the current map state
    map_data = get_map(workspace, room, api_key)
    old_map_data = json.loads(json.dumps(map_data))

    logging.debug('Got current map state')

    # Look for the door on the map. If we find it, return
    found = False
    for i, obj in enumerate(map_data['objects']):
        if (obj['x'] == door.x_position and obj['y'] == door.y_position):
            found = True
            logging.debug('Door already found at X: %d, Y: %d' % (door.x_position, door.y_position))
            return False

    # If we couldn't find the door, create it
    if found == False:
        closed_door = {
            'type': 1,
            'x': door.x_position,
            'y': door.y_position,
            'properties': {
                'url': door_url
            },
            'width': door.width,
            'height': door.height,
            'normal': door_image_urls['closed'],
            'highlighted': door_image_urls['closed']
        }

        map_data['objects'].append(closed_door)

        logging.debug('Door initialized at X: %d, Y: %d' % (door.x_position, door.y_position))
        logging.debug(map_data['objects'][-1])

    # Change the normal tile to impassible in map data
    collision_buffer = bytearray(base64.b64decode(map_data['collisions']))
    for dx in range(door.width):
        for dy in range(door.height):
            collision_buffer[
                (door.y_position + dy) * old_map_data['dimensions'][0] + door.x_position + dx
            ] = 0x01

    map_data['collisions'] = base64.b64encode(collision_buffer).decode('ascii')
    logging.debug('Changed normal tile to impassible (door initialized)')

    ###### Send the update to Gather ######
    response, payload = set_map(workspace, room, api_key, map_data)

    logging.debug('Response summary (init_door):')
    logging.debug({
        'workspace': workspace.workspace_id,
        'room': room.room_id,
        'door': door.door_slug,
        'api_key': api_key,
        'door_pos': {
            'x': door.x_position,
            'y': door.y_position
        },

        'response': {
            'status_code' : response.status_code,
            'text': response.text
        },
        'request' : {
            'payload' : payload
        },
    })

def unlock_door(workspace, room, door):

    logging.basicConfig(filename='door_updater.log', level=logging.DEBUG)

    # Get all our variables in order
    api_key = workspace.api_key
    door_image_urls = {
        'open': 'https://i.imgur.com/VqQ9w3q.png',
        'closed': 'https://i.imgur.com/xh6zKMd.png'
    }
    door_url = "http://localhost:8000" + reverse('doorLogin', kwargs={'workspace_slug': workspace.workspace_slug, 'room_slug': room.room_slug, 'door_slug': door.door_slug})

    logging.debug('Got workspace, room, door, and API key')
    logging.debug('Door image urls: ')
    logging.debug(door_image_urls)
    
    logging.debug('Door url:')
    logging.debug(door_url)

    # Get the current map state
    map_data = get_map(workspace, room, api_key)
    old_map_data = json.loads(json.dumps(map_data))

    logging.debug('Got current map state')

    
    ###### Find the door object, change its image, and store the old object ######

    # Look for the door on the map. If we find it, open it in map_data, and cache the closed door in old_map_data
    found = False
    for i, obj in enumerate(map_data['objects']):
        if (obj['x'] == door.x_position and obj['y'] == door.y_position):
            found = True
            logging.debug('Found door at X: %d, Y: %d' % (obj['x'], obj['y']))
            map_data['objects'][i]['normal'] = door_image_urls['open']
            map_data['objects'][i]['highlighted'] = door_image_urls['open']
            old_map_data['objects'][i]['normal'] = door_image_urls['closed']
            old_map_data['objects'][i]['highlighted'] = door_image_urls['closed']

    # If we couldn't find the door, create it
    if found == False:
        open_door = {
            'type': 1,
            'x': door.x_position,
            'y': door.y_position,
            'properties': {
                'url': door_url
            },
            'width': door.width,
            'height': door.height,
            'normal': door_image_urls['open'],
            'highlighted': door_image_urls['open']
        }
        closed_door = {
            'type': 1,
            'x': door.x_position,
            'y': door.y_position,
            'properties': {
                'url': door_url
            },
            'width': door.width,
            'height': door.height,
            'normal': door_image_urls['closed'],
            'highlighted': door_image_urls['closed']
        }

        map_data['objects'].append(open_door)
        old_map_data['objects'].append(closed_door)

        logging.debug('Door not found; created at X: %d, Y: %d' % (door.x_position, door.y_position))
        logging.debug(map_data['objects'][-1])


    ###### Get rid of the impassable tile ######

    # Change the impassable tile to normal in the new map data
    collision_buffer = bytearray(base64.b64decode(map_data['collisions']))
    for dx in range(door.width):
        for dy in range(door.height):
            collision_buffer[
                (door.y_position + dy) * map_data['dimensions'][0] + door.x_position + dx
            ] = 0x00

    map_data['collisions'] = base64.b64encode(collision_buffer).decode('ascii')
    logging.debug('Changed impassable tile to normal in new map')

    # Change the normal tile to impassible in the old map data
    old_collision_buffer = bytearray(base64.b64decode(old_map_data['collisions']))
    for dx in range(door.width):
        for dy in range(door.height):
            old_collision_buffer[
                (door.y_position + dy) * old_map_data['dimensions'][0] + door.x_position + dx
            ] = 0x01

    old_map_data['collisions'] = base64.b64encode(old_collision_buffer).decode('ascii')
    logging.debug('Changed normal tile to impassible in old map')

    ###### Send the update to Gather ######
    response, payload = set_map(workspace, room, api_key, map_data)

    if response.status_code == 200:
        # Wait 5 seconds and then close/lock the door
        t = Thread(target=set_map, args=(workspace, room, api_key, old_map_data, 5))
        t.start()


    logging.debug('Response summary (unlock_door):')
    logging.debug({
        'workspace': workspace.workspace_id,
        'room': room.room_id,
        'door': door.door_slug,
        'api_key': api_key,
        'door_pos': {
            'x': door.x_position,
            'y': door.y_position
        },

        'response': {
            'status_code' : response.status_code,
            'text': response.text
        },
        'request' : {
            'payload' : payload
        },
    })

def delete_door(workspace, room, door):

    logging.basicConfig(filename='door_updater.log', level=logging.DEBUG)

    # Get all our variables in order
    api_key = workspace.api_key
    
    # Get the current map state
    map_data = get_map(workspace, room, api_key)

    # Find and remove the door
    found = False
    for i, obj in enumerate(map_data['objects']):
        if (obj['x'] == door.x_position and obj['y'] == door.y_position):
            found = True
            logging.debug('Found door at X: %d, Y: %d' % (obj['x'], obj['y']))
            del map_data['objects'][i]
            logging.debug('Door deleted from map')

    ###### Get rid of the impassable tile ######

    # Change the impassable tile to normal in the new map data
    collision_buffer = bytearray(base64.b64decode(map_data['collisions']))
    for dx in range(door.width):
        for dy in range(door.height):
            collision_buffer[
                (door.y_position + dy) * map_data['dimensions'][0] + door.x_position + dx
            ] = 0x00

    map_data['collisions'] = base64.b64encode(collision_buffer).decode('ascii')
    logging.debug('Changed impassable tile to normal')

    ###### Send the update to Gather ######
    response, payload = set_map(workspace, room, api_key, map_data)

    logging.debug('Response summary (delete_door):')
    logging.debug({
        'workspace': workspace.workspace_id,
        'room': room.room_id,
        'door': door.door_slug,
        'api_key': api_key,
        'door_pos': {
            'x': door.x_position,
            'y': door.y_position
        },
        'response': {
            'status_code' : response.status_code,
            'text': response.text
        },
        'request' : {
            'payload' : payload
        },
        
    })

def get_map(workspace, room, api_key):
    payload = {
        'spaceId': workspace.workspace_id,
        'mapId': room.room_id,
        'apiKey': api_key
    }
    r = requests.get('https://gather.town/api/getMap', params=payload)
    return r.json()

def set_map(workspace, room, api_key, map_data, delay=0):
    sleep(delay)
    payload = {
        'spaceId': workspace.workspace_id,
        'mapId': room.room_id,
        'apiKey': api_key,
        'mapContent': map_data
    }
    r = requests.post('https://gather.town/api/setMap', json=payload)
    logging.debug('Updated Gather map: %s' % r.text)
    return r, payload