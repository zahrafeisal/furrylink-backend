#!/usr/bin/env python3

from models import User, Pet, Review, AdoptionApplication
from config import app, db

with app.app_context():
    users = []

    user1 = User(
        first_name = 'Alice',  
        last_name = 'Smith',  
        email = 'alice@example.com',  
        telephone = '0712-345-678',  
    )
    user1.password_hash = 'password123'

    user2 = User(
        organization_name = 'Animal Shelter', 
        email = 'animalshelter@example.com',  
        telephone = '0767-812-345',  
    )
    user2.password_hash = 'password456'
    
    users.append(user1)
    users.append(user2)

    db.session.add_all(users)
    db.session.commit()
