# workaround for werkzeug bug
# must be at the top level
# https://github.com/noirbizarre/flask-restplus/issues/777
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
# =======================================================
from flask import Flask, request
from flask_restplus import Api, Resource
import logging
import db_test
import pandas as pd



app = Flask(__name__)
api = Api(app)
# todo: auth db using docker-compose
logging.basicConfig(level=logging.DEBUG)


@api.route("/users/")
class Users(Resource):
    @api.doc("List of all users", params={"id": "user ID"})
    def get(self):
        conn = app.db.conn
        res = pd.read_sql_query(f'select * from users', con=conn).to_json()
        return res

    @api.doc("Create a new user", params={"name": "user name", "age": "user age"})
    @api.response(201, 'User created successfully')
    # @api.expect()
    def post(self):
        data = request.json
        # todo: resources with classes
        # todo: how to send data - in body or in header?
        print(data)
        # name = request.form["name"]
        # age = request.form["age"]
        # df = pd.DataFrame(data={'name': name, 'age': age})
        # df.to_sql(name='users', con=app.db, if_exists='replace', index=False)



    def put(self):
        return "pat"


    def delete(self):
        return "del"

@api.route("/users/<int:id>")
class User(Resource):

    def get(self, id):
        conn = app.db.conn
        res = pd.read_sql_query(f'select * from users where id={id}', con=conn).to_json()
        app.logger.info(res)
        return res


if __name__ == '__main__':
    app.db = db_test.db()
    app.db.recreate()
    app.run(host="0.0.0.0", debug=True)
