import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

import time


@st.dialog("Enroll in Subject")
def enroll_dialog():

    st.write(
        'Enter the subject code provided '
        'by your teacher to enroll'
    )

    join_code = st.text_input(
        'Subject Code',
        placeholder='Eg. CS101'
    )

    if st.button(
    'Enroll now',
    type='primary',
    use_container_width=True
    ):

        if join_code:

            res = (
                supabase
                .table('subjects')
                .select('subject_id, name, subject_code')
                .ilike('subject_code', join_code.strip())
                .execute()
            )

            if res.data:

                subject = res.data[0]

                student_id = (
                    st.session_state.student_data['usn']
                )

                check = (
                    supabase
                    .table('subject_students')
                    .select('*')
                    .eq('subject_id', subject['subject_id'])
                    .ilike('usn', student_id.strip())
                    .execute()
                )

                if check.data:

                    st.warning(
                        'You are already enrolled in this program'
                    )

                else:

                    res_enroll = enroll_student_to_subject(
                        student_id,
                        subject['subject_id']
                    )

                    if res_enroll:
                        st.success('Successfully enrolled!')
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error('Enrollment failed. Could not save to database.')

            else:

                st.error('Invalid subject code')

        else:

            st.warning('Please enter a subject code')