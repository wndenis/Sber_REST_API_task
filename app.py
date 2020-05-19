# workaround for werkzeug bug
# must be at the top level
# https://github.com/noirbizarre/flask-restplus/issues/777
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
# =======================================================
from flask import Flask
import flask_sqlalchemy
from flask_restplus import Api, Resource, fields
from faker import Faker
import random
from logging import DEBUG
from psycopg2 import OperationalError
import time

import config

# create app
app = Flask(__name__)

# create api
api = Api(app, version="0.1", title="Sber test task API")

# create api model
user_api = api.model("User", {
    "id": fields.Integer(readonly=True, description="Unique id of user", min=1),
    "name": fields.String(required=True, description="User's name", max_length=80, example="Peter Parker"),
    "age": fields.Integer(required=True, description="User's age", example=22)
})

# create db access
db = flask_sqlalchemy.SQLAlchemy()

# configure logger
app.logger.setLevel(DEBUG)


class UsersModel(db.Model):
    """SQLalchemy model represents "Users" table"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column("name", db.String(80))
    age = db.Column("age", db.Integer)

    def __init__(self, name, age):
        self.name = name
        self.age = age

    @property
    def serialize(self):
        """
        :return: serialized version of object
        """
        return {"id": self.id,
                "name": self.name,
                "age": self.age}

    def __repr__(self):
        return f"<User {self.name} {self.age}>"


class UsersDAO(object):
    """Data access object to interact with database"""
    @property
    def all(self):
        """
        Retrieve all users
        :return: List with all users
        """
        result = UsersModel.query.all()
        return [elem.serialize for elem in result]

    def get(self, id: int):
        """
        Retrieve user by id
        :param id: User id
        :return: User or 404 if not found
        """
        user = UsersModel.query.filter_by(id=id).first()
        if user:
            return user.serialize
        api.abort(404, f"User {id} not found")

    def create(self, data):
        """
        Create a new user
        :param data: dict containing "age" (int) and "name" (str)
        :return: User or 400 if body invalid
        """
        try:
            user = UsersModel(data["name"], data["age"])
        except (KeyError, TypeError):
            api.abort(400, "Invalid payload")
        else:
            db.session.add(user)
            db.session.commit()
            return user.serialize

    def update(self, id: int, data):
        """
        Update user by id using values from data
        :param id: User id
        :param data: dict containing both "age" (int) and "name" (str) keys
        :return: User
        """
        user = UsersModel.query.filter_by(id=id).first()
        # if one of parameters is not present, return 400
        try:
            user.name = data["name"]
            user.age = data["age"]
        except (KeyError, TypeError):
            api.abort(400, "Invalid payload")
        else:
            db.session.commit()
            return user.serialize

    def delete(self, id: int):
        """
        Delete user by id
        :param id: User id
        :return: None
        """
        user = UsersModel.query.filter_by(id=id).first()
        if not user:
            api.abort(404, "User not found")
        db.session.delete(user)
        db.session.commit()


DAO = UsersDAO()


# Routes
@api.route("/users/")
class UsersResource(Resource):
    """Get a list of all users or create a new one"""
    @api.doc("list_users")
    def get(self):
        """List of all users"""
        # res = pd.read_sql_query(f'select * from users', con=conn).to_dict(orient="records")
        return DAO.all

    @api.doc("create_user")
    @api.response(201, 'User created successfully')
    @api.response(400, "Invalid payload")
    @api.expect(user_api)
    def post(self):
        """Create a new user"""
        # df = pd.DataFrame(data={'name': name, 'age': age}, index=[0])
        # df.to_sql(name='users', con=app.db.conn, if_exists='append', index=False)
        return DAO.create(api.payload), 201


@api.route("/users/<int:id>/")
@api.response(404, "User not found")
@api.param("id", "User identifier")
class UserResource(Resource):
    """Access a single user and replace or delete it"""
    @api.doc("get_user")
    @api.marshal_with(user_api)
    def get(self, id):
        """Fetch user with given id"""
        # res = pd.read_sql_query(f'select * from users where id={id}', con=conn).to_dict(orient="records")
        return DAO.get(id)

    @api.expect(user_api)
    @api.marshal_with(user_api)
    @api.response(400, "Invalid payload")
    def put(self, id):
        """Update user with given id"""
        return DAO.update(id, api.payload)

    @api.doc("delete_user")
    @api.response(204, "User deleted")
    def delete(self, id):
        """Delete user with given id"""
        DAO.delete(id)
        return "", 204


def recreate_db():
    """
    function for testing purposes: fills database with some entries if it's empty
    """
    # if database is not empty, skip this step
    if UsersModel.query.count():
        app.logger.info("Database is not empty, skipping recreating")
        return
    # else create 100 random entries
    fake = Faker()
    for x in range(100):
        user = UsersModel(name=fake.name(), age=random.randint(1, 99))
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"Created {user}")


if __name__ == '__main__':
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.app_context().push()
    db.init_app(app)

    # I need this to avoid Operational Error which may be caused by long time of database loading
    # try to connect 30 times with delay of 1 second
    # else halt and print that we couldn't manage to connect to database
    db_connected = False
    for x in range(30):
        try:
            db.create_all()
            db_connected = True
            break
        except OperationalError as e:
            app.logger.info(e)
            time.sleep(1)
    if not db_connected:
        app.logger.error("Couldn't connet to database")
        exit(1)
    app.logger.info("Database connected successfully")

    if config.fake_db:
        recreate_db()

    app.run(host="0.0.0.0", debug=True)
