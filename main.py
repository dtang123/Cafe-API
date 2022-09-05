from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

#API is not published but is saved in postman


app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random():
    all = db.session.query(Cafe).all()
    cafe = random.choice(all)
    return jsonify(cafe={"name": cafe.name, "map": cafe.map_url, "img": cafe.img_url,
                         "location": cafe.location, "wifi": cafe.has_wifi, "sockets": cafe.has_sockets,
                         "toilets": cafe.has_toilet, "calls": cafe.can_take_calls, "seats": cafe.seats,
                         "price": cafe.coffee_price})


@app.route("/all")
def all():
    all = db.session.query(Cafe).all()
    dict_all = [{"name": cafe.name, "map": cafe.map_url, "img": cafe.img_url,
                 "location": cafe.location, "wifi": cafe.has_wifi, "sockets": cafe.has_sockets,
                 "toilets": cafe.has_toilet, "calls": cafe.can_take_calls, "seats": cafe.seats,
                 "price": cafe.coffee_price} for cafe in all]
    return jsonify(dict_all)

@app.route("/search")
def search():
    query_location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    if not cafes:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    cafesAtLocation = []
    for cafe in cafes:
        if cafe.location == query_location:
            cafesAtLocation.append({"name": cafe.name, "map": cafe.map_url, "img": cafe.img_url,
                 "location": cafe.location, "wifi": cafe.has_wifi, "sockets": cafe.has_sockets,
                 "toilets": cafe.has_toilet, "calls": cafe.can_take_calls, "seats": cafe.seats,
                 "price": cafe.coffee_price})

    return jsonify(cafes=cafesAtLocation)



## HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def add():
    cafe = Cafe(name=request.form.get("name"), map_url=request.form.get("map_url"), img_url=request.form.get("img_url"),
                         location=request.form.get("location"), has_wifi=bool(request.form.get("has_wifi")), has_sockets=bool(request.form.get("has_sockets")),
                         has_toilet=bool(request.form.get("has_toilet")), can_take_calls=bool(request.form.get("can_take_calls")),
                seats=request.form.get("seats"), coffee_price=request.form.get("coffee_price"))
    db.session.add(cafe)
    db.session.commit()
    return jsonify(response={"Success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update(id):
    newPrice = request.args.get("new_price")
    db_element = db.session.query(Cafe).get(id)
    if db_element:
        db_element.coffee_price = newPrice
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price"}), 200
    return jsonify(error={"Not Found": "A cafe with that id was not found."}), 404

## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:id>", methods=["DELETE"])
def closed(id):
    secret_key = "abcdefg"
    key = request.args.get("api_key")
    db_element = db.session.query(Cafe).get(id)
    if db_element and key == secret_key:
        db.session.delete(db_element)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted item"}), 200
    if not db_element:
        return jsonify(error={"Not Found": "A cafe with that id was not found."}), 404
    return jsonify(error={"Wrong key": "API key does not match"}), 403



if __name__ == '__main__':
    app.run(debug=True)
