import sys
sys.path.insert(0, '.')
from app.database import init_db, SessionLocal
from app.models.models import Room, RoomStatus

init_db()
db = SessionLocal()

if db.query(Room).count() == 0:
    rooms = [
        Room(number="101", type="Single", price_per_night=80, status=RoomStatus.available, amenities="TV, WiFi"),
        Room(number="102", type="Single", price_per_night=80, status=RoomStatus.available, amenities="TV, WiFi"),
        Room(number="201", type="Double", price_per_night=120, status=RoomStatus.available, amenities="TV, WiFi, Mini-bar"),
        Room(number="202", type="Double", price_per_night=120, status=RoomStatus.available, amenities="TV, WiFi, Mini-bar"),
        Room(number="301", type="Suite", price_per_night=250, status=RoomStatus.available, amenities="TV, WiFi, Mini-bar, Jacuzzi"),
    ]
    db.add_all(rooms)
    db.commit()
    print("Seeded 5 rooms.")
else:
    print("Rooms already exist.")
db.close()
