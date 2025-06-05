# Logic.py
from llama_integration import get_symptoms, predict_disease, run_llama, get_diet_recommendation, get_medication_alert, get_treatment_options
from sql import update_patient_record, get_patient, add_chat_message
from food2 import get_food_suggestions 
from drugs import get_medications_for_condition
from datetime import datetime


def handle_query(user_input, patient_id, conditions, symptoms):
    """
    Process user queries and provide appropriate responses based on conditions and symptoms.
    """
    user_input = user_input.lower().strip()
    response = ""
    detected_conditions = []
    detected_symptoms = []

    try:
        # Check if the user is reporting multiple symptoms with phrases like "I am having" or "Symptoms are"
        if "i am having" in user_input or "symptoms are" in user_input:
            symptom_list = (
                user_input.replace("i am having", "")
                .replace("symptoms are", "")
                .strip()
                .split(", ")
            )
            detected_symptoms.extend(symptom_list)
            # Predict disease based on symptoms
            disease_prediction = predict_disease(detected_symptoms)
            response = f"Based on your symptoms, the most likely disease could be {disease_prediction}. Would you like to know more about its symptoms or treatment options?"
            # Update patient record with detected symptoms
            update_patient_record(patient_id, symptoms=", ".join(detected_symptoms))

        # Check if the user is asking about symptoms of a specific condition
        elif "symptoms of" in user_input:
            condition_name = extract_condition_name(user_input, conditions)
            if condition_name:
                response = get_symptoms(condition_name)  # Fetch symptoms for the condition
            else:
                response = run_llama(user_input)  # Fallback to LLaMA

        # Check if the user is asking for treatment options for a specific condition
        elif "treatment for" in user_input or "what are treatment options for" in user_input:
            condition_name = extract_condition_name(user_input, conditions)
            if condition_name:
                response = get_treatment_options(condition_name)  # Fetch treatment options
            else:
                response = run_llama(user_input)  # Fallback to LLaMA

        # Check if the user is reporting a disease with "I am having [disease]"
        elif "i am having" in user_input:
            condition_name = user_input.replace("i am having", "").strip()
            if condition_name:
                # Fetch symptoms and treatment options for the condition
                symptoms = get_symptoms(condition_name)
                treatment = get_treatment_options(condition_name)
                response = (
                    f"I see you are having {condition_name}. Here are a few symptoms: {symptoms}. "
                    f"Treatment options include: {treatment}."
                )
                # Update patient record with the condition
                update_patient_record(patient_id, diagnosis=condition_name)
            else:
                response = run_llama(user_input)  # Fallback to LLaMA

        # Fallback to LLaMA for any unrecognized input
        else:
            response = run_llama(user_input)

    except Exception as e:
        print(f"Error in handle_query: {e}")
        response = run_llama(user_input)  # Fallback to LLaMA in case of any exceptions

    return response, detected_conditions, detected_symptoms


def extract_condition_name(user_input, known_conditions):
    """
    Helper function to extract a condition name from user input if mentioned,
    or use a known condition if available.
    """
    user_input_lower = user_input.lower()
    
    # First, check against known conditions
    for condition in known_conditions:
        if condition.lower() in user_input_lower:
            return condition
    
    # Extract potential condition directly from user input
    if "symptoms of" in user_input_lower or "symptoms for" in user_input_lower:
        words = user_input_lower.split()
        try:
            # Look for the word after "of" or "for"
            if "of" in words:
                condition_index = words.index("of") + 1
            elif "for" in words:
                condition_index = words.index("for") + 1
            else:
                return None
            if condition_index < len(words):
                return words[condition_index].capitalize()  # Capitalize for consistency
        except Exception as e:
            print(f"Error extracting condition: {e}")
            return None
    
    # Default to None if no condition is found
    return None


def handle_diet_recommendation(patient_id):
    """Retrieve diet recommendation based on patient's diagnosis."""
    patient = get_patient(patient_id)
    if not patient:
        return "Patient data not found."

    disease = patient.get('diagnosis') or "general health" 
    diet_plan = get_food_suggestions(disease) 
    update_patient_record(patient_id, diet=diet_plan) 
    return diet_plan


def handle_medication_alert(patient_id):
    """Retrieve medication alert based on patient's diagnosis."""
    patient = get_patient(patient_id)
    if not patient:
        return "Patient data not found."

    disease = patient.get('diagnosis') or "general health"
    medication_alert = get_medications_for_condition(disease)
    update_patient_record(patient_id, medication=medication_alert)
    return medication_alert

# def handle_report_analysis(file_path, api_key):
#     """
#     Extract text from a report (PDF/image) and analyze it using Groq's LLaMA 70B.
#     """
#     import PyPDF2
#     import pytesseract
#     from PIL import Image
#     import os

#     text = ""

#     try:
#         # Extract text based on file type
#         if file_path.endswith(".pdf"):
#             with open(file_path, "rb") as f:
#                 pdf_reader = PyPDF2.PdfReader(f)
#                 text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
#         elif file_path.endswith((".jpg", ".jpeg", ".png")):
#             image = Image.open(file_path)
#             text = pytesseract.image_to_string(image)
#         else:
#             return "Unsupported file format. Please upload a PDF or an image file."

#         if not text.strip():
#             return "No readable text found in the uploaded file. Please check the file content."

#         # Analyze the extracted text using the Groq API
#         analysis_result = analyze_report_with_groq(text, api_key)
#         return analysis_result
#     except Exception as e:
#         return f"Error processing report: {str(e)}"
#     finally:
#         # Cleanup: Delete the temporary file if it exists
#         if os.path.exists(file_path):
#             os.remove(file_path)


import os
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from easyocr import Reader
from llama_integration import run_llama
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def handle_report_analysis(file_path):
    """
    Extracts text from a lab report (PDF/image) and analyzes it using the LLaMA model with context.
    """
    text = ""
    try:
        # Extract text based on file type
        if file_path.lower().endswith(".pdf"):
            pdf_reader = PdfReader(file_path)
            text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)  # OCR for image
        else:
            return "Unsupported file format. Please upload a PDF or image file."

        # Preprocess text
        text = preprocess_text(text)
        if not text.strip():
            return "No readable text found in the uploaded file. Please check the file content."

        # Analyze the extracted text using LLaMA
        prompt = f"""
        You are a medical expert. Analyze the following medical report and summarize it professionally:
        {text}
        """
        response = run_llama(prompt)
        return response

    except Exception as e:
        return f"Error processing the report: {str(e)}"


def preprocess_text(text):
    """
    Clean and preprocess extracted text for better analysis.
    """
    lines = text.split("\n")
    filtered_lines = [
        line for line in lines if not any(
            keyword in line.lower()
            for keyword in ["nric", "passport", "doctor", "patient"]
        )
    ]
    return "\n".join(filtered_lines)
