from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__, static_folder='public')

# Connect to db.py
tasks_collection = get_tasks_collection()

@app.route('/')
def home():
    tasks = tasks_collection.find()
    return render_template('home.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        due_date = request.form['due_date']
        
        tasks_collection.insert_one({
            'title': title,
            'description': description,
            'priority': priority,
            'due_date': due_date
        })
        
        return redirect(url_for('home'))
    
    return render_template('add_task.html')

@app.route('/public/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
