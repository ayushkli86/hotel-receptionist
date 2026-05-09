import requests, json

# simulate a full conversation
conversation = [
    {"role": "user", "content": "I'd like to book room 101 for 2 nights. My name is John Smith, email john@example.com, phone 555-1234. Check-in 2026-05-10, check-out 2026-05-12."}
]

res = requests.post("http://localhost:8000/api/chat", json={"messages": conversation})
reply = res.json()["reply"]
print("Receptionist:", reply)
