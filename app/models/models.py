from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class RoomStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    number = Column(String(10), unique=True, nullable=False)
    type = Column(String(50))  # single, double, suite
    price_per_night = Column(Float)
    status = Column(Enum(RoomStatus), default=RoomStatus.available)
    amenities = Column(Text)  # JSON string
    bookings = relationship("Booking", back_populates="room")

class Guest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    bookings = relationship("Booking", back_populates="guest")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    guest_id = Column(Integer, ForeignKey("guests.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    checked_in = Column(Boolean, default=False)
    checked_out = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    guest = relationship("Guest", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    type = Column(String(50))  # complaint, request, inquiry
    message = Column(Text)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
