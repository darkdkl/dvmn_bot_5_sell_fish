import requests
import os
import time
from db_redis_connect import get_database_connection


def get_token():
    db = get_database_connection()

    if db.get('expires') is None or int(db.get('expires')) <= int(time.time() + 20):
        data = {
                'client_id': os.environ["MOLTIN_CLIENT_ID"],
                'client_secret': os.environ["MOLTIN_CLIENT_SECRET"],
                'grant_type': 'client_credentials',
                }

        response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
        if response.ok:
            expires = response.json()['expires']
            token = response.json()['access_token']
            db.set('expires', expires)
            db.set('access_token', token)
        else:
            return None
    else:
        token = db.get('access_token').decode("utf-8")

    return token


def get_items(item_id=None):
    params = None
    headers = {'Authorization': f'Bearer {get_token()}'}
    if item_id:
        params = {'id': item_id, }

    response = requests.get('https://api.moltin.com/v2/products', headers=headers, params=params )
    if response.ok:
        return response.json()
    else:
        return None


def add_cart(item_id, quantity, chat_id):
    headers = {'Authorization': f'Bearer {get_token()}'}
    data = {"data": {
        "id": item_id,
        "type": "cart_item",
        "quantity": quantity}
                    }
    response = requests.post(f'https://api.moltin.com/v2/carts/{chat_id}/items', headers=headers, json=data )

    if response.ok:
        return response.json()
    else:
        return None


def get_items_cart(chat_id, bill=None):
    headers = {'Authorization': f'Bearer {get_token()}'}
    if bill:

        response = requests.get(f'https://api.moltin.com/v2/carts/{chat_id}', headers=headers )
        if not response.ok:
            return None
    else:
        response = requests.get(f'https://api.moltin.com/v2/carts/{chat_id}/items', headers=headers )
        if not response.ok:
            return None
    return response.json()


def get_image_url(id_item):

    id_image = get_items(id_item)['data'][0]['relationships']['main_image']['data']['id']

    headers = {'Authorization': f'Bearer {get_token()}'}

    response = requests.get(f'https://api.moltin.com/v2/files/{id_image}', headers=headers)
    if response.ok:
        image_url = response.json()['data']['link']['href']

        return image_url
    else:
        return None


def delete_item_from_cart(chat_id, id_item):

    headers = {'Authorization': f'Bearer {get_token()}'}

    response = requests.delete(f'https://api.moltin.com/v2/carts/{chat_id}/items/{id_item}', headers=headers)
    if response.ok:
        return response.json()
    else:
        return None


def create_customer(name, email):
    headers = {'Authorization': f'Bearer {get_token()}'}
    data = {
            "data": {
                    "type": "customer",
                    "name": f'{name}',
                    "email": f'{email}' 
                    }
           }
    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=data)
    if response.ok:
        return response.json()['data']['id']
    else:
        response.json()


def get_customer(customer_id):
    headers = {'Authorization': f'Bearer {get_token()}'}
    response = requests.get(f'https://api.moltin.com/v2/customers/{customer_id}', headers=headers )
    if response.ok:
        return response.ok
