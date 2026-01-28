# Enhanced Instagram Login Script with Detailed Device Emulation (2026 Edition)
# Fixed: UUIDs and device_id generation use correct instagrapi instance methods
# WARNING: Datacenter IPs (Wisspbyte, Pterodactyl-style hosts) are heavily flagged by Instagram.
# Best chance: Run once on your home PC/phone → copy session.json to server.
import os
import random
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, ChallengeRequired, TwoFactorRequired,
    ClientThrottledError, BadPassword, PleaseWaitFewMinutes
)

load_dotenv()

# ────────────────────────────────────────────────
#               CONFIGURATION
# ────────────────────────────────────────────────

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")
PROXY    = os.getenv("PROXY", "")           # residential proxy strongly recommended
SESSION_FILE = "session.json"

# ────────────────────────────────────────────────
#               DEVICE EMULATION (randomized)
# ────────────────────────────────────────────────

DEVICE_SETTINGS = {
    "app_version": random.choice(["346.0.0.42.102", "350.1.0.39.104", "352.0.0.0.45"]),
    "android_version": random.randint(13, 15),
    "android_release": f"{random.randint(13, 15)}.0.0",
    
    "dpi": f"{random.choice([480, 560, 640])}dpi",
    "resolution": random.choice(["1080x2340", "1440x3200", "1080x2400"]),
    
    "manufacturer": random.choice(["Google", "Samsung", "OnePlus"]),
    "device": random.choice(["Pixel 8 Pro", "Galaxy S24 Ultra", "OnePlus 12"]),
    "model": random.choice(["Pixel 8 Pro", "SM-S928B", "PJX110"]),
    "cpu": "arm64-v8a",
    
    "processor_details": f"ARM64 FP ASIMD AES | {random.randint(2500, 3200)} | {random.randint(4, 8)}",
    "memory": random.randint(6000, 12000),
    "gpu_renderer": random.choice(["Adreno (TM) 750", "Mali-G710", "Adreno (TM) 740"]),
    "gpu_version": "OpenGL ES 3.2 v1.10",
    
    "internal_storage_total": random.randint(128000, 512000),
    "internal_storage_available": random.randint(50000, 400000),
    "external_storage_total": random.randint(0, 1000000),
    "external_storage_available": random.randint(0, 900000),
    
    "network_type": random.choice(["WIFI", "MOBILE"]),
    "telecom_operator": random.choice(["Jio", "Airtel", "Vodafone", "Verizon"]),
    "language": "en_IN",
}

# Calculate dependent fields AFTER dict creation
res_parts = DEVICE_SETTINGS["resolution"].split("x")
DEVICE_SETTINGS["screen_width"]  = int(res_parts[0])
DEVICE_SETTINGS["screen_height"] = int(res_parts[1])

# Custom User-Agent
USER_AGENT = (
    f"Instagram {DEVICE_SETTINGS['app_version']} Android "
    f"({DEVICE_SETTINGS['android_version']}/{DEVICE_SETTINGS['android_release']}; "
    f"{DEVICE_SETTINGS['dpi']}; {DEVICE_SETTINGS['resolution']}; "
    f"{DEVICE_SETTINGS['manufacturer']}; {DEVICE_SETTINGS['device']}; "
    f"{DEVICE_SETTINGS['model']}; {DEVICE_SETTINGS['cpu']}; "
    f"en_IN; {random.randint(500000000, 599999999)})"
)

# ────────────────────────────────────────────────
#               CLIENT SETUP
# ────────────────────────────────────────────────

cl = Client()

# Apply settings
cl.set_device(DEVICE_SETTINGS)
cl.set_user_agent(USER_AGENT)
cl.set_locale(DEVICE_SETTINGS["language"])
cl.set_timezone_offset(random.randint(-3600, 3600))
cl.set_country("IN")
cl.set_country_code(91)

cl.delay_range = [1.5, 5.5]

if PROXY:
    print(f"Using proxy: {PROXY}")
    cl.set_proxy(PROXY)

# Generate UUIDs and device ID using INSTANCE methods (cl.)
cl.set_uuids({
    "phone_id": cl.generate_uuid(),
    "uuid": cl.generate_uuid(),
    "android_id": cl.generate_android_device_id(),   # ← this is the correct method
    "request_id": cl.generate_uuid(),
    # "device_id": cl.generate_device_id()          # ← does NOT exist → removed
    # If you need a device_id, use android_id above or generate manually
})

# ────────────────────────────────────────────────
#               LOGIN FUNCTION
# ────────────────────────────────────────────────

def login():
    if os.path.exists(SESSION_FILE):
        print("Trying to load existing session...")
        try:
            cl.load_settings(SESSION_FILE)
            cl.get_timeline_feed()  # quick test
            print("Session loaded successfully!")
            return True
        except Exception as e:
            print(f"Session invalid: {e}")
            os.remove(SESSION_FILE)

    print("Performing fresh login...")
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("Login successful! Session saved.")
        return True
    except TwoFactorRequired:
        code = input("Enter 2FA code: ").strip()
        cl.login(USERNAME, PASSWORD, verification_code=code)
        cl.dump_settings(SESSION_FILE)
        return True
    except ChallengeRequired:
        print("\n!!! Instagram Challenge Required !!!")
        print("→ Open Instagram app or website → verify your login manually")
        print("→ After verification, delete session.json and retry")
        return False
    except (BadPassword, ClientThrottledError, PleaseWaitFewMinutes) as e:
        print(f"Login blocked: {e}")
        print("Likely IP flagged (datacenter host). Try from home network or add residential proxy.")
        return False
    except Exception as e:
        print(f"Login failed: {type(e).__name__} → {e}")
        return False

# ────────────────────────────────────────────────
#               MAIN EXECUTION
# ────────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting enhanced Instagram login script...")
    success = login()
    
    if success:
        print("\nLogin successful!")
        print("You can now add your story liking / automation code here.")
        # Example test line:
        # user = cl.user_info(cl.user_id)
        # print(f"Logged in as: {user.username}")
    else:
        print("\nLogin failed. Possible reasons:")
        print("- Wrong credentials")
        print("- Challenge / 2FA required (solve in official app)")
        print("- IP blocked (common on Wisspbyte / cloud hosts)")
        print("Recommendation: Run once on your home PC/phone → copy session.json here.")