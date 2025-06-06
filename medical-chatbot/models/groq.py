import os
from PyPDF2 import PdfReader
from PIL import Image, ImageOps
import pytesseract
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from llama_integration import run_llama



def extract_text_from_file(file_path):
    """
    Extract text from a PDF or image file.
    """
    try:
        pytesseract.pytesseract.tesseract_cmd = r"C:/Users/Hp/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
        if file_path.lower().endswith(".pdf"):
            # Extract text from PDF
            pdf_reader = PdfReader(file_path)
            text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
            if not text.strip():
                return "No text extracted. PDF might contain images only."
            return text

        elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            # Preprocess the image for better OCR
            image = Image.open(file_path)
            preprocessed_image = preprocess_image(image)
            text = pytesseract.image_to_string(preprocessed_image, config="--psm 6")
            if not text.strip():
                return "No text could be extracted from the image."
            return text

        else:
            return "Unsupported file format. Please upload a PDF or image file."

    except Exception as e:
        return f"Error extracting text: {str(e)}"


def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy.
    """
    try:
        # Convert the image to grayscale
        grayscale = ImageOps.grayscale(image)
        # Enhance contrast
        enhanced = ImageOps.autocontrast(grayscale)
        return enhanced
    except Exception as e:
        return f"Error preprocessing image: {str(e)}"


def preprocess_text(text):
    """
    Clean and preprocess the extracted text.
    """
    lines = text.split("\n")
    return "\n".join(line.strip() for line in lines if line.strip())


def get_vector_store(text_chunks):
    """
    Create a FAISS vector store using Google Generative AI embeddings.
    """
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=os.getenv("your-api-key"), model="models/embedding-001"
        )
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        return vector_store
    except Exception as e:
        return f"Error creating vector store: {str(e)}"


def analyze_report_with_llama(text):
    """
    Analyze the extracted text using the LLaMA model.
    """
    # Refined Prompt
    prompt = f"""
    You are a highly knowledgeable medical assistant specializing in medical report analysis. Based on the following report, analyze the findings and provide:

    1. A summary of the patient's key details (e.g., name, age, gender).
    2. Observations from the tests or examinations, with explanations of what the findings might indicate.
    3. Recommendations, including follow-up actions, further diagnostic tests, or treatments, based on the findings. Provide detailed insights even if the report doesn't explicitly specify recommendations.

    Report Content:
    {text}

    Provide your response in a professional and structured format with clear sections for Summary, Observations, and Recommendations.
    """
    try:
        # Check if the input text is valid
        if not text.strip():
            return "Error: The provided report content is empty or invalid."

        # Debugging: Print the generated prompt
        print("Generated Prompt:")
        print(prompt)

        # Call the LLaMA model to process the prompt
        result = run_llama(prompt)

        # Debugging: Print the LLaMA output
        print("LLaMA Response:")
        print(result)

        # Return the result if it's not empty
        if result.strip():
            return result
        else:
            return "Error: LLaMA did not produce a valid response."

    except Exception as e:
        # Return a clear error message if something goes wrong
        return f"Error analyzing report with LLaMA: {str(e)}"


def handle_report_analysis(file_path):
    """
    Main function to analyze a medical report:
    1. Extract text from the file (PDF or image).
    2. Preprocess the text.
    3. Analyze the content using LLaMA.
    """
    try:
        # Step 1: Extract Text
        extracted_text = extract_text_from_file(file_path)
        if not extracted_text.strip() or "Error" in extracted_text:
            return extracted_text  # Return error or notification if text extraction failed

        # Debugging: Print extracted text
        print("Extracted Text:")
        print(extracted_text)

        # Step 2: Preprocess Text
        preprocessed_text = preprocess_text(extracted_text)

        # Debugging: Print preprocessed text
        print("Preprocessed Text:")
        print(preprocessed_text)

        # Step 3: Analyze the Report Using LLaMA
        analysis_result = analyze_report_with_llama(preprocessed_text)

        # Debugging: Print analysis result
        print("Analysis Result:")
        print(analysis_result)

        return analysis_result

    except Exception as e:
        return f"Error during analysis: {str(e)}"

