import mysql.connector
from mysql.connector import Error

DB_HOST = 'localhost'
DB_USER = 'root' 
DB_PASSWORD = 'Harshavard2005'
DB_NAME = 'diet'

def get_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def init_db():
    """Initialize the database with patients and patient_chats tables."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create patients table with diet and medication fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                age INT,
                symptoms TEXT,
                diagnosis TEXT,
                diet_recommendation TEXT,
                medication_alerts TEXT
            )
        ''')
        
        # Create patient_chats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_chats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                role ENUM('user', 'assistant'),
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                condition_name VARCHAR(255),
                email VARCHAR(255),
                schedule_time DATETIME,
                message TEXT,
                status ENUM('pending', 'sent') DEFAULT 'pending'
            )
        ''')
        
        connection.commit()
        cursor.close()
        connection.close()

# sql.py
def init_alerts_table():
    """Initialize the alerts table to store user-specific condition monitoring alerts."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create alerts table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                `condition` VARCHAR(255),
                frequency ENUM('daily', 'weekly', 'monthly'),
                last_alert TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        ''')
        
        connection.commit()
        cursor.close()
        connection.close()



def add_patient(name, age):
    """Add a new patient to the database."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO patients (name, age, symptoms, diagnosis, diet_recommendation, medication_alerts) VALUES (%s, %s, '', '', '', '')", (name, age))
        connection.commit()
        cursor.close()
        connection.close()

def get_patient(patient_id):
    """Retrieve a patient record from the database by ID."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        cursor.close()
        connection.close()
        return patient if patient else {}

def update_patient_record(patient_id, symptoms = None, diagnosis = None, diet=None, medication=None):
    """Update a patient's symptoms, diagnosis, diet, and medication in the database."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE patients SET symptoms = COALESCE(%s, symptoms), diagnosis = COALESCE(%s, diagnosis), diet_recommendation = COALESCE(%s, diet_recommendation), medication_alerts = COALESCE(%s, medication_alerts) WHERE id = %s",
                       (symptoms, diagnosis, diet, medication, patient_id))
        connection.commit()
        cursor.close()
        connection.close()

def get_all_patients():
    """Retrieve all patient records from the database."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM patients")
        patients = cursor.fetchall()
        cursor.close()
        connection.close()
        return patients

def add_chat_message(patient_id, role, message):
    """Add a chat message to the patient_chats table."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO patient_chats (patient_id, role, message) VALUES (%s, %s, %s)", (patient_id, role, message))
        connection.commit()
        cursor.close()
        connection.close()

def get_chat_history(patient_id):
    """Retrieve chat history for a specific patient."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT role, message, timestamp FROM patient_chats WHERE patient_id = %s ORDER BY timestamp", (patient_id,))
        chat_history = cursor.fetchall()
        cursor.close()
        connection.close()
        return chat_history

def delete_patient(patient_id):
    """Delete a patient's record and associated chat history from the database."""
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM patient_chats WHERE patient_id = %s", (patient_id,))
            cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
            connection.commit()
            print("Patient and associated chat history deleted successfully.")
        except Error as e:
            print(f"Error while deleting patient: {e}")
        finally:
            cursor.close()
            connection.close()
