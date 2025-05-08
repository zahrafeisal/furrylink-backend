#!/usr/bin/env python3

from models import User, Pet, Review, AdoptionApplication
from config import app, db

with app.app_context():
    reviews = []

    review1 = User(
        comment = 'Amazing app',
        user_id = 2
    )

    review2 = User(
        organization_name = 'Animal Shelter', 
        email = 'animalshelter@example.com',  
        telephone = '0767-812-345',  
    )
    
    reviews.append(review1)
    reviews.append(review2)

    db.session.add_all(reviews)
    db.session.commit()
