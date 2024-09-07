# Course Availability Notifier

This script checks the availability of a specific course on Cornell's course roster and sends an email notification when the course status changes to "Open." The script is intended to run on a personal device, such as your laptop or desktop computer. However, you can also deploy it on a cloud service like AWS Lambda with AWS EventBridge for scheduling.

## Prerequisites

- Python 3.x installed on your machine
- Required Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `smtplib` (built-in with Python)

You can install the necessary libraries using the following command:

```bash
pip install requests beautifulsoup4
```

## Usage on Personal Device

1. Clone or download this repository to your local machine.
2. Update the `url`, `sender_email`, `receiver_email`, and `password` variables in the script to match your course and email details.
3. Run the script:

```bash
python course_notifier.py
```

The script will periodically check the course status and send an email notification if the course becomes available.

## Running on AWS Lambda with AWS EventBridge

### Step 1: Preparing Python Packages with Lambda Layers

1. **Create a Virtual Environment:**

   First, create a virtual environment on your local machine:

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

2. **Install Required Packages:**

   Inside the virtual environment, install the required packages:

   ```bash
   pip install requests beautifulsoup4
   ```

3. **Package Dependencies:**

   Create a directory structure for your Lambda layer:

   ```bash
   mkdir -p lambda_layer/python
   ```

   Then, copy the installed packages to this directory:

   ```bash
   cp -r myenv/lib/python3.x/site-packages/* lambda_layer/python/
   ```

4. **Create a ZIP File:**

   Compress the `lambda_layer` directory into a ZIP file:

   ```bash
   cd lambda_layer
   zip -r9 ../lambda_layer.zip .
   cd ..
   ```

5. **Upload to AWS Lambda:**

   Go to the AWS Lambda Console, create a new Lambda function, and in the "Layers" section, choose "Add a layer."

   - Click "Create a new layer."
   - Upload the `lambda_layer.zip` file.
   - In the "Compatible runtimes" section, select `Python 3.x`.
   - After creating the layer, attach it to your Lambda function.

### Step 2: Modifying the Script for Lambda

1. **Adjust the Script:**

   Modify your script slightly to work with AWS Lambda's handler function:

   ```python
    import requests
    from bs4 import BeautifulSoup
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # URL of the course roster page
    url = "https://classes.cornell.edu/search/roster/FA24?q=MPS+Project&days-type=any&crseAttrs-type=any&breadthDistr-type=any&pi="

    # Email sending function
    def send_email():
        sender_email = "your_email@gmail.com"  # Enter your Gmail address
        receiver_email = "recipient_email@gmail.com"  # Enter the recipient's email address
        password = "your_app_password"  # Enter your Gmail app password

        subject = "MPSIS notification: there are open seats"
        body = "The course status is now OPEN. Please check the registration portal."

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

    # Lambda handler function
    def lambda_handler(event, context):
        status = check_course_status()
        print(f"Current course status: {status}")
        
        # If the status is open, send an email
        if status == "Open":
            send_email()

        return {
            'statusCode': 200,
            'body': status
        }


   ```

2. **Upload the Script:**

   In the AWS Lambda Console, upload your modified script as the Lambda function's code.

### Step 3: Setting Up AWS EventBridge to Trigger Lambda

1. **Create a Rule in AWS EventBridge:**

   Go to the AWS EventBridge Console and follow these steps:

   - Click on "Create rule."
   - Give your rule a name, like `CourseAvailabilityChecker`.
   - In the "Define pattern" section, choose "Event Source" as "EventBridge (formerly CloudWatch Events)."
   - Select "Schedule" and set the rate expression to run every minute, like:

     ```bash
     rate(1 minute)
     ```

2. **Set the Target as the Lambda Function:**

   - In the "Select targets" section, choose "Lambda function."
   - Select the Lambda function you created earlier.
   - Save the rule.

Your AWS Lambda function will now automatically run every minute, checking the course status and sending an email if the course becomes available.

## Additional Notes

- Ensure that your Lambda function has the necessary permissions to send emails using the SMTP server.
- If you encounter any issues, you can refer to the official [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) and [AWS EventBridge documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-run-lambda-schedule.html).

---

This README file provides step-by-step instructions for setting up the Python environment, creating Lambda layers, configuring AWS Lambda, and setting up a scheduler in AWS EventBridge.