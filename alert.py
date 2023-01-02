import os
import logging
import logging.config
import ssl

from email.mime.text import MIMEText
from smtplib import SMTP, SMTPAuthenticationError, SMTPRecipientsRefused
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})

logging.basicConfig(
    format='[%(asctime)s] %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

class EmailAlert():
    def __init__(self, email, data):
        self.email = email
        self.data = data

    def send_alert(self):
        course_name = self.data['course']
        semester = self.data['semester']
        grade = self.data['grade']
        half_body = f'<br></br>Grade: {grade}' if self.data['view_grade'] else \
            'You may view this grade by logging into <a href="https://path.at.upenn.edu/student/landing">Path@Penn</a> and selecting Review my unofficial transcript,' \
            'or by logging into <a href="https://courses.upenn.edu/">Courses@Penn</a> and selecting Degree Audit & Advising.'
        msg_body = f'A grade has been posted for you in the course {course_name} for the {semester} term. {half_body}'

        msg = MIMEText(msg_body, 'html')
        msg["Subject"] = f'Grade posted in {course_name} for {semester}'
        msg["From"] = os.environ.get('EMAIL')
        msg["To"] = self.email

        context = ssl.create_default_context()
        with SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            try:
                server.login(os.environ.get('EMAIL'), os.environ.get('EMAIL_PASSWORD'))
            except SMTPAuthenticationError:
                logging.error('Error logging into email: invalid credentials')
                return

            try:
                server.send_message(msg)
                logging.info('Successfully sent email notification')
            except SMTPRecipientsRefused:
                logging.error('Error sending email')

class SMSAlert():
    def __init__(self, phone_number, data):
        self.phone_number = phone_number
        self.data = data

    def send_alert(self):
        course_name = self.data['course']
        semester = self.data['semester']
        grade = self.data['grade']
        msg = f'\nGrade: {grade}' if self.data['view_grade'] else \
            'You may view this grade by logging into Path@Penn (https://path.at.upenn.edu/student/landing) and selecting Review my unofficial transcript,' \
            'or by logging into Courses@Penn (https://courses.upenn.edu/) and selecting Degree Audit & Advising.'

        try:
            client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
            client.messages.create(
                body=f'A grade has been posted for you in the course {course_name} for the {semester} term. {msg}',
                from_=os.environ.get('TWILIO_NUMBER'),
                to=self.phone_number
            )
            logging.info('Successfully sent SMS notification')
        except TwilioRestException as exc:
            logging.error(f'Error sending SMS: {exc}')
