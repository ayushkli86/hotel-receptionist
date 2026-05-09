from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Room, Guest, Booking, ServiceRequest, RoomStatus
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# --- Schemas ---
class GuestCreate(BaseModel):
    name: str
    email: str
    phone: str

class BookingCreate(BaseModel):
    guest_id: int
    room_id: int
    check_in: datetime
    check_out: datetime

class ServiceRequestCreate(BaseModel):
    booking_id: int
    type: str
    message: str

# --- Rooms ---
@router.get("/rooms")
def get_rooms(status: str = None, db: Session = Depends(get_db)):
    q = db.query(Room)
    if status:
        q = q.filter(Room.status == status)
    return q.all()

# --- Guests ---
@router.post("/guests")
def create_guest(data: GuestCreate, db: Session = Depends(get_db)):
    guest = Guest(**data.model_dump())
    db.add(guest); db.commit(); db.refresh(guest)
    return guest

# --- Bookings ---
@router.post("/bookings")
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == data.room_id).first()
    if not room or room.status != RoomStatus.available:
        raise HTTPException(400, "Room not available")
    booking = Booking(**data.model_dump())
    room.status = RoomStatus.occupied
    db.add(booking); db.commit(); db.refresh(booking)
    return booking

@router.post("/bookings/{booking_id}/checkin")
def checkin(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    booking.checked_in = True
    db.commit()
    return {"message": f"Welcome! Room {booking.room.number} is ready."}

@router.post("/bookings/{booking_id}/checkout")
def checkout(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    booking.checked_out = True
    booking.room.status = RoomStatus.available
    db.commit()
    nights = (booking.check_out - booking.check_in).days
    total = nights * booking.room.price_per_night
    return {"message": "Thank you for staying!", "total": total, "nights": nights}

# --- Service Requests ---
@router.post("/service")
def service_request(data: ServiceRequestCreate, db: Session = Depends(get_db)):
    req = ServiceRequest(**data.model_dump())
    db.add(req); db.commit()
    return {"message": "Request logged. Staff will assist you shortly."}
