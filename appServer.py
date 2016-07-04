import os
from flask import Flask, redirect, url_for, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
if app.config['SQLALCHEMY_DATABASE_URI'] is None:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Anthony/Downloads/person.db'
    app.debug = True
db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    info = db.relationship('Info')

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<id: %d>' % (self.id)

    def todict(self):
        return dict(id = self.id, info = [row.todict() for row in self.info])

class Info(db.Model):
    __tablename__ = 'info'
    index = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('persons.id'))
    name = db.Column(db.String(50), unique=False)
    phone = db.Column(db.String(11), unique=False)
    companyName = db.Column(db.String(100), unique=False)
    email = db.Column(db.String(50), unique=False)

    def __init__(self, user_id, name, phone, companyName, email):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.companyName = companyName
        self.email = email

    def __repr__(self):
        return '<index: %d user_id: %d name: %s phone: %s companyName: %s email: %s>' \
               % (self.index, self.user_id, self.name, self.phone, self.companyName, self.email)

    def todict(self):
        return dict(index=self.index, user_id = self.user_id, name=self.name, phone=self.phone, companyName=self.companyName,
                    email=self.email)

def makeDB():
    db.create_all()

def dropDB():
    db.drop_all()

@app.route('/person/<user_id>/info/<info_phone>', methods = ['POST', 'DELETE'])
def addInfo(user_id, info_phone):
    error = None
    if user_id is not None and info_phone is not None:
        target = Person.query.filter_by(id=user_id).first()
        if target is not None:
            if request.method == 'POST':
                json_data = request.get_json(force=True)
                newInfo = Info(user_id=user_id, name=json_data["name"], phone=json_data["phone"],
            companyName=json_data["companyName"], email=json_data["email"])
                target.info.append(newInfo)
                db.session.commit()
                return redirect(url_for('sendData', id=user_id))
            else:
                targetInfo = Info.query.filter_by(phone=info_phone).first()
                if targetInfo is not None:
                    target.info.remove(targetInfo)
                    db.session.delete(targetInfo)
                    db.session.commit()
                    return redirect(url_for('sendData', id=user_id))
                else:
                    error="I can't find this"
        else:
            error = "This user_id's info table is NULL"
    else:
        error="user_id or info_id is maybe Null"
    return render_template('error.html', error=error)

@app.route('/person/<id>', methods=['GET', 'POST', 'DELETE'])
def sendData(id):
    error = None
    if id is not None:
        datas = Person.query.filter_by(id=id).first()
        if datas is not None:
            jsonData = datas.todict()
            return jsonify(jsonData)
        else:
            data = Person(id=id)
            db.session.add(data)
            db.session.commit()
            jsonData = data.todict()
            return jsonify(jsonData)
    else:
        error="User Id is empty"
    return render_template('error.html', error=error)

if __name__ == '__main__':
    app.run()