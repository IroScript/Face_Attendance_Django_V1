# attendance/utils.py
from datetime import datetime, timedelta

def get_attendance_status(attendance):
    if not attendance:
        return "Not Marked"
    if attendance.time_in and attendance.time_out:
        return "Complete"
    if attendance.time_in:
        return "Checked In"
    return "Not Marked"

def is_late_arrival(time_in):
    if not time_in:
        return False
    target_time = datetime.strptime('09:00', '%H:%M').time()
    return time_in > target_time