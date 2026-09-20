"""
Schedule Management background worker. Uses the `schedule` library + a
daemon thread. Re-reads the schedules table every _REBUILD_INTERVAL_SECONDS,
so changes made in gui/schedule_window.py take effect without restarting
the app.

Each DB row is a time RANGE ("from 17:00 to 18:00"): the camera is enabled
at start_time and disabled at end_time -- two jobs are registered per row.
"""
import threading
import time

import schedule as schedule_lib

from database.schedules import list_schedules
from camera.camera_control import enable_camera, disable_camera

_REBUILD_INTERVAL_SECONDS = 30
_stop_event = threading.Event()


def _apply_schedules() -> None:
    schedule_lib.clear()
    for row in list_schedules():
        schedule_lib.every().day.at(row["start_time"]).do(enable_camera, username="scheduler")
        schedule_lib.every().day.at(row["end_time"]).do(disable_camera, username="scheduler")


def _run_loop() -> None:
    last_rebuild = 0.0
    while not _stop_event.is_set():
        now = time.time()
        if now - last_rebuild > _REBUILD_INTERVAL_SECONDS:
            _apply_schedules()
            last_rebuild = now
        schedule_lib.run_pending()
        time.sleep(1)


def start_scheduler() -> threading.Thread:
    """Call once from main.py. Runs forever in a daemon thread."""
    _apply_schedules()
    thread = threading.Thread(target=_run_loop, daemon=True)
    thread.start()
    return thread


def stop_scheduler() -> None:
    _stop_event.set()
