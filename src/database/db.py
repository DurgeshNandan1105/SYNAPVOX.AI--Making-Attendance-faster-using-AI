from src.database.config import supabase
import bcrypt


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    try:
        return bcrypt.checkpw(pwd.encode(), hashed.encode())
    except Exception:
        return False


def check_teacher_exists(username):
    try:
        response = supabase.table("teachers").select("username").eq("username", username).execute()
        return len(response.data) > 0 if response and response.data else False
    except Exception as e:
        print("Database error check_teacher_exists:", e)
        return False


def create_teacher(username, password, name):
    try:
        data = {"username": username, "password": hash_pass(password), "name": name}
        response = supabase.table("teachers").insert(data).execute()
        return response.data if response else None
    except Exception as e:
        print("Database error create_teacher:", e)
        raise e


def teacher_login(username, password):
    try:
        response = supabase.table("teachers").select("*").eq("username", username).execute()

        if response and response.data:
            teacher = response.data[0]

            if check_pass(password, teacher['password']):
                return teacher

        return None
    except Exception as e:
        print("Database error teacher_login:", e)
        return None


def get_all_students():
    try:
        response = supabase.table('students').select("*").execute()
        return response.data if response and response.data else []
    except Exception as e:
        print("Database error get_all_students:", e)
        return []


def create_student(usn, new_name, face_embedding=None, voice_embedding=None):
    try:
        data = {
            'usn': usn,
            'name': new_name,
            'face_embedding': face_embedding,
            "voice_embedding": voice_embedding
        }

        response = supabase.table('students').insert(data).execute()
        return response.data if response else None
    except Exception as e:
        print("Database error create_student:", e)
        return None


def create_subject(subject_code, name, section, teacher_id):
    try:
        data = {
            "subject_code": subject_code,
            "name": name,
            "section": section,
            "teacher_id": teacher_id
        }

        response = supabase.table("subjects").insert(data).execute()
        return response.data if response else None
    except Exception as e:
        print("Database error create_subject:", e)
        return None


def get_teacher_subjects(teacher_id):
    try:
        response = (
            supabase.table('subjects')
            .select("*, subject_students(count), attendance_logs(timestamp)")
            .eq("teacher_id", teacher_id)
            .execute()
        )

        subjects = response.data if response and response.data else []

        for sub in subjects:
            sub['total_students'] = (
                sub.get("subject_students", [{}])[0].get('count', 0)
                if sub.get('subject_students')
                else 0
            )

            attendance = sub.get('attendance_logs', [])
            unique_sessions = len(set(log['timestamp'] for log in attendance))
            sub['total_classes'] = unique_sessions

            sub.pop('subject_student', None)
            sub.pop('attendance_logs', None)

        return subjects
    except Exception as e:
        print("Database error get_teacher_subjects:", e)
        return []


def enroll_student_to_subject(usn, subject_id):
    try:
        data = {
            'usn': usn,
            "subject_id": subject_id
        }

        response = supabase.table('subject_students').insert(data).execute()
        return response.data if response else None
    except Exception as e:
        print("Database error enroll_student_to_subject:", e)
        return None


def unenroll_student_to_subject(usn, subject_id):
    try:
        response = (
            supabase.table('subject_students')
            .delete()
            .eq('usn', usn)
            .eq('subject_id', subject_id)
            .execute()
        )

        return response.data if response else None
    except Exception as e:
        print("Database error unenroll_student_to_subject:", e)
        return None


def get_student_subjects(usn):
    try:
        response = (
            supabase.table('subject_students')
            .select('*, subjects(*)')
            .eq('usn', usn)
            .execute()
        )

        return response.data if response and response.data else []
    except Exception as e:
        print("Database error get_student_subjects:", e)
        return []


def get_student_attendance(usn):
    try:
        response = (
            supabase.table('attendance_logs')
            .select('*, subjects(*)')
            .eq('usn', usn)
            .execute()
        )

        return response.data if response and response.data else []
    except Exception as e:
        print("Database error get_student_attendance:", e)
        return []


def create_attendance(logs):
    try:
        if not logs:
            raise Exception("Empty logs")

        formatted_logs = []

        for log in logs:
            usn = log.get("usn") or log.get("student_id")

            if not usn:
                print("Skipping invalid log:", log)
                continue

            formatted_logs.append({
                "usn": usn,
                "subject_id": log.get("subject_id"),
                "timestamp": log.get("timestamp"),
                "is_present": log.get("is_present", False)
            })

        if not formatted_logs:
            raise Exception("No valid attendance records to insert")

        response = (
            supabase
            .table("attendance_logs")
            .insert(formatted_logs)
            .execute()
        )

        return response.data if response else None

    except Exception as e:
        print("Attendance insert error:", e)
        raise e


def get_attendance_for_teacher(teacher_id):
    try:
        response = (
            supabase.table('attendance_logs')
            .select("*, subjects!inner(*)")
            .eq('subjects.teacher_id', teacher_id)
            .execute()
        )

        return response.data if response and response.data else []
    except Exception as e:
        print("Database error get_attendance_for_teacher:", e)
        return []