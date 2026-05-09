import streamlit as st
import pandas as pd

from datetime import datetime

from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_results import (
    show_attendance_result
)


@st.dialog('Voice Attendance')
def voice_attendance_dialog(selected_subject_id):

    st.write(
        'Record audio of students saying '
        '"I am present". Then AI will '
        'recognize the students.'
    )

    audio_data = st.audio_input(
        "Record classroom audio"
    )

    if st.button(
        'Analyze Audio',
        width='stretch',
        type='primary'
    ):

        # Check if audio was recorded
        if audio_data is None:
            st.warning(
                "Please record audio first"
            )
            st.stop()

        with st.spinner(
            'Processing Audio data...'
        ):

            # Fetch enrolled students
            enrolled_res = (
                supabase
                .table('subject_students')
                .select("*, students(*)")
                .eq(
                    'subject_id',
                    selected_subject_id
                )
                .execute()
            )

            enrolled_students = (
                enrolled_res.data
            )

            # No students
            if not enrolled_students:
                st.warning(
                    'No students enrolled '
                    'in this course'
                )
                return

            # Build candidate dictionary
            candidates_dict = {
                s['students']['usn']:
                s['students']['voice_embedding']

                for s in enrolled_students

                if s.get('students')
                and s['students'].get(
                    'voice_embedding'
                )
            }

            # No voice profiles
            if not candidates_dict:
                st.error(
                    'No enrolled students '
                    'have voice profiles '
                    'registered'
                )
                return

            # Read audio
            audio_bytes = audio_data.read()

            # Detect speakers
            detected_scores = (
                process_bulk_audio(
                    audio_bytes,
                    candidates_dict
                )
            )

            results = []
            attendance_to_log = []

            current_timestamp = (
                datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
            )

            # Process attendance
            for node in enrolled_students:

                if not node.get('students'):
                    continue

                student = node['students']

                score = detected_scores.get(
                    student['usn'],
                    0.0
                )

                is_present = score > 0

                results.append({
                    "Name": student['name'],
                    "USN": student['usn'],
                    "Score": (
                        round(score, 3)
                        if is_present
                        else "-"
                    ),
                    "Status": (
                        "✅ Present"
                        if is_present
                        else "❌ Absent"
                    )
                })

                attendance_to_log.append({
                    'usn': student['usn'],
                    'subject_id':
                        selected_subject_id,
                    'timestamp':
                        current_timestamp,
                    'is_present':
                        bool(is_present)
                })

            # Store results
            st.session_state[
                'voice_attendance_results'
            ] = (
                pd.DataFrame(results),
                attendance_to_log
            )

    # Show results
    if st.session_state.get(
        'voice_attendance_results'
    ):

        st.divider()

        df_results, logs = (
            st.session_state[
                'voice_attendance_results'
            ]
        )

        show_attendance_result(
            df_results,
            logs
        )