#!/usr/bin/env python3

import os
from flask import request, make_response, session, send_from_directory, jsonify
from flask_restful import Resource
from werkzeug.utils import secure_filename  
from werkzeug.exceptions import BadRequest  
from models import User, Pet, Review, AdoptionApplication

from config import app, db, api


class Login(Resource):
    def post(self):  
        user_data = request.get_json()  
        email = user_data['email'] 
        password = user_data['password']

        # Query the user by email  
        user = User.query.filter(User.email == email).first()  
        
        if user:  
            # Check if the password matches 
            if user.authenticate(password):  
                session['user_id'] = user.id  
                response = make_response(  
                    user.to_dict(),  
                    200  
                )  
                return response  
            else:  
                # Password is incorrect  
                response_body = {'message': 'Incorrect password.'}  
                response = make_response(  
                    response_body,  
                    401
                )  
                return response  
        else:  
            # User does not exist  
            response_body = {'message': 'User does not exist.'}  
            response = make_response(  
                response_body,  
                404   
            )  
            return response  


class CheckSession(Resource):
    # checks if user is logged in on refresh
    def get(self):  
        user_id = session.get('user_id')  
        if user_id:  # First, check if user_id exists in the session  
            user = User.query.filter(User.id == user_id).first()
            
            if user:  
                response = make_response(user.to_dict(), 200)  # This will work now  
                return response  

        # If we fail to find the user or no user_id is set  
        response_body = {'message': 'Please log in.'}  
        response = make_response(response_body, 401)  
        return response  


class Logout(Resource):
    # delete cookie
    def delete(self):
        if 'user_id' not in session:
            response = make_response(
                {"message": "User not authorized."},
                401
            )
            return response
        
        session['user_id'] = None      # reset user id to none
        
        response_body = {'message': 'Logout successful.'}
        response = make_response(
            response_body,
            204
        )
        return response


class Users(Resource):
    def post(self):
        # allow users to sign up
        user_data = request.get_json()
        email = user_data['email']
        existing_user = User.query.filter(User.email == email).first()   # checks if user already exists

        if existing_user:
            response_body = {
                'message': 'User already exists.'
            }
            response = make_response(
                response_body,
                400
            )
            return response
        else:
            new_user = User(
                first_name=user_data['firstName'],
                last_name=user_data['lastName'],
                email=email,
                telephone=user_data['telephone'],
                animal_shelter=user_data['animalShelter'],
                organization_name=user_data['organizationName'],
            )

            new_user.password_hash = user_data['password']  # set pass
            
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id   # log the user in automatically

            response = make_response(
                new_user.to_dict(),
                201
            )
            return response


class UserByID(Resource):
    def patch(self, id):    # edit email and/or name
        user_data = request.get_json()
        user = User.query.filter(User.id == id).first()
        session['user_id'] = user.id

        if not user:
            response = make_response(
                {
                    "message": "User not found."
                },
                404
            )
            return response

        for attr, value in user_data.items():
            setattr(user, attr, value)

        db.session.add(user)
        db.session.commit()

        response = make_response(
            jsonify(user.to_dict()),
            200
        )
        return response

        
class Pets(Resource):
    def get(self):
        # view all pets
        pets = []  
        # base_url = "/uploads"

        for pet in Pet.query.all():
            pet_dict = pet.to_dict()
            # pet_dict['image_filename'] = base_url + pet_dict['image_filename']  # Ensure full path is set  
            pets.append(pet_dict)

        if pets:
            response = make_response(
                jsonify(pets),
                200
            )
            return response
        else :
            response_body = {
                "message": "No pets found."
            }
            response = make_response(
                response_body,
                404
            )
            return response

    def post(self):
        # Allowed file extension function  
        def allowed_file(filename):  
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']  
        
        if 'user_id' not in session:  
            return make_response({'message': 'Unauthorized'}, 401)  
        
        print("Form Data:", request.form)  # Log form data  
    
        animal_type = request.form.get('animalType')  # Use get() safely  
        breed = request.form.get('breed')  
        age = request.form.get('age')  
        price = request.form.get('price')  

        # add a pet for adoption
        new_pet = Pet(  
            type=animal_type,
            breed=breed,
            age=age,
            price=price,  
            user_id=session.get('user_id')
        )  

        # Handle file upload  
        if 'image_filename' not in request.files:  
            raise BadRequest("No file part")  

        image_file = request.files['image_filename']  

        # Check if no file was submitted  
        if image_file.filename == '':  
            raise BadRequest("No file selected")  

        # Check if the file is allowed  
        if image_file and allowed_file(image_file.filename):  
            filename = secure_filename(image_file.filename)  
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  
            # new_pet.image_filename = f"/uploads/{filename}" 
            new_pet.image_filename = filename
        else:  
            raise BadRequest("File type not allowed")  

        # Save new pet to the database  
        db.session.add(new_pet)  
        db.session.commit()  

        response = make_response(
            new_pet.to_dict(),
            201
        )
        return response
    

class UploadImages(Resource):
    def get(self, filename):
        return send_from_directory('/opt/render/project/src/uploads', filename)


class PetByID(Resource):  
    def delete(self, id):  # allow users to delete pets they put up for adoption, WHEN ADOPTED (ADOPTED button)
        deleted_pet = Pet.query.filter(Pet.id == id).first()

        if not deleted_pet:
            response = make_response(
                {
                    "message": "No pet found."
                },
                404
            )
            return response

        db.session.delete(deleted_pet)
        db.session.commit()

        response = make_response(
            {
                "message": "Pet deleted successfully!"
            },
            204
        )
        return response
        

class Reviews(Resource):
    def get(self):
        # allow users to view all reviews
        reviews = []

        for review in Review.query.all():
            review_dict = review.to_dict()
            reviews.append(review_dict)

        if not reviews:
            response = make_response(
                {
                    "message": "No reviews found."
                },
                404
            )
            return response
        
        response = make_response(
            jsonify(reviews),
            200
        )
        return response

    def post(self):    # allow users to post a review
        if 'user_id' not in session:
            response = make_response(
                {
                    "message": "User not authorized."
                },
                401
            )
            return response
        
        reviewData = request.get_json()
        new_review = Review(
            comment=reviewData['comment'],
            user_id=session['user_id']
        )

        db.session.add(new_review)
        db.session.commit()

        response = make_response(
            new_review.to_dict(),
            201
        )
        return response
    

class Applications(Resource):
    def get(self):
        if 'user_id' not in session:
            response = make_response(
                {
                    "message": "User not authorized."
                },
                401
            )
            return response
        
        applications = []

        for app in AdoptionApplication.query.all():
            app_dict = app.to_dict()
            applications.append(app_dict)

        if not applications:
            response = make_response(
                {
                    "message": "No applications found."
                },
                404
            )
            return response
        
        response = make_response(
            jsonify(applications),
            200
        )
        return response
            
    def post(self):
        if 'user_id' not in session:
            response = make_response(
                {
                    "message": "User not authorized."
                },
                401
            )
            return response
        
        data = request.get_json()
        pet_id = data['petID']
        new_application = AdoptionApplication(
            description=data['description'],
            user_id=session.get('user_id'),
            pet_id=pet_id
        )
        
        db.session.add(new_application)
        db.session.commit()

        response = make_response(
            new_application.to_dict(),
            201
        )
        return response


class ApplicationByID(Resource):  
    def patch(self, id):  
        user_id = session.get('user_id')  
        application = AdoptionApplication.query.filter(
            AdoptionApplication.id == id
        ).first()

        if not application:  
            return make_response({"message": "Application not found."}, 404) 
        
        pet = application.pet  

        if not user_id or pet.user_id != user_id:  
            return make_response({"message": "Not authorized."}, 401)
        
        data = request.get_json()  
        new_status = data.get('status')  

        if new_status not in ['Pending', 'Approved', 'Rejected']:  
            return {"message": "Invalid status."}, 400  
        
        application.status = new_status  
        db.session.commit()  
        return make_response(application.to_dict(), 200)
    

@app.route('/check-uploads-directory')
def check_uploads_directory():
    uploads_dir = os.path.join(app.root_path, 'uploads')
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        return jsonify({
            'exists': True,
            'files': files,
            'path': uploads_dir
        })
    else:
        return jsonify({ 'exists': False, 'message': 'Uploads directory does not exist.' })


api.add_resource(Login, '/login')   # done
api.add_resource(CheckSession, '/check_session')   # done
api.add_resource(Logout, '/logout')   # done
api.add_resource(Users, '/users')   # done
api.add_resource(UserByID, '/user/<int:id>') # done
api.add_resource(Pets, '/pets')    # done
api.add_resource(UploadImages, '/uploads/<path:filename>')   # done
api.add_resource(PetByID, '/pet/<int:id>')  # done
api.add_resource(Reviews, '/reviews')  # done
api.add_resource(Applications, '/applications')
api.add_resource(ApplicationByID, '/application/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
