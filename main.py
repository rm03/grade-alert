import os
import time

from scraper import Scraper
from alert import EmailAlert, SMSAlert

def send_alerts(data, sem_code):
    for result in data:
        message_data = {
                'course' : f'{result["subj"]} {result["crse"]}',
                'semester' : f'{"Fall" if sem_code[4:] == "30" else "Spring"} {sem_code[:4]}',
                'grade': f'{result["grade"]}',
                'view_grade': os.environ.get('SEND_GRADE') == '1'
        }

        if os.environ.get('TWILIO_ACCOUNT_SID') is not None and os.environ.get('TWILIO_AUTH_TOKEN') is not None and os.environ.get('TWILIO_NUMBER') is not None:
            sms = SMSAlert(os.environ.get('ALERT_NUMBER'), message_data)
            sms.send_alert()

        if os.environ.get('EMAIL') is not None and os.environ.get('EMAIL_PASSWORD') is not None:
            email = EmailAlert(os.environ.get('ALERT_EMAIL'), message_data)
            email.send_alert()

def main():
    scraper = Scraper()
    scraper.refresh_auth()
    while True:
        data, sem = scraper.query_grades()
        if data is not None:
            send_alerts(data, sem)
        time.sleep(30)
    

if __name__ == "__main__":
    main()
