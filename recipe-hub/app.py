from flask import Flask, render_template, redirect, url_for, request, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'bb3userbb3userbb3userbb3user'

# File paths for storing recipes, users, and comments
RECIPES_FILE = 'recipes.json'
USERS_FILE = 'users.json'
COMMENTS_FILE = 'comments.json'

# Load the data Basic
def load_data(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return default

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)

# Initialize data Basic
recipes = load_data(RECIPES_FILE, [])
users = load_data(USERS_FILE, {})
comments = load_data(COMMENTS_FILE, {})

@app.route('/')
def home():
    title = session.get('title', "The Recipe Hub")
    return render_template('home.html', title=title)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            users[username] = password
            save_data(USERS_FILE, users)
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            session['is_admin'] = (username == 'admin')
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Ah ah ah not the magic words. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/update_title', methods=['POST'])
def update_title():
    if 'logged_in' in session and session.get('is_admin'):
        session['title'] = request.form['title']
    return redirect(url_for('home'))

@app.route('/recipes')
def recipes_blog():
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    if recipe_id < 0 or recipe_id >= len(recipes):
        return redirect(url_for('recipes_blog'))

    recipe = recipes[recipe_id]
    recipe_comments = comments.get(recipe_id, [])

    if request.method == 'POST':
        if 'logged_in' not in session:
            flash('You need to log in to post a comment.', 'error')
            return redirect(url_for('login'))

        new_comment = {
            'username': session['username'],
            'comment': request.form['comment']
        }
        recipe_comments.append(new_comment)
        comments[recipe_id] = recipe_comments
        save_data(COMMENTS_FILE, comments)  # This is how to save the comments to file

    return render_template('view_recipe.html', recipe=recipe, comments=recipe_comments)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if 'logged_in' not in session:
        flash('You need to log in to post a recipe.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_recipe = {
            'title': title,
            'content': content,
            'username': session['username']  # Use the session that we created
        }
        recipes.append(new_recipe)
        save_data(RECIPES_FILE, recipes)
        return redirect(url_for('recipes_blog'))

    return render_template('add_recipe.html')

if __name__ == '__main__':
    app.run(debug=True)
