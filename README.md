# grade-alert
A script that notifies Penn students via email and/or SMS when their final grades are posted on Path@Penn. 
Unfortunately, the new Path@Penn system no longer informs students when professors post their final grade (RIP PennInTouch 😔), leaving many constantly refreshing their transcripts over break. 

## Setup

Clone this repo and run `pip install -r requirements.txt & mkdir session` to install the dependencies. Google Chrome must also be installed on your machine.

You will also need to set the following environment variables:
```
WDM_LOG=logging.NOTSET
WDM_LOCAL=1
PENNKEY
PENNKEY_PASSWORD
SEND_GRADE
```
`SEND_GRADE` should be 1 if you want your final grade to be sent with the notification, and 0 otherwise.

The following environment variables should be set if you want to receive an SMS and/or email notification, respectively:
```
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_NUMBER
ALERT_NUMBER

EMAIL
EMAIL_PASSWORD
ALERT_EMAIL
```
SMS notifications are sent via Twilio; you can sign up for a free trial [here](https://www.twilio.com/try-twilio). Your account SID, auth token, and Twilio phone number can be found on the console.

Email notifications are sent from your Gmail account. However, instead of using your actual password, you will need to generate and use an [App Password](https://support.google.com/accounts/answer/185833?hl=en).

The `ALERT_EMAIL` and `ALERT_NUMBER` should be the email and phone number at which you want to receive the notification, respectively.

## Usage

To launch the script, run `python main.py`. 
After a few seconds, you will receive an authentication request via DUO Mobile. **Please wait 5 to 10 seconds before approving the request**. The script should run normally afterwards.

## Deployment

If you want to avoid most of the setup and have the script run remotely, consider deploying it on Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rm03/grade-alert)

Although deploying on Heroku is no longer free, students enrolled in the [GitHub Student Developer Pack](https://education.github.com/pack) (free) can get $13 USD of credit per month for 12 months [here](https://www.heroku.com/github-students/signup). 
