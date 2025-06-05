# drugs.py
import requests

def get_medications_for_condition(condition):
    api_key =  '1cX81CAwWZtSfa8bvB9gaFBdA5cp5gcFdV1u4x2b'
    limit = 8  # Number of results to retrieve
    url = (
        f'https://api.fda.gov/drug/label.json?'
        f'api_key={api_key}&'
        f'search=indications_and_usage:"{condition}"&'
        f'limit={limit}'
    )

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        medications = []
        for result in data.get('results', []):
            brand_name = result.get('openfda', {}).get('brand_name', ['N/A'])[0]
            generic_name = result.get('openfda', {}).get('generic_name', ['N/A'])[0]
            manufacturer = result.get('openfda', {}).get('manufacturer_name', ['N/A'])[0]
            purpose = result.get('purpose', ['N/A'])[0]
            indications = result.get('indications_and_usage', ['N/A'])[0]
            
            # Add each medication detail to the list with formatting
            medication_info = (
                f"**Brand Name:** {brand_name}\n"
                f"**Generic Name:** {generic_name}\n"
                f"**Manufacturer:** {manufacturer}\n"
                f"**Purpose:** {purpose}\n"
                f"**Indications and Usage:** {indications[:300]}..."  # Truncate for readability
            )
            medications.append(medication_info)

        return "### Medication suggestions for '{}'\n\n".format(condition) + "\n\n".join(medications)
    else:
        return "Failed to retrieve data from the FDA API."
