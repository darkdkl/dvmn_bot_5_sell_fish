import requests
import redis
import os
import time
from db_redis_connect import get_database_connection




def get_token():
    db=get_database_connection()
    
        
    if db.get('expired') is None or  int(db.get('expired')) <= int(time.time()):
        data = {
        'client_id':os.environ["MOLTIN_CLIENT_ID"] ,
        'client_secret': os.environ["MOLTIN_CLIENT_SECRET"],
        'grant_type': 'client_credentials',
        }
        response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
        
        expired=response.json()['expires']
        token=response.json()['access_token']
        db.set('expired',expired)
        db.set('access_token',token)
    else:
        token=db.get('access_token').decode("utf-8")
        
    return token
    
    

def get_items(id=None):
    params=None
    headers={'Authorization':f'Bearer {get_token()}'}
    if id:
        params={'id': id,}
    
    response = requests.get('https://api.moltin.com/v2/products', headers=headers,params=params)
    
    return response.json()


   



def add_cart(id,quantity,chat_id):
    headers={'Authorization':f'Bearer {get_token()}'}
    data = {"data": {
        "id": id,
        "type": "cart_item",
        "quantity": quantity             
         }}
    response = requests.post(f'https://api.moltin.com/v2/carts/{chat_id}/items', headers=headers, json=data)
    return response.json()


def get_items_cart(chat_id,bill=None):
    headers={'Authorization':f'Bearer {get_token()}'}
    if bill:
        response = requests.get(f'https://api.moltin.com/v2/carts/{chat_id}', headers=headers)
    else:
        response = requests.get(f'https://api.moltin.com/v2/carts/{chat_id}/items', headers=headers)

    return response.json()


def get_image_url(id_item):
    
    id_image=get_items(id_item)['data'][0]['relationships']['main_image']['data']['id']
    
    
    headers = {
        'Authorization': f'Bearer {get_token()}',
    }

    response = requests.get(f'https://api.moltin.com/v2/files/{id_image}',headers=headers)
    image_url=response.json()['data']['link']['href']
    
   

    return image_url


def delete_item_from_cart(chat_id,id_item):
    

    headers = {
        'Authorization': f'Bearer {get_token()}',
    }

    response = requests.delete(f'https://api.moltin.com/v2/carts/{chat_id}/items/{id_item}', headers=headers)

    return response.json()

def create_customer(name,email):
    headers = {
        'Authorization': f'Bearer {get_token()}',
    }
    data={
        "data": {
        "type": "customer",
        "name": f'{name}',
        "email": f'{email}',}
         }
    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=data)
    if response.ok:
        return response.json()['data']['id']
    else: response.json()


def get_customer(id):
    headers = {'Authorization': f'Bearer {get_token()}'}
    response = requests.get(f'https://api.moltin.com/v2/customers/{id}',headers=headers)
    return response.ok
         
