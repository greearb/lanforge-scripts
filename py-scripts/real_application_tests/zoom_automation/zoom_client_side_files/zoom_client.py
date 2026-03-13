import time
# import paramiko
import csv
import re
import sys
import pytz
from datetime import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import requests
import socket
import pyautogui


class ZoomClient:
    def __init__(self, server_ip=None):
        self.server_ip = server_ip
        self.base_url = f"http://{self.server_ip}:5000"
        self.new_login_url = None
        self.new_login_passwd = None
        self.meeting_link = None
        self.wait = None
        self.start_time = None
        self.end_time = None
        self.tz = pytz.timezone('Asia/Kolkata')
        self.hostname = socket.gethostname()
        self.path = "/home/lanforge/lanforge-scripts/py-scripts/zoom_automation/test_results/"
        self.audio = True
        self.video = True
        self.stop_signal = False

    def dynamic_wait(self, waittime):
        return WebDriverWait(self.driver, waittime)

    def setupdriver(self):
        chrome_options = Options()

        prefs = {
            "profile.managed_default_content_settings.notifications": 1,
            "profile.managed_default_content_settings.geolocation": 1,
            "profile.managed_default_content_settings.media_stream": 1
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
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 90)

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

    def start_zoom(self):
        self.setupdriver()

        self.get_meetin_link_and_password()
        self.zoom_login()
        # After starting Zoom, retrieve new_login_url and new_password
        self.get_stats_flags()
        time.sleep(5)
        while self.start_time is None or self.end_time is None:
            self.get_start_and_end_time()
            time.sleep(5)
        print("end_time and srtrt time is", self.start_time, self.end_time)
        while self.start_time > datetime.now(self.tz).isoformat():
            time.sleep(2)
            print("waiting for the start time")

        header = ["timestamp",
                  "Sent Audio Frequency (khz)", "Sent Audio Latency (ms)", "Sent Audio Jitter (ms)", "Sent Audio Packet loss (%)",
                  "Receive Audio Frequency (khz)", "Receive Audio Latency (ms)", "Receive Audio Jitter (ms)", "Receive Audio Packet loss (%)",
                  "Sent Video Latency (ms)", "Sent Video Jitter (ms)", "Sent Video Packet loss (%)", "Sent Video Resolution (khz)",
                  "Sent Video Frames ps (khz)", "Receive Video Latency (ms)", "Receive Video Jitter (ms)", "Receive Video Packet loss (%)",
                  "Receive Video Resolution (khz)", "Receive Video Frames ps (khz)"
                  ]
        with open(f'{self.hostname}.csv', 'w+', encoding='utf-8', errors='replace', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            while self.end_time > datetime.now(self.tz).isoformat():
                print("monitoring the test", "time remaining is")
                print(self.start_time, self.end_time)
                print()
                if self.check_stop_signal():
                    break
                stats = self.collecting_stats()
                csv_writer.writerow(stats)
                self.send_stats_to_api(self.audio_stats, self.video_stats)
                # time.sleep(5)
        print("test has been completed")
        # self.transfer_files(f"{self.hostname}.csv")
        self.stop_zoom()

    def stop_zoom(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".footer__leave-btn-container button")))
        self.driver.execute_script("document.querySelector('.footer__leave-btn-container button').click()")
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".leave-meeting-options__btn.leave-meeting-options__btn--default")))
        self.driver.execute_script("document.querySelector('.leave-meeting-options__btn.leave-meeting-options__btn--default').click()")
        time.sleep(1)
        self.driver.quit()

    def zoom_login(self):

        self.driver.get("https://app.zoom.us/wc/join")

        # print("checking self.meeting_link",self.meeting_link)

        # self.driver.get(str(self.meeting_link))
        # time.sleep(200)

        # self.wait.until(EC.presence_of_element_located(
        #     (By.CSS_SELECTOR, "#joinMeeting input.join-meetingId"))).send_keys(Keys.CONTROL + 'v')
        # time.sleep(200)
        # Assuming testInputValue is your meeting ID or the value you want to input
        # script = """
        # var joinMeetingInput = document.querySelector('#joinMeeting input.join-meetingId');
        # joinMeetingInput.click();
        # joinMeetingInput.value = arguments[0];
        # joinMeetingInput.dispatchEvent(new Event('change'));
        # joinMeetingInput.dispatchEvent(new Event('input'));
        # joinMeetingInput.dispatchEvent(new Event('blur'));

        # """
        formatted_login_url = self.new_login_url[:3] + ' ' + self.new_login_url[3:7] + ' ' + self.new_login_url[7:]

        meeting_id = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#joinMeeting input.join-meetingId")))
        meeting_id.click()
        if sys.platform.lower() == "linux":
            pyautogui.write(formatted_login_url)
        else:
            meeting_id.send_keys(formatted_login_url)

        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#joinMeeting ~ footer button.btn-join"))).click()
        # self.driver.execute_script("document.getElementById('joinMeeting ~ footer button.btn-join').click()")
        time.sleep(1)
        vel = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="webclient"]')))
        self.driver.switch_to.frame(vel)
        pass_element = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#input-for-pwd")))
        pass_element.click()
        if sys.platform.lower() == "linux":
            pyautogui.write(self.new_login_passwd)
        else:
            pass_element.send_keys(self.new_login_passwd)

        time.sleep(1)
        host_element = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#input-for-name")))
        host_element.click()
        host_element.send_keys(self.hostname)
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".preview-meeting-info button.preview-join-button"))).click()
        time.sleep(1)
        # self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        #                                              "#voip-tab button.join-audio-by-voip__join-btn")))
        # self.driver.execute_script("document.querySelector('#voip-tab button.join-audio-by-voip__join-btn').click()")
        # time.sleep(1)
        action = webdriver.ActionChains(self.driver)
        action.move_by_offset(10, 20).perform()
        time.sleep(1)
        audio_join_btn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                         ".footer-button-base__button.join-audio-container__btn")))
        self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")
        time.sleep(1)
        if audio_join_btn.text.lower() == "join audio":
            print("audio not joined")
            # self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")
            # self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            #                                          "#voip-tab button.join-audio-by-voip__join-btn")))
            # self.driver.execute_script("document.querySelector('#voip-tab button.join-audio-by-voip__join-btn').click()")
            # time.sleep(3)
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
            if el.text == "Audio Settings":
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

    def get_meetin_link_and_password(self):
        try:
            self.get_login_id()
            self.get_login_passwd()
            print("pasword and email fetched succesfuly for login")
        except Exception as e:
            print("error in gettig password and meeting id", e)

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
        return [freq if freq != "-" else "0", lat if lat != "-" else "0", jitt if jitt != "-" else "0", packet_loss_ if packet_loss_ != "-" else "0", freq_rec if freq_rec != "-" else "0",
                lat_rec if lat_rec != "-" else "0", jitt_rec if jitt_rec != "-" else "0", packet_rec_ if packet_rec_ != "-" else "0"]

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
        return [latency if latency != "-" else "0", jitter if jitter != "-" else "0", packet_loss_vi if packet_loss_vi != "-" else "0", resolution if resolution != "-" else "0",
                frames_per_second if frames_per_second != "-" else "0", latency_rec if latency_rec != "-" else "0", jitter_rec if jitter_rec != "-" else "0",
                packet_loss_vi_rec if packet_loss_vi_rec != "-" else "0", resolution_rec if resolution_rec != "-" else "0", frames_per_second_rec if frames_per_second_rec != "-" else "0"]

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
        self.time = self.get_formated_time(datetime.now(self.tz).isoformat())
        return [self.time] + self.audio_stats + self.video_stats

    def send_stats_to_api(self, audio_stats, video_stats):
        endpoint_url = f"{self.base_url}/upload_stats"
        data = {
            self.hostname: {
                "timestamp": self.time,
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

    def get_formated_time(self, timestamp_str):
        timestamp = datetime.fromisoformat(timestamp_str)
        date = timestamp.date()
        hour = timestamp.hour
        minute = timestamp.minute
        second = timestamp.second
        return f"{date} {hour}:{minute:02}:{second:02}"

    def get_login_id(self):
        endpoint_url = f"{self.base_url}/login_url"
        print(endpoint_url)
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                print("Remote login URL fetched successfully.")
                data = response.json()
                print(data, str(data))
                print(type(data))
                self.new_login_url = data.get('login_url')
                print("checking self.new_login_url", self.new_login_url)
            else:
                print(f"Failed to fetch remote login URL. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def get_login_passwd(self):
        endpoint_url = f"{self.base_url}/login_passwd"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                print("Remote login password fetched successfully.")
                data = response.json()
                self.new_login_passwd = data.get('login_passwd')
                print("checking self.new_login_passwd", self.new_login_passwd)
            else:
                print(f"Failed to fetch remote login password. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zoom Automation Script")
    parser.add_argument('--ip', required=True, help="Server endpoint ip")
    parser.add_argument('--env', action='extend', nargs='+', default=[])

    args = parser.parse_args()
    for argument in args.env:
        arg = argument.split("=")
        os.environ[arg[0]] = arg[1]
    print(os.environ)

    args = parser.parse_args()

    # Example usage:
    zoom_client = ZoomClient(server_ip=args.ip)  # Replace with your actual server IP
    zoom_client.start_zoom()