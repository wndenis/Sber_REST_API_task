from flask import Flask
from flask_restplus import Api, Resource

app = Flask(__name__)
api = Api(app)


@app.route('/hello')
class GelloWorld(Resource):
    def get(self):
        return {"Hi": "world"}


if __name__ == '__main__':
    print("warming up")
    app.run(debug=True)
