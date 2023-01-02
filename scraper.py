import logging
import logging.config
import os
import sys
import time
import json
import requests

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True
})

logging.basicConfig(
    format='[%(asctime)s] %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

def get_semester_code():
    month = int(time.strftime('%m'))
    year = int(time.strftime('%Y'))
    sem_year = year - 1 if month < 5 else year
    return f'{sem_year}10' if 5 <= month <= 11 else f'{sem_year}30'

class Scraper():
    def __init__(self):
        self.driver = None
        self.auth_token = None
        self.released = None

    def init_driver(self):
        profile = os.path.join(os.getcwd(), 'session')
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={profile}")

        self.driver = webdriver.Chrome(
            service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
            options=options
        )


    def login(self):
        self.driver.get('https://courses.upenn.edu')
        windows = self.driver.window_handles
        try:
            self.driver.execute_script('sam.auth.launch()')

            WebDriverWait(self.driver, 10).until(
                EC.new_window_is_opened(windows)
            )

            new_window_id = list(set(self.driver.window_handles) - set(windows))[0]
            self.driver.switch_to.window(new_window_id)

            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'pennname'))
            )

            password_field = self.driver.find_element(By.ID, 'password')
            username_field.send_keys(os.environ.get('PENNKEY'))
            password_field.send_keys(os.environ.get('PENNKEY_PASSWORD'))

            submit_btn = self.driver.find_element(By.NAME, '_eventId_proceed')
            submit_btn.click()


            if len(self.driver.window_handles) > 1:
                try:
                    self.driver.find_element(By.CLASS_NAME, 'form-error')
                    logging.error('Error logging into Penn account; check your credentials')
                    sys.exit()
                except NoSuchElementException:
                    pass

                trust_device_checkbox = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'trust-device-checkbox'))
                )
                if not trust_device_checkbox.is_selected():
                    trust_device_checkbox.click()

                logging.critical('Awaiting DUO authentication; please wait 5-10 seconds before authenticating')
                while len(self.driver.window_handles) > 1:
                    pass

            logging.info('Successfully authenticated!')
            home_window = self.driver.window_handles[0]
            self.driver.switch_to.window(home_window)

        except TimeoutException:
            logging.error('Error logging into Penn account')
            sys.exit()


    def set_auth(self):
        self.auth_token = self.driver.execute_script('return sam.auth.token')
        self.driver.close()


    def query_grades(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Host': 'courses.upenn.edu',
            'Origin': 'https://courses.upenn.edu',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Connection': 'keep-alive',
            'Referer': 'https://courses.upenn.edu/',
            'X-Requested-With': 'XMLHttpRequest',
        }

        params = {
            'page': 'sisproxy',
            'action': 'grades',
            'ts': str(int(time.time()))
        }

        data = {
            'authtoken': self.auth_token,
        }

        response = ''
        try:
            response = requests.post('https://courses.upenn.edu/api/',
                                    params=params,
                                    headers=headers,
                                    data=data).text
        except requests.Timeout:
            logging.error('Request timed out')
        except requests.ConnectionError:
            logging.error('Error connecting to Courses@Penn API')
        else:
            grades = json.loads(response[10:len(response) - 1])
            if 'error' in grades:
                logging.info('Session timed out, refreshing...')
                self.refresh_auth()
                return self.query_grades()
            
            curr_grades = grades['grades'][get_semester_code()]
            curr_released = {course['title'] for course in curr_grades}

            if self.released and self.released != curr_released:
                new_courses = curr_released - self.released
                logging.info(f'{new_courses} just released grades')
                self.released = curr_released
                return [course for course in curr_grades if course['title'] in new_courses], get_semester_code()

            self.released = curr_released
            logging.info(f'Courses with grades released: {self.released}')
        
        return None, None


    def refresh_auth(self):
        self.init_driver()
        self.login()
        self.set_auth()


    def set_auth_token(self, token):
        self.auth_token = token
