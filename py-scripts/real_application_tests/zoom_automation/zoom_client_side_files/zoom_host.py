import time
import csv
import sys
import re
import pytz
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import requests
import socket
import argparse
import json
import pickle

class ZoomHost:
    def __init__(self, server_ip=None):
        self.server_ip = server_ip
        self.base_url = f"http://{self.server_ip}:5000"
        # self.base_url = "http://10.253.8.108:5000"
        self.new_login_url = None
        self.new_login_passwd = None
        self.login_email = None
        self.login_passwd = None
        self.meeting_link = None
        self.wait = None
        self.participants = None
        self.participants_required = None
        self.start_time = None
        self.end_time = None
        self.tz = pytz.timezone('Asia/Kolkata')
        self.hostname = socket.gethostname()
        self.path = "/home/lanforge/lanforge-scripts/py-scripts/zoom_automation/test_results/"
        self.audio = True
        self.video = True
        self.stop_signal = False

    def setupdriver(self):
        chrome_options = Options()

        prefs = {
            "profile.managed_default_content_settings.notifications": 1,
            "profile.managed_default_content_settings.geolocation": 1,
            "profile.managed_default_content_settings.media_stream": 1,
            "download.default_directory": os.getcwd(),  # Change default directory
            "download.prompt_for_download": False,  # Disable download prompt
            "download.directory_upgrade": True
        }

        # Performance-related options
        chrome_options.add_argument("--process-per-site")
        chrome_options.add_argument("--renderer-process-limit=4")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--enable-low-res-tiling")
        chrome_options.add_argument("--force-gpu-mem-available-mb=4096")
        chrome_options.add_argument("--memory-pressure-thresholds-mb=2048")
        # chrome_options.add_argument("--enable-quic")

        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--auto-select-desktop-capture-source=Entire screen")

        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 90)
    

    def share_screen(self):
        print("sharing screen now")
        try:
            # Wait for the Zoom share button to be present in the DOM
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".footer-button-base__button.sharing-entry-button-container")))
            
            # Click the Zoom share button
            self.driver.execute_script("document.querySelector('.footer-button-base__button.sharing-entry-button-container').click()")
            print("[INFO] Share Screen clicked in Zoom UI.")
            
            # Give the WebRTC connection a moment to establish
            time.sleep(2) 
            
            print("[INFO] Entire Screen shared successfully via Chrome flags")

            # We use a short wait here because if it's not there, we don't want to wait 90 seconds
            pause_audio_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Pause Audio Share']"))
            )
            
            # Click it to pause the audio sharing
            self.driver.execute_script("arguments[0].click();", pause_audio_btn)
            print("[INFO] Screen share audio has been muted/paused.")
            
        except Exception as e:
            print(f"Error in sharing screen: {e}")

    def saveCookies(self):
        # Save cookies to a file
        cookies = self.driver.get_cookies()
        with open('cookies.pkl', 'wb') as file:
            pickle.dump(cookies, file)
        print("Cookies saved.")

    def loadCookies(self):
        # Load cookies from a file
        try:
            with open('cookies.pkl', 'rb') as file:
                if os.path.getsize('cookies.pkl') > 0:  # Ensure the file is not empty
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                    print("Cookies loaded.")
                else:
                    print("Cookies file is empty. Proceeding with new login.")
        except FileNotFoundError:
            print("No cookies file found. Proceeding with new login.")
        except EOFError:
            print("Cookies file is corrupted or empty. Proceeding with new login.")

    def dynamic_wait(self, waittime):
        return WebDriverWait(self.driver, waittime)

    def start_zoom(self):
        self.setupdriver()
        self.participants_required = self.get_required_participants()
        self.zoom_login()
        # After starting Zoom, retrieve new_login_url and new_password
        self.update_login_completed()
        time.sleep(1)
    

    def keep_footer_visible(self):
        print("[INFO] Disabling Zoom's auto-hide footer...")
        try:
            # Injects a background script that fires a fake mouse movement every 2 seconds
            js_script = """
                if (!window.keepZoomActiveInterval) {
                    window.keepZoomActiveInterval = setInterval(() => {
                        document.dispatchEvent(new MouseEvent('mousemove', {
                            bubbles: true,
                            cancelable: true,
                            clientX: 100,
                            clientY: 100
                        }));
                    }, 2000);
                }
            """
            self.driver.execute_script(js_script)
            print("[INFO] Footer is now locked to visible.")
        except Exception as e:
            print(f"[ERROR] Failed to lock footer visibility: {e}")

    def zoom_login(self):
        print("getting host email and password")
        self.login_email = self.get_host_email()
        self.login_passwd = self.get_host_password()
        self.login_email = self.login_email.strip()
        self.login_passwd = self.login_passwd.strip()

        print(self.login_email)
        print(self.login_passwd)

        # Create a dictionary with the login details
        login_data = {
            "login_email": self.login_email,
            "login_passwd": self.login_passwd
        }

        # Variable to store whether the credentials match
        credentials_match = False

        # Path to the JSON file
        file_path = "login_data.json"

        # Check if the file exists
        if os.path.exists(file_path):
            # Read the existing JSON data
            with open(file_path, "r") as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = {}

            # Compare the existing data with the new login data
            if existing_data == login_data:
                credentials_match = True
        else:
            # If the file doesn't exist, treat it as new data
            existing_data = {}

        if not credentials_match:
            with open(file_path, "w") as json_file:
                json.dump(login_data, json_file, indent=4)
                credentials_match = False

        self.driver.get('https://app.zoom.us/wc')
        if (credentials_match):

            self.loadCookies()
            self.driver.refresh()
        try:
            element = self.dynamic_wait(5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn-index-signin"))
            )
            element.click()
            print("clicked sign in button")
        except Exception:
            print("Loaded session through cookies")

        if 'signin' in self.driver.current_url:
            print(self.login_email)
            print(self.login_passwd)

            # if sys.platform.lower()=="linux":
            #     email_field=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#email")))
            #     for char in self.login_email:
            #         email_field.send_keys(char)
            #     pass_field=self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#password")))
            #     for char in self.login_passwd:
            #         pass_field.send_keys(char)

            # pyautogui.write(self.login_email)
            # time.sleep(2)
            # # password_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#password")))
            # self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#password"))).click()

            # #self.driver.execute_script("arguments[0].click();", password_field)
            # pyautogui.write(self.login_passwd)

            # else:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#email"))).send_keys(self.login_email)
            time.sleep(1)
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#signin_btn_next > span"))).click()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#password"))).send_keys(self.login_passwd)
            time.sleep(5)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button#js_btn_login"))).click()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.main__action-btn")))
            time.sleep(5)
            self.saveCookies()

        else:
            print("previous session loaded")

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.main__action-btn"))).click()

        try:

            iframe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "webclient")))
            self.driver.switch_to.frame(iframe)

            try:
                element = self.dynamic_wait(5).until(
                    EC.presence_of_element_located((By.ID, 'btn_end_meeting'))

                )
                element.click()

                print("User was already in the meeting.")
            except Exception:
                print("new user login")

            self.driver.switch_to.default_content()
            print("Clicked the element inside the iframe.")
        except Exception as e:
            print(f"Error clicking the element inside the iframe: {str(e)}")

        time.sleep(2)
        print("after 2 sec sleep")
        vel = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="webclient"]')))
        self.driver.switch_to.frame(vel)
        print("after 2 switching to iframe")
        time.sleep(2)
        print("after 2 sec sleep")
        action = webdriver.ActionChains(self.driver)

        action.move_by_offset(10, 20).perform()
        self.meeting_link = self.driver.current_url
        action.move_by_offset(10, 20).perform()
        time.sleep(1)
        self.keep_footer_visible()
        try:
            time.sleep(3)
            self.share_screen()
        except Exception as e:
            print("error in sharing screen", e)

        audio_join_btn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                         ".footer-button-base__button.join-audio-container__btn")))

        self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")
        time.sleep(1)
        if audio_join_btn.text.lower() == "join audio":
            print("audio not joined")
            self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")

        elif audio_join_btn.text.lower() == "unmute":
            print("it is muted")
            self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")

        elif audio_join_btn.text.lower() == "mute":
            print("already unmuted")
        self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                        "//*[@id='audioOptionMenu']")))
        self.driver.execute_script("document.querySelector('#audioOptionMenu button').click()")
        time.sleep(2)

        setting_options = self.driver.find_elements(By.CSS_SELECTOR, "#audioOptionMenu a")
        for el in setting_options:
            print(el.text)
            if el.text == "Audio Settings":
                print(el.text)
                el.click()
                break
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#video")))
        self.driver.execute_script("document.querySelector('#video').click()")
        time.sleep(1)
        video_join_btn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                         ".footer-button-base__button.send-video-container__btn")))

        self.driver.execute_script("document.querySelector('button.footer-button-base__button.send-video-container__btn').click()")
        if video_join_btn.text.lower() == "join video" or video_join_btn.text.lower() == "start video":
            print("video not joined")
            self.driver.execute_script("document.querySelector('button.footer-button-base__button.send-video-container__btn').click()")

        elif video_join_btn.text.lower() == "stop video":
            print("already video on")


        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#stats")))
        self.driver.execute_script("document.querySelector('#stats').click()")
        time.sleep(1)
        self.send_meetin_link_and_password()

    def send_meet_link(self):
        # Call Flask endpoint to send meeting link
        endpoint_url = f"{self.base_url}/meeting_link"
        data = {"meet_link": self.android_meet_link}

        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                print("Meeting link sent successfully.")
            else:
                print(f"Failed to send meeting link. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def wait_for_exit(self):
        print("waiting for clients to disconnect")
        tries = 0
        print(self.monitor_client_count(), "participent count", self.monitor_client_count() > 1)
        print("sdfsdfgvsdvgsdvsd")
        print(self.monitor_client_count() > 1)
        while self.monitor_client_count() > 1:
            print(self.monitor_client_count(), "participent count")
            time.sleep(2)
            tries += 1
            if tries > 20:
                print("max tries reach for client disconnection wait")
                break
        print(self.monitor_client_count(), self.monitor_client_count() > 1)

    # To download the csv
    def download_csv(self):
        # redirecting to dashboard
        print("meeting link is", self.new_login_url)
        self.driver.get("https://www.zoom.us/account/metrics/dashboard/home/#/pastMeetings")

        # get meeting id formated
        cleaned_id = self.new_login_url[:3] + " " + self.new_login_url[3:7] + " " + self.new_login_url[7:]
        print(self.new_login_url, "cleaned id idcscdsc", cleaned_id)
        # XPath to find the <a> link associated with the meeting ID

        xpath = f"//p[contains(@class, 'ellipsis') and contains(text(), '{cleaned_id}')]"

        # element containing id and link to meeting dashboard
        current_elem = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        print("current outer", current_elem.get_attribute("outerHTML"))
        print("current text", current_elem.text)
        parent = current_elem.find_element(By.XPATH, "..")
        try:
            anchor = parent.find_element(By.TAG_NAME, "a")
        except BaseException:
            print("coudlnt find anchro tag refreshing in 15 seconds..")
            time.sleep(15)
            try:
                self.driver.refresh()
                current_elem = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                parent = current_elem.find_element(By.XPATH, "..")
                anchor = parent.find_element(By.TAG_NAME, "a")
            except BaseException:
                print("still link soes not appear...on last refresh")
                time.sleep(60)
                self.driver.refresh()
                current_elem = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                parent = current_elem.find_element(By.XPATH, "..")
        print("parent outer", parent.get_attribute("outerHTML"))
        anchor = parent.find_element(By.TAG_NAME, "a")
        print(anchor.get_attribute("href"))

        # redirecting to meeting dashboard
        self.driver.get(anchor.get_attribute("href"))

        # path for export button
        export_xpath = "//div[contains(@class, 'detail-operation') and contains(@class, 'detial-operation')]//button[.//span[contains(translate(., 'EXPORT', 'export'), 'export')]]"
        export_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, export_xpath)))
        export_btn.click()
        print("Clicked Export button.")
        try:
            # Wait for modal and click "Go to Downloads Page"
            modal_btn = self.dynamic_wait(25).until(EC.element_to_be_clickable((
                By.XPATH, "//button[.//span[contains(text(), 'Go to Downloads Page')]]"
            )))
            modal_btn.click()
            print("Clicked 'Go to Downloads Page'.")
        except BaseException:
            # did not get the download popup refresh here"
            self.driver.refresh()
            export_xpath = "//div[contains(@class, 'detail-operation') and contains(@class, 'detial-operation')]//button[.//span[contains(translate(., 'EXPORT', 'export'), 'export')]]"
            export_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, export_xpath)))
            export_btn.click()
            print("Clicked Export button.")
            modal_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[.//span[contains(text(), 'Go to Downloads Page')]]"
            )))
            modal_btn.click()
            print("Clicked 'Go to Downloads Page'.")

        # Wait for download to start
        print("Waiting for download to complete...")
        time.sleep(15)
        all_handles = self.driver.window_handles
        self.driver.switch_to.window(all_handles[-1])
        # refreshing to get the updated tables
        self.driver.refresh()
        filename = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table#download_queue_list tbody tr:nth-of-type(1) td.col1"))).text
        print(f"download file is {filename}")
        button__dd = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table#download_queue_list tbody tr:nth-of-type(1) button")
        ))
        self.driver.execute_script("arguments[0].click();", button__dd)
        print("Clicked 'Download' button")
        self.wait_for_download(filename, download_dir=os.getcwd(), timeout=45)

    def wait_for_download(self, dlname, download_dir, timeout=60):
        seconds = 0
        dl_wait = True
        final_file_path = None
        print(dlname, download_dir, timeout, "<====directories")
        while dl_wait and seconds < timeout:
            time.sleep(1)
            dl_wait = False
            for fname in os.listdir(download_dir):
                if fname.startswith(dlname):
                    if fname.endswith('.crdownload'):
                        dl_wait = True  # still downloading
                    else:
                        final_file_path = os.path.join(download_dir, fname)
            seconds += 1

        if final_file_path and os.path.isfile(final_file_path):
            print(f"File downloaded: {final_file_path}")
            try:
                with open(final_file_path, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    endpoint_url = f"{self.base_url}/upload_csv"
                    print(endpoint_url)

                    dd = {
                        "filename": os.path.basename(final_file_path),
                        "rows": rows
                    }
                    print(dd)
                    requests.post(endpoint_url, json={
                        "filename": os.path.basename(final_file_path),
                        "rows": rows
                    })
            except Exception as e:
                print("Error reading file:", e)
        else:
            print("File was not downloaded in time or not found.")

    def stop_zoom(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".footer__leave-btn-container button")))
        self.driver.execute_script("document.querySelector('.footer__leave-btn-container button').click()")
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".leave-meeting-options__btn.leave-meeting-options__btn--default")))
        self.driver.execute_script("document.querySelector('.leave-meeting-options__btn.leave-meeting-options__btn--default').click()")
        print("waiting for some time to let the dashboard have past meeting")
        download_csv = self.get_download_csv_flag()
        if download_csv:
            time.sleep(100)
            self.download_csv()
        self.driver.quit()

    def monitor_client_count(self):
        no_of_participants = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".footer-button__number-counter"))).text
        return int(no_of_participants)

    def set_start_test(self, flag=False):
        try:
            self.participants = self.monitor_client_count()
            self.set_participants()
            print(self.participants_required, self.participants)
            if self.participants_required == self.participants:
                self.update_start_test()

            elif flag:
                self.update_start_test()

        except Exception as e:
            print("error in seting start test", e)

    def get_download_csv_flag(self):
        try:
            endpoint_url = f'{self.base_url}/download_csv'

            response = requests.get(endpoint_url)
            if response.status_code == 200:

                download_csv_flag = response.json().get('download_csv', False)
                return download_csv_flag

            return False
        except Exception as e:
            print(f"Error checking stop signal: {e}")
            return False

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f'{self.base_url}/check_stop'

            response = requests.get(endpoint_url)  # Replace with your Flask server URL
            if response.status_code == 200:

                stop_signal_from_server = response.json().get('stop', False)

                # Only update if the server's stop signal is True
                if stop_signal_from_server:
                    self.stop_signal = True
                    print("Stop signal received from the server. Exiting the loop.")
                else:

                    print("No stop signal received from the server. Continuing.")
            return self.stop_signal
        except Exception as e:
            print(f"Error checking stop signal: {e}")

    def send_meetin_link_and_password(self):

        # pattern = r'https://\S+?\.zoom\.us/(?:j|wc)/(?P<meeting_id>\d+)(?:\S*?pwd=(?P<password>[^\s&]+))?'

        pattern = r'https://\S+?\.zoom\.us/(?:j|wc)/(?P<meeting_id>\d+)\S*?pwd=(?P<password>[^\s&]+)'

        match = re.search(pattern, self.meeting_link)
        if match:
            self.new_login_url = match.group('meeting_id')
            self.new_login_passwd = match.group('password')
            print("password and meeting id:", self.new_login_url, self.new_login_passwd)
            if self.new_login_url:
                self.update_login_email(self.new_login_url)
            if self.new_login_passwd:
                self.update_login_passwd(self.new_login_passwd)
            print("pasword and email updated succesfuly for login")

    def capture_audio_stats(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                        "//*[@id='Audio']"))).click()
        time.sleep(2)
        freq = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                               "//*[@id='Audio-tab']/div/table/tbody/tr[1]/td[2]"))).text
        freq = freq.replace(" khz", "")
        freq_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                   "//*[@id='Audio-tab']/div/table/tbody/tr[1]/td[3]"))).text
        freq_rec = freq_rec.replace(" khz", "")
        lat = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                              "//*[@id='Audio-tab']/div/table/tbody/tr[2]/td[2]"))).text
        lat = lat.replace(" ms", "")
        lat_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                  "//*[@id='Audio-tab']/div/table/tbody/tr[2]/td[3]"))).text
        lat_rec = lat_rec.replace(" ms", "")
        jitt = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                               "//*[@id='Audio-tab']/div/table/tbody/tr[3]/td[2]"))).text
        jitt = jitt.replace(" ms", "")
        jitt_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                   "//*[@id='Audio-tab']/div/table/tbody/tr[3]/td[3]"))).text
        jitt_rec = jitt_rec.replace(" ms", "")
        pack = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                               "//*[@id='Audio-tab']/div/table/tbody/tr[4]/td[2]"))).text
        packet_loss = re.sub(r'\s*\(.*?\)', '', pack)
        packet_loss_ = packet_loss.replace('%', '')
        pack_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                   "//*[@id='Audio-tab']/div/table/tbody/tr[4]/td[2]"))).text
        packet_rec = re.sub(r'\s*\(.*?\)', '', pack_rec)
        packet_rec_ = packet_rec.replace('%', '')
        return [freq if freq != "-" else "0", lat if lat != "-" else "0", jitt if jitt != "-" else "0", packet_loss_ if packet_loss_ != "-" else "0",
                freq_rec if freq_rec != "-" else "0", lat_rec if lat_rec != "-" else "0",
                jitt_rec if jitt_rec != "-" else "0", packet_rec_ if packet_rec_ != "-" else "0"]

    def capture_video_stats(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='Video']"))).click()
        time.sleep(2)
        latency = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                  "//*[@id='Video-tab']/div/table/tbody/tr[1]/td[2]"))).text
        latency = latency.replace(" ms", "")
        latency_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                      "//*[@id='Video-tab']/div/table/tbody/tr[1]/td[3]"))).text
        latency_rec = latency_rec.replace(" ms", "")
        jitter = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                 "//*[@id='Video-tab']/div/table/tbody/tr[2]/td[2]"))).text
        jitter = jitter.replace(" ms", "")
        jitter_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                     "//*[@id='Video-tab']/div/table/tbody/tr[2]/td[3]"))).text
        jitter_rec = jitter_rec.replace(" ms", "")
        packet_loss = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                      "//*[@id='Video-tab']/div/table/tbody/tr[3]/td[2]"))).text
        packet_loss_vi = re.sub(r'\s*\(.*?\)', '', packet_loss)
        packet_loss_vi = packet_loss_vi.replace('%', '')
        packet_loss_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                          "//*[@id='Video-tab']/div/table/tbody/tr[3]/td[3]"))).text
        packet_loss_vi_rec = re.sub(r'\s*\(.*?\)', '', packet_loss_rec)
        packet_loss_vi_rec = packet_loss_vi_rec.replace('%', '')
        resolution = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                     "//*[@id='Video-tab']/div/table/tbody/tr[4]/td[2]"))).text
        resolution_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                         "//*[@id='Video-tab']/div/table/tbody/tr[4]/td[3]"))).text
        frames_per_second = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                            "//*[@id='Video-tab']/div/table/tbody/tr[5]/td[2]"))).text
        frames_per_second = frames_per_second.replace(" fps", "")
        frames_per_second_rec = self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                                "//*[@id='Video-tab']/div/table/tbody/tr[5]/td[3]"))).text
        frames_per_second_rec = frames_per_second_rec.replace(" fps", "")
        return [latency if latency != "-" else "0", jitter if jitter != "-" else "0", packet_loss_vi if packet_loss_vi != "-" else "0",
                resolution if resolution != "-" else "0", frames_per_second if frames_per_second != "-" else "0", latency_rec if latency_rec != "-" else "0",
                jitter_rec if jitter_rec != "-" else "0", packet_loss_vi_rec if packet_loss_vi_rec != "-" else "0", resolution_rec if resolution_rec != "-" else "0",
                frames_per_second_rec if frames_per_second_rec != "-" else "0"]

    def get_host_email(self):
        # Call Flask endpoint to get new_login_url
        endpoint_url = f"{self.base_url}/get_host_email"
        print(endpoint_url, "sdfsdf")
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                return response.json().get("host_email", None)
            else:
                print(f"Failed to fetch new login URL. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")
        return None

    def get_host_password(self):
        # Call Flask endpoint to get new_password
        endpoint_url = f"{self.base_url}/get_host_passwd"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                return response.json().get("host_passwd", None)
            else:
                print(f"Failed to fetch new password. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")
        return None

    def update_login_email(self, new_login_url):
        endpoint_url = f"{self.base_url}/login_url"
        data = {"login_url": new_login_url}

        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                print("Remote login URL updated successfully.")
            else:
                print(f"Failed to update remote login URL. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def update_login_passwd(self, new_login_passwd):
        endpoint_url = f"{self.base_url}/login_passwd"
        data = {"login_passwd": new_login_passwd}

        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                print("Remote login password updated successfully.")
            else:
                print(f"Failed to update remote login password. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def update_login_completed(self):
        endpoint_url = f"{self.base_url}/login_completed"

        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                print("Login completed status updated successfully.")
            else:
                print(f"Failed to update login completed status. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def update_start_test(self):

        endpoint_url = f"{self.base_url}/test_started"
        data = {"test_started": True}
        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                print("test started status updated successfully.")
            else:
                print(f"Failed to update test started status. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def set_participants(self):
        endpoint_url = f"{self.base_url}/set_participants_joined"
        data = {"participants_joined": self.participants}
        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                print("test participents joned updated successfully.")
            else:
                print(f"Failed to update particiupants status. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def get_required_participants(self):
        endpoint_url = f"{self.base_url}/get_participants_req"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                return response.json().get("participants", None)
            else:
                print(f"Failed to fetch required participants. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None
        return None

    def get_start_and_end_time(self):
        endpoint_url = f"{self.base_url}/get_start_end_time"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                data = response.json()
                self.start_time = data.get("start_time")
                self.end_time = data.get("end_time")
            else:
                print(f"Failed to fetch new login URL. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")
        return None

    def send_client_disconnection(self):
        endpoint_url = f"{self.base_url}/clients_disconnected"
        data = {"clients_disconnected": True}
        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                print("test participents disconnection updated successfully.")
            else:
                print(f"Failed to update particiupants disconnection. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def read_credentials(self):
        # Read credentials.txt in the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_file = os.path.join(current_dir, "credentials.txt")

        try:
            with open(credentials_file, 'r') as file:
                lines = file.readlines()
                if lines:
                    self.server_ip = lines[0].strip().split("=")[1]
                    self.base_url = f"http://{self.server_ip}"
                    print(f"Server IP set to {self.server_ip}")
                else:
                    print("Error: credentials.txt is empty.")
        except IOError:
            print(f"Error: Unable to read {credentials_file}")

    def get_stats_flags(self):
        endpoint_url = f"{self.base_url}/stats_opt"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                data = response.json()
                self.audio = data.get("audio_stats")
                self.video = data.get("video_stats")
            else:
                print(f"Failed to fetch stats flag. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")
        return None

    def collecting_stats(self):
        if self.audio:
            self.audio_stats = self.capture_audio_stats()
        else:
            self.audio_stats = ["0", "0", "0", "0", "0", "0", "0", "0"]
        if self.video:
            self.video_stats = self.capture_video_stats()
        else:
            self.video_stats = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
        return [self.get_formated_time(datetime.now(self.tz).isoformat())] + self.audio_stats + self.video_stats

    def get_formated_time(self, timestamp_str):
        timestamp = datetime.fromisoformat(timestamp_str)
        date = timestamp.date()
        hour = timestamp.hour
        minute = timestamp.minute
        second = timestamp.second
        return f"{date} {hour}:{minute:02}:{second:02}"

    def send_stats_to_api(self, audio_stats, video_stats):
        endpoint_url = f"{self.base_url}/upload_stats"
        data = {
            self.hostname: {
                "timestamp": self.get_formated_time(datetime.now(self.tz).isoformat()),
                "audio_stats": {
                    "frequency_sent": audio_stats[0],
                    "latency_sent": audio_stats[1],
                    "jitter_sent": audio_stats[2],
                    "packet_loss_sent": audio_stats[3],
                    "frequency_received": audio_stats[4],
                    "latency_received": audio_stats[5],
                    "jitter_received": audio_stats[6],
                    "packet_loss_received": audio_stats[7],
                },
                "video_stats": {
                    "latency_sent": video_stats[0],
                    "jitter_sent": video_stats[1],
                    "packet_loss_sent": video_stats[2],
                    "resolution_sent": video_stats[3],
                    "frames_per_second_sent": video_stats[4],
                    "latency_received": video_stats[5],
                    "jitter_received": video_stats[6],
                    "packet_loss_received": video_stats[7],
                    "resolution_received": video_stats[8],
                    "frames_per_second_received": video_stats[9],
                }
            }
        }

        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                print("Stats sent successfully.")
            else:
                print(f"Failed to send stats. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")


if __name__ == "__main__":
    zoom_host = ZoomHost()  # Replace with your actual server IP
    parser = argparse.ArgumentParser(description="Zoom Automation Script")
    parser.add_argument('--ip', required=True, help="Server endpoint ip")
    parser.add_argument('--env', action='extend', nargs='+', default=[])

    args = parser.parse_args()
    for argument in args.env:
        arg = argument.split("=")
        os.environ[arg[0]] = arg[1]
    print(os.environ)

    zoom_host = ZoomHost(server_ip=args.ip)  # Replace with your actual server IP

    # zoom_host.read_credentials()
    zoom_host.start_zoom()
    wait_limit = datetime.now() + timedelta(seconds=120)
    zoom_host.get_stats_flags()
    while True:
        zoom_host.set_start_test()
        if zoom_host.participants_required is not None and zoom_host.participants_required == zoom_host.participants:
            print(zoom_host.participants_required,)
            print("required participants are connected", zoom_host.participants)
            break
        elif datetime.now() > wait_limit:
            print("wait limit is reached. Starting the test with available clients", zoom_host.participants_required, zoom_host.participants)
            zoom_host.set_start_test(flag=True)
            break
        time.sleep(5)
    while zoom_host.start_time is None or zoom_host.end_time is None:
        zoom_host.get_start_and_end_time()
        time.sleep(5)
    print("end_time and srtrt time is", zoom_host.start_time, zoom_host.end_time)
    while zoom_host.start_time > datetime.now(zoom_host.tz).isoformat():
        time.sleep(2)
        print("waiting for the start time")
    header = ["timestamp",
              "Sent Audio Frequency (khz)", "Sent Audio Latency (ms)", "Sent Audio Jitter (ms)", "Sent Audio Packet loss (%)",
              "Receive Audio Frequency (khz)", "Receive Audio Latency (ms)", "Receive Audio Jitter (ms)", "Receive Audio Packet loss (%)",
              "Sent Video Latency (ms)", "Sent Video Jitter (ms)", "Sent Video Packet loss (%)", "Sent Video Resolution (khz)",
              "Sent Video Frames ps (khz)", "Receive Video Latency (ms)", "Receive Video Jitter (ms)", "Receive Video Packet loss (%)",
              "Receive Video Resolution (khz)", "Receive Video Frames ps (khz)"
              ]

    with open(f'{zoom_host.hostname}.csv', 'w+', encoding='utf-8', errors='replace', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(header)
        while zoom_host.end_time > datetime.now(zoom_host.tz).isoformat():
            print("monitoring the test")
            print(header)
            print(len(header))
            if zoom_host.check_stop_signal():
                break
            stats = zoom_host.collecting_stats()
            csv_writer.writerow(stats)
            zoom_host.send_stats_to_api(zoom_host.audio_stats, zoom_host.video_stats)
            # time.sleep(5)
    print("test has been completed")
    zoom_host.wait_for_exit()
    zoom_host.stop_zoom()
    zoom_host.send_client_disconnection()