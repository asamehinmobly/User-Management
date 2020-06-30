from datetime import datetime
from flask import Flask, jsonify, request
from skeleton.domain import commands
from skeleton.service_layer.handlers import InvalidEmail
from skeleton import bootstrap, views

app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/login", methods=['POST'])
def login():
    email = request.json['email']
    pwd = request.json['pwd']

    if not (email and pwd):
        return jsonify({'message': "error message"}), 400

    login_data = views.get_user_by_email(email=email, uow=bus.uow)
    return jsonify(login_data.__dict__), 200


@app.route("/change_password", methods=['POST'])
def change_password():
    try:
        cmd = commands.ChangePassword(ID=request.json['ID'], email=request.json['email'], pwd=request.json['pwd'], time=datetime.utcnow())
        bus.handle(cmd)
    except InvalidEmail as e:
        return jsonify({'message': str(e)}), 400

    return 'OK', 202


if __name__ == "__main__":
    app.run(host='0.0.0.0')
