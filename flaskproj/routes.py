from flask import render_template, redirect, url_for, flash , request , Blueprint , abort
from flaskproj import app , db , bcrypt
from flaskproj.forms import RegisterForm, LoginForm , PostForm , EditProfile , FriendRequestForm 
from flaskproj.models import User , Post , Friend
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users',__name__,url_prefix='/users')
@app.route('/home')
@login_required # this decorator will redirect to login page if the user is not logged in
def home():
    endpoint_title = 'Home Page'
    return render_template('home.html',context={'title':endpoint_title})

@app.route('/about')
@login_required
def about():
    endpoint_title = 'About Page'
    return render_template('about.html',context={'title':endpoint_title})

@app.route('/register', methods=['GET','POST'])
def register():
    endpoint_title = 'Register Page'
    form = RegisterForm()
    if form.validate_on_submit():
        with app.app_context():
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw
            )
            db.session.add(new_user)
            db.session.commit()
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('login'))
        
    return render_template('register.html',context={'title':endpoint_title,'form':form})

    
@app.route('/login', methods=['GET','POST'])
def login():  # sourcery skip: remove-redundant-fstring
    if current_user.is_authenticated:
        return redirect(url_for('posts', mode='all'))
    
    endpoint_title = 'Login Page'
    form = LoginForm()
    if form.validate_on_submit():
        with app.app_context():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                flash(f'Welcome {user.username}!','success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('posts')) # redirect to next page if it exists
              
            else:
                flash(f'Login Unsuccessful. Please check username and password','danger')
                return redirect(url_for('login'))
        
    return render_template('login.html',context={'title':endpoint_title,'form':form})


@app.route('/logout')
def logout():  
    logout_user()
    return redirect(url_for('posts', mode='all'))
    
    
# -------------------------------- Post routes --------------------------------
# add/Edit post page
@users.route('/add_post', methods=['GET', 'POST'])
@users.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def add_post(post_id=None):
    # Check if a post_id is provided for editing an existing post
    if post_id:
        post = Post.query.get_or_404(post_id)
        form = PostForm(obj=post)
    else:
        form = PostForm()

    if form.validate_on_submit():
        if post_id:
            post.title = form.title.data
            post.content = form.content.data
            post.privacy = form.privacy.data
        else:
            title = form.title.data
            content = form.content.data
            privacy = form.privacy.data

            # Create a new post
            post = Post(title=title, content=content, privacy=privacy, author=current_user)
            db.session.add(post)

        db.session.commit()

        flash('Post created/updated successfully!', 'success')
        return redirect(url_for('posts', mode='all'))

    return render_template('add_post.html',context = {'form':form,'post_id':post_id})

# Delete post
@users.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # Return a forbidden error if the current user is not the author of the post
    db.session.delete(post)
    db.session.commit()

    flash('Post deleted successfully!', 'success')
    return redirect(request.referrer)


# Get post page
@app.route('/', defaults={'mode': 'all'}, methods=['GET'])
@app.route('/posts/', defaults={'mode': 'all'}, methods=['GET'])
@app.route('/posts/<mode>', methods=['GET'])
@login_required
def posts(mode):
    if mode == 'all':
        # Retrieve all posts
        posts = Post.query.filter(Post.privacy == 'public').all()
    elif mode == 'friends':
        # Retrieve posts from friends only
        friends = current_user.friendships
        friend_ids = [friend.friend_id for friend in friends if friend.status == 'accepted']
        posts = Post.query.filter(Post.user_id.in_(friend_ids), Post.privacy != 'only me').all()
    else:
        # Invalid mode
        flash('Invalid post mode.', 'error')
        return redirect(url_for('posts', mode='all'))

    return render_template('posts.html', context = {'posts':posts})



# ------------------------------------- User routes -------------------------------------
# user profile page
@users.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    friends = user.get_accepted_friends(user_id)
    count = len(friends)
    posts = user.posts
    endpoint_title = 'Profile Page'
    return render_template('profile.html', context={'title': endpoint_title, 'posts': posts, 'user': user , 'friends':friends, 'count':count})


# user edit profile page
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    endpoint_title = 'Edit Profile'
    user = User.query.get_or_404(current_user.id)
    form = EditProfile(obj=user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        # Update other relevant user information
        if bcrypt.check_password_hash(user.password,form.password.data):
            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('users.profile', user_id=current_user.id))
        else:
            flash('Your password is incorrect!', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('edit_profile.html', context={'title':endpoint_title,'form':form})

    




@app.route('/users')
@login_required
def display_users():
    all_users = User.query.all()  # get all users
    friend_ids = [friend.friend_id if friend.user_id == current_user.id else friend.user_id for friend in current_user.friendships if friend.status == 'accepted']  # get IDs of current user's friends with status 'accepted'
    user = [user for user in all_users if user != current_user and user.id not in friend_ids]  # filter out current user and friends
    form = FriendRequestForm() 

    # Get list of friend requests sent by the current user that are still pending
    sent_requests = [friend.friend for friend in current_user.friendships if friend.status == 'pending']

    # Get list of friend requests received by the current user that are still pending
    pending_friends = [friend.user for friend in current_user.friend_requests if friend.status == 'pending']

    endpoint_title = 'Users Page'
    return render_template('users.html', context={
        'title': endpoint_title,
        'user': user,
        'form': form,
        'sent_requests': sent_requests,
        'pending_friends': pending_friends
    })
@app.route('/users/<int:friend_id>/send_request', methods=['POST'])
@login_required
def send_request(friend_id):
    user = User.query.get(friend_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('display_users'))
    form = FriendRequestForm()
    if form.validate_on_submit():
        friend = Friend(user_id=current_user.id, friend_id=user.id, status='pending')
        db.session.add(friend)
        db.session.commit()
        flash(f'Friend request sent to {user.username}.')
        return redirect(url_for('display_users'))
    else:
        flash('Error sending friend request.')
        return redirect(url_for('display_users'))

@app.route('/friends')
@login_required
def view_friends():
    # Get the friend requests where the friend_id matches the ID of the logged-in user
    friend_requests = Friend.query.filter_by(friend_id=current_user.id, status='pending').all()
    # Get the users who have sent friend requests to the logged-in user
    users = [request.user_id for request in friend_requests]
    # Query for the user objects
    friends = User.query.filter(User.id.in_(users)).all()
    endpoint_title = 'Friends Page'
    return render_template('friend.html', context={'title': endpoint_title, 'friends': friends})

@app.route('/friends/<int:friend_id>/accept', methods=['POST'])
@login_required
def accept_friend_request(friend_id):
    friend = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.id).first()
    if friend is None:
        flash('Friend request not found.')
        return redirect(url_for('view_friends'))
    friend.status = 'accepted'
    db.session.commit()

    # Add the friend to current user's list of friends
    new_friend = Friend(user_id=current_user.id, friend_id=friend.user.id, status='accepted')
    db.session.add(new_friend)
    db.session.commit()

    flash(f'You are now friends with {friend.user.username}.')
    

    return redirect(url_for('view_friends'))
@app.route('/friends/<int:friend_id>/reject', methods=['POST'])
@login_required
def reject_friend_request(friend_id):
    friend = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.id).first()
    if friend is None:
        flash('Friend request not found.')
        return redirect(url_for('view_friends'))
    friend.status = 'rejected'
    db.session.commit()
    flash(f'You have rejected the friend request from {friend.user.username}.')
    return redirect(url_for('view_friends'))


@app.route('/friends/list')
@login_required
def view_friends_list():
    friends = User.query.join(Friend, User.id == Friend.friend_id).filter(Friend.user_id == current_user.id, Friend.status == 'accepted').all()
    endpoint_title = 'Friends List'
    return render_template('friendlist.html', context={'title': endpoint_title, 'friends': friends})
