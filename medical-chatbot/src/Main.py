# Main.py
import streamlit as st
from sql import init_db, init_alerts_table, add_patient, get_patient, update_patient_record, get_all_patients, add_chat_message, get_chat_history
from Logic import handle_query
from food2 import get_food_suggestions
from drugs import get_medications_for_condition
from voice_assistant import listen_for_voice_input, speak_text, stop_speaking
from notifications import notifications_sidebar
import os


# Initialize the database
init_db()
init_alerts_table()

st.set_page_config(page_title="Medical Report Analysis", layout="centered")

st.title("Medical Chatbot")

# Sidebar - Patient Management
st.sidebar.header("Patient Management")
patient_name = st.sidebar.text_input("Enter patient name:")
patient_age = st.sidebar.number_input("Enter patient age:", min_value=0, max_value=120)

if st.sidebar.button("Add New Patient"):
    add_patient(patient_name, patient_age)
    st.sidebar.success(f"Added new patient: {patient_name}")

# Dropdown to select a patient by ID
patient_id = st.sidebar.selectbox("Select Patient", ["Select a Patient"] + [row[0] for row in get_all_patients()])
if patient_id == "Select a Patient":
    patient_id = None

# Sidebar - Condition Monitoring Alert Setup
st.sidebar.header("Set Notifications")
notifications_sidebar()

# Initialize session state for chat history and conditions if they don't already exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = {}
if "patient_conditions" not in st.session_state:
    st.session_state["patient_conditions"] = {}
if "patient_symptoms" not in st.session_state:
    st.session_state["patient_symptoms"] = {}

# Display Patient Details and Chat History if a patient is selected
if patient_id:
    patient_info = get_patient(patient_id)
    if patient_info:
        st.subheader(f"Patient: {patient_info['name']}")
        st.write(f"Age: {patient_info.get('age', 'N/A')}")
        st.write(f"Known Conditions: {patient_info.get('diagnosis', 'None')}")
        st.write(f"Symptoms History: {patient_info.get('symptoms', 'None')}")

        # Chat history display
        st.write("### Chat History")
        chat_history = get_chat_history(patient_id)
        st.session_state["chat_history"][patient_id] = chat_history

        for message in st.session_state["chat_history"][patient_id]:
            if "reminder" in message["message"].lower():
                st.markdown(
                    f'<div style="background-color: #FFDDC1; padding: 10px; border-radius: 5px;">'
                    f"<strong>🔔 Reminder:</strong> {message['message']}</div>",
                    unsafe_allow_html=True
                )
            else:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['message']}")
                else:
                    st.markdown(f"**Assistant:** {message['message']}")

        # Additional options
        st.write("### Additional Options")
        if st.button("Diet Plans"):
            disease = patient_info.get('diagnosis', 'general health')
            diet_plan = get_food_suggestions(disease)
            st.write("### Personalized Diet Plan")
            st.write(diet_plan if diet_plan else "No diet plan available.")

        if st.button("Medication Alerts"):
            disease = patient_info.get('diagnosis', 'general health')
            medication_alert = get_medications_for_condition(disease)
            st.write("### Medication Alerts and Recommendations")
            st.write(medication_alert if medication_alert else "No medication alerts available.")

else:
    st.write("Please select a valid patient.")

# Chatbot user input section
st.write("### Chat with Assistant")
user_input = st.text_input("You:", "")

# Buttons for voice input and stop
voice_clicked = st.button("🎤 Voice Input")
stop_clicked = st.button("Stop")

if stop_clicked:
    stop_speaking()

if voice_clicked and patient_id:
    st.write("Listening for your voice input...")
    voice_input = listen_for_voice_input()
    if voice_input:
        st.write(f"**You (Voice):** {voice_input}")
        # Use the voice input as the user input and process it
        user_input = voice_input
        conditions = st.session_state["patient_conditions"].get(patient_id, [])
        symptoms = st.session_state["patient_symptoms"].get(patient_id, [])
        response, detected_conditions, detected_symptoms = handle_query(user_input, patient_id, conditions, symptoms)
        st.write(f"**Assistant:** {response}")
        speak_text(response)  # Speak the response

        # Update state and database
        st.session_state["patient_conditions"].setdefault(patient_id, []).extend(detected_conditions)
        st.session_state["patient_symptoms"].setdefault(patient_id, []).extend(detected_symptoms)
        update_patient_record(patient_id, symptoms=', '.join(st.session_state["patient_symptoms"][patient_id]))
        add_chat_message(patient_id, "user", user_input)
        add_chat_message(patient_id, "assistant", response)

# Send button
if st.button("Send"):
    if patient_id and user_input:
        st.write(f"**You:** {user_input}")
        conditions = st.session_state["patient_conditions"].get(patient_id, [])
        symptoms = st.session_state["patient_symptoms"].get(patient_id, [])
        response, detected_conditions, detected_symptoms = handle_query(user_input, patient_id, conditions, symptoms)
        st.write(f"**Assistant:** {response}")

        if voice_clicked:  # Check if the input was via voice
            speak_text(response)

        # Update state and database
        st.session_state["patient_conditions"].setdefault(patient_id, []).extend(detected_conditions)
        st.session_state["patient_symptoms"].setdefault(patient_id, []).extend(detected_symptoms)
        update_patient_record(patient_id, symptoms=', '.join(st.session_state["patient_symptoms"][patient_id]))
        add_chat_message(patient_id, "user", user_input)
        add_chat_message(patient_id, "assistant", response)


import os
import tempfile
import streamlit as st
from groq import handle_report_analysis  # Import the analysis function from groq.py

# Set the page configuration
# st.set_page_config(page_title="Medical Report Analysis", layout="centered")

# Set up the Google API key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = "AIzaSyDFRi2vqIvtoldhV5oCigCAkspWoKWWQrg"  # Replace this with your actual API key

# Main UI for uploading a file
st.title("Medical Report Analysis")
st.write("### Upload a Medical Report for Analysis")
st.write("Supported formats: PDF, JPG, JPEG, PNG")

# File uploader for PDF or image reports
uploaded_file = st.file_uploader("Drag and drop a file here, or click to browse", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    # Save the uploaded file to a temporary directory
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        tmp_file_path = tmp_file.name

    st.info("Processing the uploaded report...")

    try:
        # Call the report analysis function
        analysis_result = handle_report_analysis(tmp_file_path)

        # Display the analysis result
        if analysis_result.strip():
            st.write("### Report Analysis and Recommendations:")
            # Display the analysis result normally, without a box
            for line in analysis_result.split("\n"):
                st.write(line)
        else:
            st.error("No meaningful analysis could be performed. Please check the file content.")

    except Exception as e:
        st.error(f"An error occurred during report processing: {str(e)}")

    finally:
        # Clean up the temporary file
        os.remove(tmp_file_path)
else:
    st.write("Please upload a PDF or image report to analyze.")



