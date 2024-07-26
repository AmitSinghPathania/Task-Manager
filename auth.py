from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_httpauth import HTTPBasicAuth
import app
api = Api(app)
auth = HTTPBasicAuth()

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='Username is required')
user_parser.add_argument('password', type=str, required=True, help='Password is required')

task_parser = reqparse.RequestParser()
task_parser.add_argument('title', type=str, required=True, help='Title is required')
task_parser.add_argument('description', type=str)
task_parser.add_argument('completed', type=bool)

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
}

task_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'completed': fields.Boolean,
    'user_id': fields.Integer,
}

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

class UserRegister(Resource):
    def post(self):
        args = user_parser.parse_args()
        hashed_password = generate_password_hash(args['password'], method='sha256')
        new_user = User(username=args['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return marshal_with(user_fields)(new_user), 201

class TaskList(Resource):
    @auth.login_required
    @marshal_with(task_fields)
    def get(self):
        tasks = Task.query.filter_by(user_id=auth.current_user().id).all()
        return tasks

    @auth.login_required
    @marshal_with(task_fields)
    def post(self):
        args = task_parser.parse_args()
        new_task = Task(title=args['title'], description=args['description'], completed=args['completed'], user_id=auth.current_user().id)
        db.session.add(new_task)
        db.session.commit()
        return new_task, 201

class TaskDetail(Resource):
    @auth.login_required
    @marshal_with(task_fields)
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        if task.user_id != auth.current_user().id:
            return {'message': 'Forbidden'}, 403
        return task

    @auth.login_required
    @marshal_with(task_fields)
    def put(self, task_id):
        args = task_parser.parse_args()
        task = Task.query.get_or_404(task_id)
        if task.user_id != auth.current_user().id:
            return {'message': 'Forbidden'}, 403
        task.title = args['title']
        task.description = args['description']
        task.completed = args['completed']
        db.session.commit()
        return task

    @auth.login_required
    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        if task.user_id != auth.current_user().id:
            return {'message': 'Forbidden'}, 403
        db.session.delete(task)
        db.session.commit()
        return '', 204

api.add_resource(UserRegister, '/api/register')
api.add_resource(TaskList, '/api/tasks')
api.add_resource(TaskDetail, '/api/tasks/<int:task_id>')
