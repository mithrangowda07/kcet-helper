import time


def generate_jitsi_meeting_link(studying_student_id, counselling_student_id):
    timestamp = int(time.time())
    room_name = f"kcet-helper-{studying_student_id}-{counselling_student_id}-{timestamp}"
    return f"https://meet.jit.si/{room_name}"
