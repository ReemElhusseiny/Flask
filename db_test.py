from flaskproj.models import User, Post, Friend  
from flaskproj import app, db
import sys

# --------------------------------------- DATABASE OPERATIONS ---------------------------------------
# Create database
def create_db():
    with app.app_context(): # this is needed to create the database
        db.create_all() # create the database tables from the models
        print('Database created')
        
# Drop database
def drop_db():
    with app.app_context():
        db.drop_all() # drop all the database tables
        print('Database dropped')

# --------------------------------------------------------------------------------------------------


# --------------------------------------- CRUD OPERATIONS ------------------------------------------

# --------------------------------------- Create Operation ------------------------------------------
# Create User
def create_user():
    with app.app_context():
        new_user = User(username='John', email='yahia@gmail.com', password='123')
        db.session.add(new_user)
        db.session.commit()

# Create Post
def create_post():
    with app.app_context():
        user = User.query.first()
        post_1 = Post(title='First Post', content='Hello World', privacy='public',user_id=user.id)
        post_2 = Post(title='second Post', content='this is private post test', privacy='private',user_id=user.id)
        db.session.add(post_1)
        db.session.add(post_2)
        db.session.commit()

# --------------------------------------- Read Operation ------------------------------------------

# Read User
def read_user():
    with app.app_context():
        # users = User.query.all() # get all users
        # for user in users:
        #     print(user)
        
        # ------------------- Query Filters -------------------
        # user = User.query.filter_by(username='John').first() # get the first user with username = 'John'
        
        # ------------------- Join Query -------------------
        query = db.session.query(
            Post,
            User
        ).join(User, Post.user_id == User.id)\
        .filter(Post.privacy == 'public')\
        .order_by(Post.date_posted.desc())\
        .all()
        for item in query:
            print(item)


# --------------------------------------- Update Operation ------------------------------------------
# Update users
def update_users():
    with app.app_context():
        user = User.query.filter_by(username='John').first()
        user.username = 'Yahia'
        db.session.commit()
        
# --------------------------------------- Delete Operation ------------------------------------------
# Delete Posts
def delete_posts():
    with app.app_context():
        post = Post.query.filter_by(title='First Post').first()
        db.session.delete(post)
        db.session.commit()




if __name__ == '__main__':
    globals()[sys.argv[1]]() # run the function specified in the command line argument 