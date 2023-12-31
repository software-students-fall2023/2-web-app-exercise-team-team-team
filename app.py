from functools import wraps

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from db import get_tasks_collection, insert_user, get_user_from_db

# comment out all stuff related to login/register
app = Flask(__name__, static_folder='public')
app.secret_key = '059763067224cfd60c9260a509447c10ac25b5a6562f75ed'

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


@app.route('/change_view')
def change_view():
    tasks = tasks_collection.find()

    return render_template('change_view.html', tasks=tasks)


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


@app.route('/search', methods=['GET', 'POST'])
def search_task():
    if request.method == 'POST':
        title = request.form['title']
        progress = request.form['progress']
        pinned = True if request.form['pinned'] == 'true' else False
        priority = int(request.form['priority'])

        query = {}
        if title:
            query['title'] = title
        elif progress:
            query['progress'] = {'$regex': progress, '$options': 'i'}
        elif pinned:
            query['pinned'] = pinned
        elif priority:
            query['priority'] = priority
        else:
            print("An error occurred")

        tasks = tasks_collection.find(query)
        return render_template('search_results.html', tasks=tasks)

    return render_template('search_task.html')


@app.route('/edit')
def edit_tasks_list():
    tasks = tasks_collection.find()  # Assuming you have a tasks_collection object connected to your database
    return render_template('edit.html', tasks=tasks)


@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])  # added '<task_id>' dynamic part to the route
def edit_task(task_id):
    task = tasks_collection.find_one({"_id": ObjectId(task_id)})

    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('home'))  # or wherever you list your tasks

    if request.method == 'POST':
        # Gather data from the form
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        due_date = request.form.get('due_date')
        tags = request.form.get('tags').split(',')
        progress = request.form.get('progress')
        pinned = True if request.form.get('pinned') == 'true' else False

        # Update the task in the database
        tasks_collection.update_one({"_id": ObjectId(task_id)}, {
            "$set": {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date,
                "tags": tags,
                "progress": progress,
                "pinned": pinned
            }
        })

        flash('Task updated successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('edit_task.html', task=task)


@app.route('/public/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=47218, debug=True)
