from flaskproj import db , login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader # decorator to tell flask how to load a user
def load_user(user_id): # used to load a user given the id
    return User.query.get(int(user_id)) # get the current user by id

# User Table
# UserMixin is a class that has default implementations for the methods 
# that Flask-Login expects user objects to have (is_authenticated, is_active, is_anonymous, get_id)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False) # 20 char max, unique, not null
    email = db.Column(db.String(120), unique=True, nullable=False) # 120 char max, unique, not null
    password = db.Column(db.String(60), nullable=False) # 60 char max as it will be hashed, not null
    
    # the following are not actual columns in the table, but they are used to query the database
    friendships = db.relationship('Friend', foreign_keys='Friend.user_id', backref='user', lazy=True) # Friendship.user_id is the foreign key for the user who sent the request
    friend_requests = db.relationship('Friend', foreign_keys='Friend.friend_id', backref='friend', lazy=True) # Friendship.friend_id is the foreign key for the user who received the request
    posts = db.relationship('Post', backref='author', lazy=True) # backref is the name of the attribute that will be added to the objects of the "many" class that points to the "one" object
    
    #------------------------------------------------------------------------------------------------------------------
    # Dunder/magic method to print the object in a more readable way - used for debugging  
    # every time we print the object, this method will be called
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    

    
    @staticmethod
    def get_accepted_friends(user_id):
        accepted_friends = Friend.query.filter_by(user_id=user_id, status='accepted').all()
        friend_ids = [friend.friend_id for friend in accepted_friends]
        friends = User.query.filter(User.id.in_(friend_ids)).all()
        return friends
    
# Friend Table
class Friend(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # user_id is the id of the user who sent the request
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # friend_id is the id of the user who received the request
    status = db.Column(db.String(10), default='pending') # status can be pending, accepted, or declined


        
# Post Table 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100) , nullable=False) 
    content = db.Column(db.Text , nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now()) # default is the current time
    privacy = db.Column(db.Enum('public', 'friends only','only me'), nullable=False)  # privacy can be public or private
    # Tables = lowercase , Class = uppercase
    # notice we use 'user' to refer to the table name 
    # 'Post' to refer to the class name 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # user_id is the id of the user who posted the post