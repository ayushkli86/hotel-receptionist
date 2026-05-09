from groq import Groq
from sqlalchemy.orm import Session
from app.models.models import Room, Guest, Booking, ServiceRequest, RoomStatus
from datetime import datetime
import os, json

SYSTEM_PROMPT = """You are an AI receptionist for Grand Hotel. Be polite, professional, and concise.
Use the available tools to perform real actions when guests request them.
Hotel WiFi: GrandHotel_5G | Password: welcome2024"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_available_rooms",
            "description": "Get list of available rooms",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_and_book",
            "description": "Register a guest and book a room",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "room_number": {"type": "string"},
                    "check_in": {"type": "string", "description": "YYYY-MM-DD"},
                    "check_out": {"type": "string", "description": "YYYY-MM-DD"}
                },
                "required": ["name", "email", "phone", "room_number", "check_in", "check_out"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "checkin_guest",
            "description": "Check in a guest by their booking ID",
            "parameters": {
                "type": "object",
                "properties": {"booking_id": {"type": "integer"}},
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "checkout_guest",
            "description": "Check out a guest by their booking ID",
            "parameters": {
                "type": "object",
                "properties": {"booking_id": {"type": "integer"}},
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_service_request",
            "description": "Log a complaint or service request",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "integer"},
                    "type": {"type": "string", "enum": ["complaint", "request", "inquiry"]},
                    "message": {"type": "string"}
                },
                "required": ["booking_id", "type", "message"]
            }
        }
    }
]

def run_tool(name: str, args: dict, db: Session) -> str:
    if name == "get_available_rooms":
        rooms = db.query(Room).filter(Room.status == RoomStatus.available).all()
        return json.dumps([{"number": r.number, "type": r.type, "price": r.price_per_night, "amenities": r.amenities} for r in rooms])

    elif name == "register_and_book":
        # find or create guest
        guest = db.query(Guest).filter(Guest.email == args["email"]).first()
        if not guest:
            guest = Guest(name=args["name"], email=args["email"], phone=args["phone"])
            db.add(guest); db.flush()
        room = db.query(Room).filter(Room.number == args["room_number"], Room.status == RoomStatus.available).first()
        if not room:
            return json.dumps({"error": "Room not available"})
        booking = Booking(
            guest_id=guest.id, room_id=room.id,
            check_in=datetime.strptime(args["check_in"], "%Y-%m-%d"),
            check_out=datetime.strptime(args["check_out"], "%Y-%m-%d")
        )
        room.status = RoomStatus.occupied
        db.add(booking); db.commit(); db.refresh(booking)
        return json.dumps({"booking_id": booking.id, "room": room.number, "guest": guest.name})

    elif name == "checkin_guest":
        booking = db.query(Booking).filter(Booking.id == args["booking_id"]).first()
        if not booking:
            return json.dumps({"error": "Booking not found"})
        booking.checked_in = True
        db.commit()
        return json.dumps({"message": f"Checked in. Room {booking.room.number} is ready."})

    elif name == "checkout_guest":
        booking = db.query(Booking).filter(Booking.id == args["booking_id"]).first()
        if not booking:
            return json.dumps({"error": "Booking not found"})
        booking.checked_out = True
        booking.room.status = RoomStatus.available
        db.commit()
        nights = (booking.check_out - booking.check_in).days
        total = nights * booking.room.price_per_night
        return json.dumps({"message": "Checked out successfully", "nights": nights, "total": total})

    elif name == "log_service_request":
        req = ServiceRequest(**args)
        db.add(req); db.commit()
        return json.dumps({"message": "Request logged. Staff will assist shortly."})

    return json.dumps({"error": "Unknown tool"})

def chat(messages: list, db: Session) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        tools=TOOLS,
        tool_choice="auto",
        max_tokens=500
    )
    msg = response.choices[0].message

    # if AI wants to call a tool
    if msg.tool_calls:
        tool_messages = messages + [msg]
        for tc in msg.tool_calls:
            result = run_tool(tc.function.name, json.loads(tc.function.arguments), db)
            tool_messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        # get final response after tool execution
        final = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + tool_messages,
            max_tokens=300
        )
        return final.choices[0].message.content

    return msg.content
