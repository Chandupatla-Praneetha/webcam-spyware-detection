# 🛡️ Webcam Spyware Detection and Security Tool

> A Python-based cybersecurity desktop application that protects users from unauthorized webcam access using authentication, face recognition, intrusion detection, activity logging, and real-time email alerts.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green)
![OpenCV](https://img.shields.io/badge/OpenCV-LBPH-orange)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## 📖 Project Overview

The **Webcam Spyware Detection and Security Tool** is a desktop application developed in Python to enhance webcam privacy and security.

The system prevents unauthorized webcam usage by authenticating users before camera access. It also detects intrusion attempts, captures snapshots of unauthorized users, logs security events, and sends real-time email alerts to the administrator.

This project was developed as part of a B.Tech cybersecurity project and demonstrates practical applications of:

- Cybersecurity
- Computer Vision
- Desktop Application Development
- Authentication Systems
- Database Management

---

# ✨ Features

- 🔐 Username & Password Authentication
- 😊 Face Recognition Authentication (LBPH)
- 📧 OTP Verification
- 🔑 Password Reset via Email
- 📸 Intruder Snapshot Capture
- 🚨 Unauthorized Webcam Access Detection
- 📩 Email Alerts
- 📋 Activity Logging
- 👤 Role-Based Access Control (RBAC)
- 📅 Webcam Access Scheduling
- 📄 PDF Security Report Generation
- 🖥️ Modern PyQt5 Desktop Interface

---

# 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Application Development |
| PyQt5 | Desktop GUI |
| OpenCV (LBPH) | Face Recognition |
| SQLite | Database |
| SMTP | Email Alerts |
| Windows Registry | Webcam Enable/Disable |
| ReportLab | PDF Report Generation |

---

# 📂 Project Structure

```
WebcamSecurityTool/
│
├── alerts/
├── assets/
├── auth/
├── camera/
├── database/
├── gui/
├── faces/
├── logs/
├── main.py
├── config.py
├── scheduler.py
├── reports.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YourUsername/webcam-spyware-detection.git
```

Move into the project

```bash
cd webcam-spyware-detection
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

### Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

---

# 📸 Screenshots

> Add screenshots here.

| Login | Dashboard |
|-------|-----------|
| ![](screenshots/login.png) | ![](screenshots/dashboard.png) |

| User Management | Intruder Detection |
|----------------|--------------------|
| ![](screenshots/users.png) | ![](screenshots/intruder.png) |

---

# 🔒 Security Features

- Face Recognition Authentication
- OTP Verification
- Webcam Access Control
- Intruder Detection
- Email Notifications
- Role-Based Access Control
- Activity Logging
- Security Report Generation

---

# 📊 Future Enhancements

- Multi-camera Support
- AI-based Face Recognition
- Cloud Backup
- Mobile Notifications
- Live Security Dashboard
- Facial Anti-Spoofing

---

# ⚠️ Known Limitations

- Windows-only registry-based webcam control.
- LBPH performs best with consistent lighting.
- OTPs are stored in memory during runtime.
- Designed for educational and research purposes.

---

# 👨‍💻 Author

**Pragan**

B.Tech Computer Science Engineering

Cybersecurity & Python Developer

---

# 📜 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you found this project useful, consider giving it a **Star ⭐** on GitHub.
