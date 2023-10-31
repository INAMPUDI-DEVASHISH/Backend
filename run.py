from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

# Flask Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2000@localhost/new'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'} # no doc

db = SQLAlchemy(app)
jwt = JWTManager(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/')
def project():
    return 'Project By Devashish and Pavan'

    
#Since we have planned to do the project based on To do List we made sure the public can access the login page and their data can only be accessed admin protected route 
# The public can just see the tasks present in the To Do List. Update, Delete and Creating tasks are doing using protected endpoints for safety

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }

# Error Handling
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error='Bad request'), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error='Unauthorized'), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify(error='Not found'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(error='Internal server error'), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify(error='File too large'), 413

# Authentication and Public route since they can access it
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify(error="Invalid username or password"), 401


# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created', 'user': new_user.serialize()}), 201

# Retrieve all users and jwt_required() implies protected in our project ADMIN ROUTE
@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

# Retrieve a single user
@app.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.serialize()), 200

# Update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.password = data['password']
    db.session.commit()
    return jsonify({'message': 'User updated', 'user': user.serialize()}), 200


# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

       


# File Handling
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400
    file = request.files['file']
    if file.filename == '':
                return jsonify(error="No selected file"), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify(message="File uploaded!", file_path=file_path), 201
    return jsonify(error="File type not allowed"), 400

# Public Route for Tasks
@app.route('/publictasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.filter_by(is_public=True).all()
    return jsonify(tasks=[task.serialize() for task in tasks]), 200

# Admin Route for Tasks
@app.route('/admintasks', methods=['POST'])
@jwt_required()
def create_task():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_task = Task(name=data['name'], is_public=data.get('is_public', True))
    db.session.add(new_task)
    db.session.commit()
    return jsonify(message="Task created!", task=new_task.serialize()), 201
    
#USING is_public value=False makes it only visible in admin route 

@app.route('/admintasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    task = Task.query.get_or_404(task_id)
    task.name = data.get('name', task.name)
    task.is_public = data.get('is_public', task.is_public)
    db.session.commit()
    return jsonify(message="Task updated!", task=task.serialize()), 200

@app.route('/admintasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user_id = get_jwt_identity()
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify(message="Task deleted!"), 200

@app.route('/admintasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    current_user_id = get_jwt_identity()
    task = Task.query.get_or_404(task_id)
    return jsonify(task=task.serialize()), 200

@app.route('/admintasks', methods=['GET'])
@jwt_required()
def get_all_tasks():
    current_user_id = get_jwt_identity()
    tasks = Task.query.all()
    return jsonify(tasks=[task.serialize() for task in tasks]), 200

# Initialize the Database and Run the Application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't already exist
    app.run(debug=True)


