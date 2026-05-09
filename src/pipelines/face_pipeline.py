import dlib
import numpy as np
import face_recognition_models
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():

    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


def get_face_embeddings(image_np):

    detector, sp, facerec = load_dlib_models()

    faces = detector(image_np, 1)

    encodings = []

    for face in faces:

        shape = sp(image_np, face)

        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(np.array(face_descriptor))

    return encodings


def train_classifier():
    """
    Kept for compatibility with existing code.
    No SVM training needed anymore.
    """
    return True


def predict_attendance(class_image_np):

    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    student_db = get_all_students()

    if not student_db:

        return detected_student, [], len(encodings)

    all_students = []

    for encoding in encodings:

        best_match = None
        best_score = 999

        for student in student_db:

            stored_embedding = student.get('face_embedding')

            if not stored_embedding:
                continue

            stored_embedding = np.array(stored_embedding)

            distance = np.linalg.norm(
                stored_embedding - encoding
            )

            all_students.append(student['usn'])

            print(
                f"Checking {student['usn']} "
                f"Distance: {distance}"
            )

            if distance < best_score:

                best_score = distance
                best_match = student['usn']

        # FACE MATCH THRESHOLD
        threshold = 0.75

        if best_match and best_score < threshold:

            detected_student[best_match] = True

            print(
                f"Matched: {best_match} "
                f"Score: {best_score}"
            )

        else:

            print("No match found")

    return (
        detected_student,
        list(set(all_students)),
        len(encodings)
    )