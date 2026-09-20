"""
Central configuration shared by every module.
Everyone on the team imports this instead of hardcoding paths/credentials.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Database ----
DATABASE = os.path.join(BASE_DIR, "webcam_security.db")

# ---- Folders ----
LOGS_FOLDER = os.path.join(BASE_DIR, "logs")
INTRUDER_FOLDER = os.path.join(BASE_DIR, "intruders")
FACES_FOLDER = os.path.join(BASE_DIR, "faces")

for folder in (LOGS_FOLDER, INTRUDER_FOLDER, FACES_FOLDER):
    os.makedirs(folder, exist_ok=True)

# ---- Branding ----
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
ICON_PATH = os.path.join(BASE_DIR, "assets", "icon.ico")

# ---- Default admin account (created automatically on first run) ----
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "ComplexPassword123!"
ADMIN_EMAIL = "admin@example.com"  # <-- CHANGE ME: where intruder/OTP alerts get sent to by default

# ---- SMTP settings (fill these in with your own mail account) ----
# Gmail example: create an "App Password" at https://myaccount.google.com/apppasswords
# (a normal Gmail login password will NOT work here).
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_EMAIL = "your_sender_email@gmail.com"       # <-- CHANGE ME
SMTP_PASSWORD = "your_16_char_app_password"      # <-- CHANGE ME

# ---- Registry control ----
# NOTE: HKEY_LOCAL_MACHINE requires the app to run "as Administrator" on Windows.
# HKEY_CURRENT_USER does NOT require elevation and is what Windows itself uses
# per-user for the camera privacy toggle, so it's used by default here.
# Set to True if you specifically want to attempt the HKLM path (needs admin).
USE_HKLM = False
REGISTRY_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam"

# ---- Face recognition ----
FACE_SAMPLES_TO_CAPTURE = 20          # frames captured during registration
FACE_CONFIDENCE_THRESHOLD = 70.0      # LBPH distance: LOWER = more confident match. Above this = "no match".

# ---- Security ----
MAX_FAILED_ATTEMPTS_BEFORE_LOCK = 5
OTP_VALIDITY_SECONDS = 300            # 5 minutes
