import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np

from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    train_classifier
)

from src.pipelines.voice_pipeline import get_voice_embedding

from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)

import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


# ---------------- DASHBOARD ---------------- #

def student_dashboard():

    student_data = st.session_state.student_data

    # USING USN
    student_id = student_data['usn']

    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')

    with c1:
        header_dashboard()

    with c2:

        st.subheader(f"Welcome, {student_data['name']}")

        if st.button(
            "Logout",
            type='secondary',
            key='student_logout_btn'
        ):
            st.session_state.clear()
            st.rerun()

    st.write("")

    c1, c2 = st.columns(2)

    with c1:
        st.header('Your Enrolled Subjects')

    with c2:

        if st.button(
            'Enroll in Subject',
            type='primary',
            use_container_width=True,
            key='enroll_subject_btn'
        ):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects...'):

        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:

        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {
                "total": 0,
                "attended": 0
            }

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):

        sub = sub_node['subjects']
        sid = sub['subject_id']

        stats = stats_map.get(
            sid,
            {
                "total": 0,
                "attended": 0
            }
        )

        def unenroll_button(sid=sid, sub=sub):

            if st.button(
                "Unenroll from this course",
                type='tertiary',
                use_container_width=True,
                icon='🗑️',
                key=f"unenroll_{sid}"
            ):

                unenroll_student_to_subject(student_id, sid)

                st.toast(
                    f"Unenrolled from {sub['name']} successfully!"
                )

                st.rerun()

        with cols[i % 2]:

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button
            )

    footer_dashboard()


# ---------------- LOGIN SCREEN ---------------- #

def student_screen():

    style_background_dashboard()
    style_base_layout()

    # CHECK LOGIN
    if (
        st.session_state.get("is_logged_in")
        and "student_data" in st.session_state
    ):
        student_dashboard()
        return

    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='large'
    )

    with c1:
        header_dashboard()

    with c2:

        if st.button(
            "Go back to Home",
            type='secondary',
            key='student_home_btn'
        ):

            st.session_state['login_type'] = None
            st.rerun()

    st.markdown(
        "<h2 style='text-align:center;'>Login using FaceID</h2>",
        unsafe_allow_html=True
    )

    st.write("")
    st.write("")

    show_registration = False

    photo_source = st.camera_input(
        "Position your face in the center"
    )

    if photo_source:

        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning...'):

            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:

                st.warning('Face not found!')

            elif num_faces > 1:

                st.warning('Multiple faces found!')

            else:

                if detected:

                    student_id = list(detected.keys())[0]

                    all_students = get_all_students()

                    # MATCH USING USN
                    student = next(
                        (
                            s for s in all_students
                            if s['usn'] == student_id
                        ),
                        None
                    )

                    if student:

                        st.session_state.clear()

                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student

                        st.toast(
                            f"Welcome Back {student['name']} 👋"
                        )

                        time.sleep(1)

                        st.rerun()

                else:

                    st.info(
                        'Face not recognized! Register new profile below.'
                    )

                    show_registration = True

    # ---------------- REGISTRATION ---------------- #

    if show_registration:

        with st.container(border=True):

            st.header('Register New Profile')

            # FIXED USN INPUT
            new_usn = st.text_input(
                "Enter your USN",
                placeholder='E.g. 1RV23CS001'
            )

            # FIXED NAME INPUT
            new_name = st.text_input(
                "Enter your name",
                placeholder='E.g. John Doe'
            )

            st.subheader('Optional: Voice Enrollment')

            st.info(
                "Upload your voice sample for voice attendance"
            )

            audio_data = st.file_uploader(
                "Upload voice sample (optional)",
                type=["wav", "mp3", "m4a"]
            )

            if st.button(
                'Create Account',
                type='primary',
                key='create_student_account_btn'
            ):

                # FIXED CONDITION
                if new_name and new_usn:

                    with st.spinner('Creating profile...'):

                        img = np.array(Image.open(photo_source))

                        encodings = get_face_embeddings(img)

                        if encodings:

                            face_emb = encodings[0].tolist()

                            voice_emb = None

                            if audio_data:

                                voice_emb = get_voice_embedding(
                                    audio_data.read()
                                )

                            # FIXED FUNCTION CALL
                            response_data = create_student(
                                usn=new_usn,
                                new_name=new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb
                            )

                            if response_data:

                                train_classifier()

                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'

                                st.session_state.student_data = (
                                    response_data[0]
                                )

                                st.toast(
                                    f"Profile Created! Hi {new_name} 👋"
                                )

                                time.sleep(1)

                                st.rerun()

                        else:

                            st.error(
                                "Couldn't capture facial features"
                            )

                else:

                    st.warning(
                        'Please enter your name and USN!'
                    )

    footer_dashboard()