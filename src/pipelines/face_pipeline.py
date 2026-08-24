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

    # Detect faces
    faces = detector(image_np, 1)

    encodings = []

    for face in faces:

        # Face landmarks
        shape = sp(image_np, face)

        # Generate embedding
        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(np.array(face_descriptor))

    return encodings


def train_classifier():
    """
    Kept for compatibility.
    No classifier training required.
    """
    return True


def predict_attendance(class_image_np):

    # Generate embeddings from uploaded image
    encodings = get_face_embeddings(class_image_np)

    detected_students = {}

    # Fetch all students from database
    student_db = get_all_students()

    if not student_db:

        return detected_students, [], len(encodings)

    # Keep all available USNs
    all_students = [
        student['usn'].lower() if student.get('usn') else ''
        for student in student_db
    ]

    # STRICT FACE MATCH THRESHOLD
    threshold = 0.5

    # Compare every detected face
    for encoding in encodings:

        best_match = None
        best_score = float("inf")

        for student in student_db:

            stored_embedding = student.get(
                'face_embedding'
            )

            # Skip students without embeddings
            if not stored_embedding:
                continue

            stored_embedding = np.array(
                stored_embedding,
                dtype=np.float64
            )

            # Euclidean distance
            distance = np.linalg.norm(
                stored_embedding - encoding
            )

            print(
                f"Checking {student['usn']} "
                f"Distance: {distance:.4f}"
            )

            # Keep best match only
            if distance < best_score:

                best_score = distance
                best_match = student['usn'].lower() if student.get('usn') else None

        # FINAL VERIFICATION
        if (
            best_match is not None
            and best_score <= threshold
        ):

            detected_students[best_match] = {
                "matched": True,
                "distance": round(
                    float(best_score),
                    4
                )
            }

            print(
                f"✅ MATCHED: {best_match} "
                f"Distance: {best_score:.4f}"
            )

        else:

            print(
                f"❌ NO CONFIDENT MATCH "
                f"(Best Score: {best_score:.4f})"
            )

    return (
        detected_students,
        all_students,
        len(encodings)
    )