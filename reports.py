"""
PDF Report Generator. Builds a simple security summary PDF from the DB.
"""
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import config
from database.logs import get_recent_activity, get_intruder_logs, get_failed_login_count, get_intruder_alert_count
from database.users import list_users


def generate_security_report() -> str:
    filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(config.LOGS_FOLDER, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    y = height - 50

    def line(text: str, size: int = 11, gap: int = 18) -> None:
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(50, y, text)
        y -= gap

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Webcam Security - Report")
    y -= 30

    line(f"Generated: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")
    line(f"Total users: {len(list_users())}")
    line(f"Total failed logins: {get_failed_login_count()}")
    line(f"Total intruder alerts: {get_intruder_alert_count()}")
    y -= 10

    line("Recent Activity:", size=13)
    for row in get_recent_activity(15):
        line(f"  {row['timestamp']} | {row['username']} | {row['action']}", size=9, gap=14)
        if y < 80:
            c.showPage()
            y = height - 50

    y -= 10
    line("Recent Intruder Events:", size=13)
    for row in get_intruder_logs(15):
        line(f"  {row['timestamp']} | {row['reason']} | attempted user: {row['username']}", size=9, gap=14)
        if y < 80:
            c.showPage()
            y = height - 50

    c.save()
    return filepath
