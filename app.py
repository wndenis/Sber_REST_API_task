# workaround for werkzeug bug
# must be at the top level
# https://github.com/noirbizarre/flask-restplus/issues/777
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
# =======================================================
from flask import Flask, request
from flask_restplus import Api, Resource
import logging
import pandas as pd

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
api = Api(app)
# todo: auth db using docker-compose
logging.basicConfig(level=logging.DEBUG)


@api.route("/users/")
class Users(Resource):
    # todo: docstring
    @api.doc("List of all users")
    def get(self):
        conn = app.db.conn
        res = pd.read_sql_query(f'select * from users', con=conn).to_dict(orient="records")
        return res

    @api.doc("Create a new user", params={"name": "user name", "age": "user age"})
    @api.response(201, 'User created successfully')
    # @api.expect()
    def post(self):
        # todo: how to send data - in json or in form?
        data = request.json or request.form
        if not data:
            print("empty body")
        print(data)
        name = data["name"]
        age = data["age"]
        df = pd.DataFrame(data={'name': name, 'age': age}, index=[0])
        print(df)
        print()
        # append because of POST
        df.to_sql(name='users', con=app.db.conn, if_exists='append', index=False)

    @api.doc("Change user", params={"id": "user id", "name": "user name", "age": "user age"})
    def put(self):
        return "pat"

    def delete(self):
        return "del"

@api.route("/users/<int:id>")
class User(Resource):
    @api.doc("List of all users", params={"id": "user ID"})
    def get(self, id):
        conn = app.db.conn
        res = pd.read_sql_query(f'select * from users where id={id}', con=conn).to_dict(orient="records")
        app.logger.info(res)
        return res


if __name__ == '__main__':



    app.db = db_test.db()
    app.db.recreate()
    app.run(host="0.0.0.0", debug=True)
