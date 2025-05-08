from sqlalchemy.ext.hybrid import hybrid_property  
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime  

from config import db, bcrypt

class User(db.Model, SerializerMixin):  # one to many with Pet  
    __tablename__ = 'users'  

    serialize_rules = ('-pets_added.user', '-applications.user', '-reviews.user',)

    id = db.Column(db.Integer, primary_key=True)  
    first_name = db.Column(db.String, nullable=True)  # Nullable to accommodate shelters  
    last_name = db.Column(db.String, nullable=True)    # Nullable to accommodate shelters  
    email = db.Column(db.String, unique=True, nullable=False)  # one user, one email  
    telephone = db.Column(db.String, unique=True, nullable=False) # one user, one telephone
    animal_shelter = db.Column(db.Boolean, default=False)  # Determine if user is a shelter or just an individual  
    organization_name = db.Column(db.String, nullable=True)  # New field for animal shelters  
    _password_hash = db.Column(db.String, nullable=False)  
    
    # Relationships  
    pets_added = db.relationship('Pet', back_populates='user') 
    applications = db.relationship('AdoptionApplication', back_populates='user')  
    reviews = db.relationship('Review', back_populates='user')

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))  

    def __repr__(self):  
        return f"<User {self.first_name} {self.last_name} - {self.organization_name}>"  


class Pet(db.Model, SerializerMixin): 
    __tablename__ = 'pets'

    serialize_rules = ('-user.pets_added', '-applications.pet',)

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    breed = db.Column(db.String)
    age = db.Column(db.String)
    price = db.Column(db.String)
    image_filename = db.Column(db.String)    # allow users to upload pet photo
    
    # foreign keys for user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
    
    # Relationships  
    user = db.relationship('User', back_populates='pets_added')
    applications = db.relationship('AdoptionApplication', back_populates='pet')


class Review(db.Model, SerializerMixin):    # one to many rlship w user
    __tablename__ = 'reviews'

    serialize_rules = ('-user.reviews',)

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    comment = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))    # foreign key for user

    # Relationships  
    user = db.relationship('User', back_populates='reviews')


class AdoptionApplication(db.Model, SerializerMixin):
    __tablename__ = 'adoption_applications'

    serialize_rules = ("-pet.applications", "-user.applications",)

    id = db.Column(db.Integer, primary_key=True)  
    description= db.Column(db.String)     # describe why they would like to adopt the pet
    status = db.Column(db.String, default='Pending')  # Status of the application (e.g., Pending, Approved, Rejected)  
    created_at = db.Column(db.DateTime, default=datetime.now)  # Timestamp of when the application was created  

    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)  # Reference to the pet being applied for  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Reference to the user applying  

    # Relationships  
    pet = db.relationship('Pet', back_populates='applications')  
    user = db.relationship('User', back_populates='applications')  
