# from flask import Flask, render_template, request, redirect, url_for, flash, session
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash


# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), nullable=False, unique=True)
#     password = db.Column(db.String(150), nullable=False)

# class Task(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(150), nullable=False)
#     description = db.Column(db.String(500))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
#         new_user = User(username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Registration successful!', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             session['user_id'] = user.id
#             flash('Login successful!', 'success')
#             return redirect(url_for('index'))
#         flash('Invalid credentials', 'danger')
#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     flash('Logged out successfully!', 'success')
#     return redirect(url_for('login'))

# @app.route('/')
# def index():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     user_id = session['user_id']
#     tasks = Task.query.filter_by(user_id=user_id).all()
#     return render_template('index.html', tasks=tasks)

# @app.route('/task/add', methods=['POST'])
# def add_task():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     title = request.form['title']
#     description = request.form['description']
#     new_task = Task(title=title, description=description, user_id=session['user_id'])
#     db.session.add(new_task)
#     db.session.commit()
#     flash('Task added!', 'success')
#     return redirect(url_for('index'))

# @app.route('/task/update/<int:id>', methods=['POST'])
# def update_task(id):
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     task = Task.query.get_or_404(id)
#     task.title = request.form['title']
#     task.description = request.form['description']
#     db.session.commit()
#     flash('Task updated!', 'success')
#     return redirect(url_for('index'))

# @app.route('/task/delete/<int:id>')
# def delete_task(id):
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     task = Task.query.get_or_404(id)
#     db.session.delete(task)
#     db.session.commit()
#     flash('Task deleted!', 'success')
#     return redirect(url_for('index'))




# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    tasks = db.relationship('Task', foreign_keys='Task.user_id', backref='creator', lazy=True)
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_user_id', backref='assigned_user', lazy=True)
    updates = db.relationship('Task', foreign_keys='Task.last_updated_by', backref='updater', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Task creator
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Assigned user
    last_updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who last updated
    last_updated_at = db.Column(db.DateTime, nullable=True)  # When last updated

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    tasks = Task.query.filter((Task.user_id == user_id) | (Task.assigned_user_id == user_id)).all()
    users = User.query.all()
    return render_template('index.html', tasks=tasks, users=users)

@app.route('/task/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    title = request.form['title']
    description = request.form['description']
    assigned_user_id = request.form.get('assigned_user_id')
    if assigned_user_id:
        assigned_user_id = int(assigned_user_id)
    new_task = Task(title=title, description=description, user_id=session['user_id'], assigned_user_id=assigned_user_id)
    db.session.add(new_task)
    db.session.commit()
    flash('Task added!', 'success')
    return redirect(url_for('index'))

@app.route('/task/update/<int:id>', methods=['POST'])
def update_task(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    task = Task.query.get_or_404(id)
    if session['user_id'] not in [task.user_id, task.assigned_user_id]:
        flash('You do not have permission to update this task.', 'danger')
        return redirect(url_for('index'))
    task.title = request.form['title']
    task.description = request.form['description']
    task.last_updated_by = session['user_id']
    task.last_updated_at = datetime.utcnow()
    db.session.commit()
    flash('Task updated!', 'success')
    return redirect(url_for('index'))

@app.route('/task/delete/<int:id>')
def delete_task(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    task = Task.query.get_or_404(id)
    if session['user_id'] != task.user_id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
