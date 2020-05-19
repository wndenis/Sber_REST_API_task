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

app = Flask(__name__)
api = Api(app, version="0.1", title="Sber test task API")

user_api = api.model("User", {
    "id": fields.Integer(readOnly=True, description="Unique id of user"),
    "name": fields.String(required=True, description="User's name"),
    "age": fields.Integer(required=True, description="User's age")
})

db = flask_sqlalchemy.SQLAlchemy()
app.logger.setLevel(DEBUG)


class UsersModel(db.Model):
    """sqlalchemy model represents "Users" table"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column("name", db.String(80))
    age = db.Column("age", db.Integer)

    def __init__(self, name, age):
        self.name = name
        self.age = age

    @property
    def serialize(self):
        return {"id": self.id,
                "name": self.name,
                "age": self.age}

    def __repr__(self):
        return f"<User {self.name} {self.age}>"


class UsersDAO(object):
    """data access object to interact with database"""
    @property
    def all(self):
        result = UsersModel.query.all()
        return [elem.serialize for elem in result]

    def get(self, id):
        user = UsersModel.query.filter_by(id=id).first()
        if user:
            return user.serialize
        api.abort(404, f"User {id} not found")

    def create(self, data):
        try:
            user = UsersModel(data["name"], data["age"])
        except TypeError:
            api.abort(400, f"Invalid payload")
        except KeyError:
            api.abort(400, f"Not all fields present")
        else:
            db.session.add(user)
            db.session.commit()
            return user.serialize

    def update(self, id, data):
        user = UsersModel.query.filter_by(id=id).first()
        # if parameter is present, we change user's parameter
        # else leave the old one
        try:
            new_name = data.get("name")
            new_age = data.get("age")
            user.name = new_name or user.name
            user.age = new_age or user.age
        except TypeError:
            api.abort(400, f"Invalid payload")
        else:
            db.session.commit()
            return user.serialize


    def delete(self, id):
        user = UsersModel.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()


DAO = UsersDAO()


@api.route("/users")
class UsersResource(Resource):
    """Get a list of all users and create a new one"""
    def get(self):
        """List of all users"""
        # res = pd.read_sql_query(f'select * from users', con=conn).to_dict(orient="records")
        return DAO.all

    @api.response(201, 'User created successfully')
    @api.expect(user_api)
    def post(self):
        """Create a new user"""
        # df = pd.DataFrame(data={'name': name, 'age': age}, index=[0])
        # df.to_sql(name='users', con=app.db.conn, if_exists='append', index=False)
        return DAO.create(api.payload), 201


@api.route("/users/<int:id>")
@api.response(404, "User not found")
@api.param("id", "User identifier")
class User(Resource):
    @api.doc("get_user")
    def get(self, id):
        """Fetch user with given id"""
        # res = pd.read_sql_query(f'select * from users where id={id}', con=conn).to_dict(orient="records")
        return DAO.get(id)

    @api.doc("change_user")
    @api.marshal_with(user_api)
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
