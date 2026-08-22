import src.database.config as config
import bcrypt


def safe_query(query_fn):
    """
    Executes a Supabase database query with automatic reconnection retry
    to handle stale httpx connection pools or temporary network glitches.
    """
    try:
        return query_fn(config.supabase)
    except Exception as e:
        print("Database query warning (reconnecting Supabase client):", e)
        try:
            config.supabase = config.get_supabase_client()
            return query_fn(config.supabase)
        except Exception as retry_err:
            print("Database query retry failed:", retry_err)
            return None


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    try:
        return bcrypt.checkpw(pwd.encode(), hashed.encode())
    except Exception:
        return False


def check_teacher_exists(username):
    res = safe_query(
        lambda db: db.table("teachers").select("username").eq("username", username).execute()
    )
    return len(res.data) > 0 if res and res.data else False


def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    res = safe_query(
        lambda db: db.table("teachers").insert(data).execute()
    )
    return res.data if res else None


def teacher_login(username, password):
    res = safe_query(
        lambda db: db.table("teachers").select("*").eq("username", username).execute()
    )

    if res and res.data:
        teacher = res.data[0]
        if check_pass(password, teacher['password']):
            return teacher

    return None


def get_all_students():
    res = safe_query(
        lambda db: db.table('students').select("*").execute()
    )
    return res.data if res and res.data else []


def create_student(usn, new_name, face_embedding=None, voice_embedding=None):
    data = {
        'usn': usn,
        'name': new_name,
        'face_embedding': face_embedding,
        "voice_embedding": voice_embedding
    }
    res = safe_query(
        lambda db: db.table('students').insert(data).execute()
    )
    return res.data if res else None


def create_subject(subject_code, name, section, teacher_id):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }
    res = safe_query(
        lambda db: db.table("subjects").insert(data).execute()
    )
    return res.data if res else None


def get_teacher_subjects(teacher_id):
    res = safe_query(
        lambda db: (
            db.table('subjects')
            .select("*, subject_students(count), attendance_logs(timestamp)")
            .eq("teacher_id", teacher_id)
            .execute()
        )
    )

    subjects = res.data if res and res.data else []

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


def enroll_student_to_subject(usn, subject_id):
    data = {'usn': usn, "subject_id": subject_id}
    res = safe_query(
        lambda db: db.table('subject_students').insert(data).execute()
    )
    return res.data if res else None


def unenroll_student_to_subject(usn, subject_id):
    res = safe_query(
        lambda db: (
            db.table('subject_students')
            .delete()
            .eq('usn', usn)
            .eq('subject_id', subject_id)
            .execute()
        )
    )
    return res.data if res else None


def get_student_subjects(usn):
    res = safe_query(
        lambda db: (
            db.table('subject_students')
            .select('*, subjects(*)')
            .eq('usn', usn)
            .execute()
        )
    )
    return res.data if res and res.data else []


def get_student_attendance(usn):
    res = safe_query(
        lambda db: (
            db.table('attendance_logs')
            .select('*, subjects(*)')
            .eq('usn', usn)
            .execute()
        )
    )
    return res.data if res and res.data else []


def create_attendance(logs):
    if not logs:
        return None

    formatted_logs = []
    for log in logs:
        usn = log.get("usn") or log.get("student_id")
        if not usn:
            continue
        formatted_logs.append({
            "usn": usn,
            "subject_id": log.get("subject_id"),
            "timestamp": log.get("timestamp"),
            "is_present": log.get("is_present", False)
        })

    if not formatted_logs:
        return None

    res = safe_query(
        lambda db: db.table("attendance_logs").insert(formatted_logs).execute()
    )
    return res.data if res else None


def get_attendance_for_teacher(teacher_id):
    res = safe_query(
        lambda db: (
            db.table('attendance_logs')
            .select("*, subjects!inner(*)")
            .eq('subjects.teacher_id', teacher_id)
            .execute()
        )
    )
    return res.data if res and res.data else []