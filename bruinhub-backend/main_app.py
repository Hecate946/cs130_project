import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from config import DATABASE_URL

# Initialize Flask App
app = Flask(__name__)

# Database Configuration (Change this for your setup)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', DATABASE_URL)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB and Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# ------------------------------
# 🚀 Database Models
# ------------------------------


class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, db.ForeignKey(
        'library.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False,
                       default="available")  # available or booked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------------------
# 🚀 Schema for JSON Output
# ------------------------------


class LibrarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Library


class RoomSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Room


class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Booking


library_schema = LibrarySchema()
libraries_schema = LibrarySchema(many=True)

room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# ------------------------------
# 🚀 API Routes
# ------------------------------

# 🔹 Get All Libraries


@app.route('/libraries', methods=['GET'])
def get_libraries():
    libraries = Library.query.all()
    return jsonify(libraries_schema.dump(libraries))

# 🔹 Get Rooms in a Specific Library


@app.route('/libraries/<slug>/rooms', methods=['GET'])
def get_rooms(slug):
    library = Library.query.filter_by(slug=slug).first()
    if not library:
        return jsonify({"message": "Library not found"}), 404
    rooms = Room.query.filter_by(library_id=library.id).all()
    return jsonify(rooms_schema.dump(rooms))

# 🔹 Get Availability for a Specific Room


@app.route('/rooms/<slug>/availability', methods=['GET'])
def get_room_availability(slug):
    room = Room.query.filter_by(slug=slug).first()
    if not room:
        return jsonify({"message": "Room not found"}), 404

    bookings = Booking.query.filter_by(room_id=room.id).all()
    return jsonify(bookings_schema.dump(bookings))

# 🔹 Create a New Booking


@app.route('/bookings', methods=['POST'])
def create_booking():
    data = request.json
    room = Room.query.filter_by(id=data['room_id']).first()
    if not room:
        return jsonify({"message": "Room not found"}), 404

    new_booking = Booking(
        room_id=data['room_id'],
        start_time=datetime.strptime(data['start_time'], "%Y-%m-%d %H:%M:%S"),
        end_time=datetime.strptime(data['end_time'], "%Y-%m-%d %H:%M:%S"),
        status=data.get('status', 'available')
    )

    db.session.add(new_booking)
    db.session.commit()
    return booking_schema.jsonify(new_booking), 201


# ------------------------------
# 🚀 Run Flask App
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
