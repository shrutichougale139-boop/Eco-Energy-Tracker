import requests
import random
import time
from datetime import datetime

API = "http://localhost:5000/api/readings"

devices = [
    ("fridge", 90, 150),     # base W range
    ("light_living", 5, 20),
    ("ac", 800, 2000),
    ("washer", 500, 1200),
    ("tv", 30, 120)
]

def send_reading(device, watts):
    payload = {
        "device": device,
        "watts": watts,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        r = requests.post(API, json=payload, timeout=2)
        print("sent", payload, "->", r.status_code)
    except Exception as e:
        print("err", e)

def simulate():
    while True:
        # each loop randomly pick some devices to be active, produce readings
        for dev, minw, maxw in devices:
            if random.random() < 0.7:  # 70% chance device sends reading
                # simulate varying load
                watts = round(random.uniform(minw, maxw), 2)
                send_reading(dev, watts)
        time.sleep(5)  # send batch every 5s

if __name__ == "__main__":
    simulate()
