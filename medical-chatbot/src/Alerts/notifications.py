import streamlit as st
from conditions import condition_messages
from sql import get_connection
from datetime import datetime, timedelta

def notifications_sidebar():
    """UI for setting notifications."""
    condition_name = st.sidebar.text_input("Condition Name (e.g., pneumonia):")
    email = st.sidebar.text_input("Recipient Email:")
    notification_time = st.sidebar.number_input("Notify in (days):", min_value=1, max_value=30)

    if st.sidebar.button("Set Notification"):
        if condition_name and email:
            # Fetch the message from the dictionary
            message = condition_messages.get(
                condition_name.lower(),
                "Please consult your doctor for further advice."  # Default message
            )

            # Schedule time for the notification
            schedule_time = datetime.now() + timedelta(days=notification_time)

            # Debug: Log values for verification
            st.sidebar.write(f"Condition: {condition_name}, Email: {email}, Schedule: {schedule_time}, Message: {message}")

            # Save to the database
            connection = get_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "INSERT INTO notifications (condition_name, email, schedule_time, message) VALUES (%s, %s, %s, %s)",
                        (condition_name, email, schedule_time, message)
                    )
                    connection.commit()
                    cursor.close()
                    connection.close()
                    st.sidebar.success(f"Notification set for {email} about {condition_name}.")
                except Exception as e:
                    st.sidebar.error(f"Error setting notification: {e}")
            else:
                st.sidebar.error("Database connection failed.")
        else:
            st.sidebar.error("Please provide both a condition and an email address.")
