import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

import configparser

# Read config
config = configparser.ConfigParser()
config.read('app/constants/config.ini')

# Init Firebase App
try:
    cred = credentials.Certificate(config['Main']['DATABASE_ACCOUNT_FILE'])
    firebase_admin.initialize_app(cred, {
        "databaseURL": 'database_url'
    })
    
except Exception as e:
    print(f"Error initialising database: {e}")

# Add data to a collection
def add_data(ref: str, id: int, data: dict):
    try:
        db.reference(ref).child(str(id)).set(data)

    except Exception as e:
        return e


# Get data by ID
def get_data(ref: str, id: int) -> dict:
    _ref = db.reference(f'{ref}/{str(id)}')
    doc = _ref.get()
    return doc if not None else []

# Update document
def update_data(group_id: int, data: dict) -> None:
    group_ref = db.reference(f'groups/{str(group_id)}')
    group_ref.update(data)


# Delete document
def delete_data(ref: str, id: int):
    group_ref = db.reference(f"{ref}/{str(id)}")
    group_ref.delete()

# Get all document  
def get_all(name: str) -> dict:
    ref = db.reference(name)
    docs = ref.get() 

    return docs if docs else {}