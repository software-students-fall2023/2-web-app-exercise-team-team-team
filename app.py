from functools import wraps

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from bson.objectid import ObjectId
from datetime import datetime
from db import get_tasks_collection, insert_user, get_user_from_db
# comment out all stuff related to login/register
app = Flask(__name__, static_folder='public')
# app.secret_key = '059763067224cfd60c9260a509447c10ac25b5a6562f75ed'

# Connect to db.py
tasks_collection = get_tasks_collection()


# # check if user is already in session
# @app.route('/')
# def index():
#     if 'user_id' in session:
#         return redirect(url_for('home'))
#     return redirect(url_for('login'))


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = get_user_from_db(username, password)
#         if user:
#             session['user_id'] = user['_id']  # Store user ID in the session
#             return redirect(url_for('home'))
#         else:
#             return "Invalid credentials", 401
#     return render_template('login.html')
#

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     return redirect(url_for('login'))


# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#
#     return decorated_function


@app.route('/')
# @login_required
def home():
    # Default sorting criteria
    sort_by = "due_date"
    sort_order = 1
    if 'sort-by' in request.args:
        if request.args['sort-by'] == 'priority':
            sort_by = 'priority'
    if 'sort-order' in request.args and request.args['sort-order'] == 'desc':
        sort_order = -1

    tasks = tasks_collection.find().sort(sort_by, sort_order)

    return render_template('home.html', tasks=tasks)


@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        due_date = request.form['due_date']
        pinned = True if request.form['pinned'] == 'true' else False
        tags = request.form['tags'].split(",")
        progress = request.form['progress']

        # Convert due_date from string to datetime object
        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')

        try:
            tasks_collection.insert_one({
                'title': title,
                'description': description,
                'priority': int(priority),
                'due_date': due_date_obj,
                'pinned': pinned,
                'tags': tags,
                'progress': progress
            })
        except Exception as e:
            print(f"An error occurred: {e}")
            return "Error adding task.", 500

        return redirect(url_for('home'))

    return render_template('add_task.html')


# @app.route('/register', methods=['GET', 'POST'])
# def acc_register():
#     if request.method == 'POST':
#
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#         try:
#             result = insert_user(username, password, email)
#
#             if result:
#                 # registration success
#                 return redirect(url_for('login'))
#
#             else:
#                 # error during registration
#                 return "Error registering account.", 500
#
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return "Error inputing account information.", 500
#
#     return render_template('acc_register.html')
#

@app.route('/delete', methods=['GET'])
def display_delete_page():
    tasks = tasks_collection.find()
    return render_template('delete_task.html', tasks=tasks)


@app.route('/delete/<task_id>', methods=['GET'])
def delete_task(task_id):
    try:
        tasks_collection.delete_one({"_id": ObjectId(task_id)})
        return redirect(url_for('display_delete_page'))
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error deleting task.", 500


@app.route('/public/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=47218, debug=True)
