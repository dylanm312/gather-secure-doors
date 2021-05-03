from django.conf import settings
from django.http import Http404
from django.urls import reverse
from threading import Thread
from time import sleep

import copy
import requests
import logging
import base64


logging.basicConfig(filename=settings.LOG_FILE, level=logging.DEBUG)


def find_door(map_dict, door):
    '''Returns the map['objects'] index for door. -1 if not found'''
    for i, obj in enumerate(map_dict['objects']):
        if (obj['x'] == door.x_position and obj['y'] == door.y_position):
            return i
            break
    else:
        return -1


def get_door_image_urls(door):
    '''Returns image url or blank'''
    urls = {}
    if door.open_image:
        urls['open'] = door.open_image.url
    else:
        urls['open'] = ''
    if door.closed_image:
        urls['closed'] = door.closed_image.url
    else:
        urls['closed'] = ''
    return urls


def init_door(door):
    door_image_urls = get_door_image_urls(door)

    door_url = settings.FQDN + reverse('doorLogin', kwargs={
        'workspace_slug': door.room.workspace.workspace_slug,
        'room_slug': door.room.room_slug,
        'door_slug': door.door_slug})

    logging.debug('Got workspace, room, door, and API key')
    logging.debug('Door image urls: ')
    logging.debug(door_image_urls)

    logging.debug('Door url:')
    logging.debug(door_url)

    # Get the current map state
    map_data = get_map(door.room.workspace, door.room, door.room.workspace.api_key)
    old_map_data = copy.deepcopy(map_data)

    logging.debug('Got current map state')

    # Look for the door on the map. If we find it, return
    if find_door(map_data, door) != -1:
        logging.debug('Door already found at X: %d, Y: %d' % (door.x_position, door.y_position))
        return False

    # If we couldn't find the door, create it
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

    # ##### Send the update to Gather ######
    response, payload = set_map(
        door.room.workspace,
        door.room,
        door.room.workspace.api_key,
        map_data)

    logging.debug('Response summary (init_door):')
    logging.debug({
        'workspace': door.room.workspace.workspace_id,
        'room': door.room.room_id,
        'door': door.door_slug,
        'api_key': door.room.workspace.api_key,
        'door_pos': {
            'x': door.x_position,
            'y': door.y_position
        },

        'response': {
            'status_code': response.status_code,
            'text': response.text
        },
    })


def unlock_door(door):
    logging.basicConfig(filename=settings.LOG_FILE, level=logging.DEBUG)
    door_image_urls = get_door_image_urls(door)
    door_url = settings.FQDN + reverse('doorLogin', kwargs={
        'workspace_slug': door.room.workspace.workspace_slug,
        'room_slug': door.room.room_slug,
        'door_slug': door.door_slug})

    logging.debug('Got workspace, room, door, and API key')
    logging.debug('Door image urls: ')
    logging.debug(door_image_urls)

    logging.debug('Door url:')
    logging.debug(door_url)

    # Get the current map state
    map_data = get_map(door.room.workspace, door.room, door.room.workspace.api_key)
    old_map_data = copy.deepcopy(map_data)

    logging.debug('Got current map state')

    # ##### Find the door object, change its image, and store the old object ######

    # Look for the door on the map. If we find it, open it in map_data, and cache the closed door in old_map_data
    index = find_door(map_data, door)
    if index != -1:
        logging.debug('Found door at X: %d, Y: %d' % (door.x_position, door.y_position))
        map_data['objects'][index]['normal'] = door_image_urls['open']
        map_data['objects'][index]['highlighted'] = door_image_urls['open']
        old_map_data['objects'][index]['normal'] = door_image_urls['closed']
        old_map_data['objects'][index]['highlighted'] = door_image_urls['closed']

    # If we couldn't find the door, create it
    else:
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

    # ##### Get rid of the impassable tile ######

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

    # ##### Send the update to Gather ######
    response, payload = set_map(
        door.room.workspace,
        door.room,
        door.room.workspace.api_key,
        map_data)

    if response.status_code == 200:
        # Wait 180 seconds and then close/lock the door
        t = Thread(target=set_map, args=(
            door.room.workspace,
            door.room,
            door.room.workspace.api_key,
            old_map_data,
            180))
        t.start()

    logging.debug('Response summary (unlock_door):')
    logging.debug({
        'workspace': door.room.workspace.workspace_id,
        'room': door.room.room_id,
        'door': door.door_slug,
        'api_key': door.room.workspace.api_key,
        'door_pos': {
            'x': door.x_position,
            'y': door.y_position
        },

        'response': {
            'status_code': response.status_code,
            'text': response.text
        },
    })


def delete_door(door):

    logging.basicConfig(filename=settings.LOG_FILE, level=logging.DEBUG)

    # Get the current map state
    map_data = get_map(door.room.workspace, door.room, door.room.workspace.api_key)

    # Find and remove the door
    index = find_door(map_data, door)
    if index != -1:
        logging.debug('Found door at X: %d, Y: %d' % (door.x_position, door.y_position))
        del map_data['objects'][index]
        logging.debug('Door deleted from map')
    else:
        logging.debug('Could not find door to delete')

    # ##### Get rid of the impassable tile ######

    # Change the impassable tile to normal in the new map data
    collision_buffer = bytearray(base64.b64decode(map_data['collisions']))
    for dx in range(door.width):
        for dy in range(door.height):
            collision_buffer[
                (door.y_position + dy) * map_data['dimensions'][0] + door.x_position + dx
            ] = 0x00

    map_data['collisions'] = base64.b64encode(collision_buffer).decode('ascii')
    logging.debug('Changed impassable tile to normal')

    # ##### Send the update to Gather ######
    response, payload = set_map(
        door.room.workspace,
        door.room,
        door.room.workspace.api_key,
        map_data)

    logging.debug('Response summary (delete_door):')
    logging.debug({
        'workspace': door.room.workspace.workspace_id,
        'room': door.room.room_id,
        'door': door.door_slug,
        'api_key': door.room.workspace.api_key,
        'door_pos': {
            'x': door.x_position,
            'y': door.y_position
        },
        'response': {
            'status_code': response.status_code,
            'text': response.text
        },
    })


def get_map(workspace, room, api_key):
    '''Returns map as a dictionary'''
    payload = {
        'spaceId': workspace.workspace_id,
        'mapId': room.room_id,
        'apiKey': api_key
    }
    r = requests.get('https://gather.town/api/getMap', params=payload)
    if r.status_code == 200:
        return r.json()
    else:
        logging.error('get_map failed (url={}, content={})'.format(r.url, r.content))
        raise Http404


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
