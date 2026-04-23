import requests
import time
import json
import uuid
import os
from datetime import datetime
from pathlib import Path

# Configuration - Assuming backend is at localhost:8000
BASE_URL = "http://localhost:8000"
IMAGE_PATH = r"C:\Users\manoj\.gemini\antigravity\brain\792fcdac-60e7-449b-995f-88c359178896\test_skin_condition_1776329074254.png"

class PerfLogger:
    def __init__(self):
        self.results = []

    def log_request(self, scenario, method, endpoint, status_code, duration):
        self.results.append({
            "scenario": scenario,
            "method": method,
            "endpoint": endpoint,
            "status": status_code,
            "duration_ms": round(duration * 1000, 2)
        })
        print(f"[PERF] {scenario} | {method} {endpoint} | Status: {status_code} | Time: {round(duration * 1000, 2)}ms")

perf = PerfLogger()

def timed_request(scenario, method, url, **kwargs):
    start_time = time.time()
    try:
        resp = requests.request(method, url, **kwargs)
        end_time = time.time()
        perf.log_request(scenario, method, url.replace(BASE_URL, ""), resp.status_code, end_time - start_time)
        return resp
    except Exception as e:
        print(f"[ERROR] {scenario} failed: {e}")
        return None

def run_tests():
    print("=" * 60)
    print("Starting Backend Scenario Performance Tests")
    print("=" * 60)

    # --- 1. Authentication & Authorization ---
    email = f"perf_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPassword123!"
    
    # 1.1 Register
    timed_request("Auth Register", "POST", f"{BASE_URL}/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Performance Tester"
    })

    # 1.2 Login
    login_resp = timed_request("Auth Login", "POST", f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": password
    })
    
    if not login_resp or login_resp.status_code != 200:
        print("Login failed, skipping dependent tests.")
        return

    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # --- 2. AI Analysis ---
    if os.path.exists(IMAGE_PATH):
        with open(IMAGE_PATH, 'rb') as f:
            files = [('image_files', ('test.png', f, 'image/png'))]
            data = {
                "messages": json.dumps([{"role": "user", "content": "Category: Skin, Condition: Acne. Analyze this image."}])
            }
            timed_request("AI Analysis", "POST", f"{BASE_URL}/api/ai/chat", data=data, files=files, headers=headers)
    else:
        print(f"Image not found at {IMAGE_PATH}, skipping AI Analysis test.")

    # --- 3. Appointments ---
    prov_resp = timed_request("List Providers", "GET", f"{BASE_URL}/api/provider/providers", headers=headers)
    if prov_resp and prov_resp.status_code == 200:
        providers = prov_resp.json()
        if providers:
            # Try to find a provider with slots
            found_slot = False
            for provider in providers:
                p_id = provider['id']
                slots_resp = timed_request(f"List Slots for {p_id}", "GET", f"{BASE_URL}/api/provider/slot/{p_id}", headers=headers)
                if slots_resp and slots_resp.status_code == 200:
                    slots = slots_resp.json()
                    if slots:
                        slot = slots[0]
                        st_dt = datetime.fromisoformat(slot['start_time'].replace('Z', ''))
                        
                        book_payload = {
                            "provider_id": p_id,
                            "preferred_date": st_dt.date().isoformat(),
                            "preferred_time": st_dt.time().isoformat(),
                            "case_id": None
                        }
                        timed_request("Book Appointment (Order)", "POST", f"{BASE_URL}/api/appointment/appointments/book", json=book_payload, headers=headers)
                        found_slot = True
                        break
            if not found_slot:
                print("No available slots for any provider, skipping booking test.")
    
    # --- 4. Video Calls ---
    appts_resp = timed_request("List My Appts", "GET", f"{BASE_URL}/api/appointment/appointments", headers=headers)
    if appts_resp and appts_resp.status_code == 200:
        appts = appts_resp.json()
        if appts:
            appt_id = appts[0]['id']
            timed_request("Video Call Token", "GET", f"{BASE_URL}/api/videocall/token?appointment_id={appt_id}", headers=headers)

    # --- Summary ---
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("-" * 60)
    print(f"{'Scenario':<25} | {'Method':<6} | {'Status':<6} | {'Time (ms)':<10}")
    print("-" * 60)
    for r in perf.results:
        print(f"{r['scenario']:<25} | {r['method']:<6} | {r['status']:<6} | {r['duration_ms']:<10}")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
