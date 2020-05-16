# workaround for werkzeug bug
# must be at the top level
# https://github.com/noirbizarre/flask-restplus/issues/777
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
# =======================================================
from flask import Flask
from flask_restplus import Api, Resource
import db_test
app = Flask(__name__)
api = Api(app)

# todo: I realized that I shouldnt try to connect to db at startup

@api.route('/hello')
class GelloWorld(Resource):
    def get(self):
        return {"Hi": "world!"}


if __name__ == '__main__':
    try:
        db_test.test_connection()
    except Exception as e:
        print(e)
    else:
        print("DB OK")
    app.run(host="0.0.0.0", debug=True)
