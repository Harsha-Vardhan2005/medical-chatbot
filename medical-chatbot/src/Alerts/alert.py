from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sql import get_connection
import smtplib
from email.mime.text import MIMEText
import os

# Fetch email credentials from environment variables
sender = os.getenv("EMAIL_SENDER")
password = os.getenv("EMAIL_PASSWORD")


def send_email(recipient, subject, message):
    """Send email to the recipient."""
    smtp_server = "smtp.gmail.com"

    try:
        # Construct the email
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        # Send the email using SMTP
        with smtplib.SMTP_SSL(smtp_server, 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

        print(f"Email sent to {recipient} successfully.")
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")


def send_notifications():
    """Check and send pending notifications."""
    try:
        connection = get_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)

            # Fetch pending notifications
            cursor.execute(
                "SELECT * FROM notifications WHERE schedule_time <= NOW() AND status = 'pending'"
            )
            notifications = cursor.fetchall()

            for notification in notifications:
                # Send the email
                send_email(
                    notification["email"],
                    f"Health Notification: {notification['condition_name']}",
                    notification["message"]
                )

                # Mark the notification as sent
                cursor.execute(
                    "UPDATE notifications SET status = 'sent' WHERE id = %s",
                    (notification["id"],)
                )

            connection.commit()
            cursor.close()
            connection.close()
    except Exception as e:
        print(f"Error processing notifications: {e}")


# Set up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(send_notifications, "interval", minutes=1)  # Check every minute
scheduler.start()

print("Notification scheduler started.")

# Prevent the script from exiting
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler stopped.")
