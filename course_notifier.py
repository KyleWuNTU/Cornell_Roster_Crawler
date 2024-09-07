import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Webpage URL
url = "the_url_of_the_course_page" #Leave only the specific course in the course page

# Function to send an email
def send_email():
    sender_email = "your_email@gmail.com"  # Enter your Gmail address
    receiver_email = "recipient_email@gmail.com"
    password = "your_app_password"  # Enter your Gmail app password

    subject = "MPSIS notification: there are open seats"
    body = ""  # Empty email body

    # Set up the email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Use Gmail's SMTP server to send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"Email sent to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check the course status
def check_course_status():
    try:
        # Send an HTTP GET request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the span elements that contain the course status
        open_element = soup.find('span', class_="tooltip-iws open-status-open-tt")
        closed_element = soup.find('span', class_="tooltip-iws open-status-closed-tt")

        # Determine the course status
        if open_element:
            return "Open"
        elif closed_element:
            return "Closed"
        else:
            return "Status not found"

    except Exception as e:
        return f"Error occurred: {e}"

# Main loop
while True:
    status = check_course_status()
    print(f"Current course status: {status}")
    
    # If the status is open, send an email
    if status == "Open":
        send_email()
        break  # Exit the loop after sending the email to avoid sending multiple emails

    # Wait 60 seconds before checking again
    time.sleep(60)

