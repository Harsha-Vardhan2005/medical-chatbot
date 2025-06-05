import subprocess

def run_llama(prompt):
    """Runs the LLaMA model with the given prompt and returns the response."""
    try:
        print("Generated prompt for LLaMA:", prompt)  # Debugging line
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:latest'],
            input=prompt.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            response = result.stdout.decode('utf-8').strip()
            print("Response from LLaMA:", response)  # Debugging line
            return response
        else:
            error_message = result.stderr.decode('utf-8')
            print("Error in LLaMA subprocess:", error_message)
            return f"Error: {error_message}"
    except Exception as e:
        print("Exception in run_llama:", str(e))
        return f"An error occurred: {str(e)}"

def get_symptoms(disease_name):
    """Uses the LLaMA model to get symptoms for a specific disease."""
    prompt = f"Briefly list the common symptoms of {disease_name}."
    return run_llama(prompt)

# llama_integration.py
def get_treatment_options(disease_name):
    """Uses the LLaMA model to get treatment options for a specific disease."""
    prompt = f"Provide common treatment options for managing {disease_name}."
    return run_llama(prompt)


def predict_disease(symptoms):
    """Uses the LLaMA model to predict the most likely disease based on symptoms."""
    prompt = f"List the most likely disease for these symptoms: {', '.join(symptoms)}."
    return run_llama(prompt)


def get_diet_recommendation(disease):
    """Uses the LLaMA model to get a general diet recommendation based on disease."""
    prompt = (
        f"Provide general dietary guidance specifically for managing {disease}. "
        "This should focus on diet tips and recommendations that are commonly beneficial for this condition."
    )
    return run_llama(prompt)

def get_medication_alert(disease):
    """Uses the LLaMA model to get general medication alerts based on disease."""
    prompt = (
        f"Provide general medication guidance specifically for managing {disease}. "
        "Include any common precautions and general advice to consider for someone with this condition."
    )
    return run_llama(prompt)
