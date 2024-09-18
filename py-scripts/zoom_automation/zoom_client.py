import time
import paramiko
import csv
import re
import sys
import pyperclip
import pytz
from datetime import datetime,timedelta
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import requests
import socket

class ZoomClient:
    def __init__(self):
        self.server_ip = None
        self.base_url = f"http://{self.server_ip}"
        self.new_login_url = None
        self.new_login_passwd = None
        self.meeting_link = None
        self.wait = None
        self.start_time = None
        self.end_time = None
        self.tz=pytz.timezone('Asia/Kolkata')
        self.hostname = socket.gethostname()
        self.path = "/home/lanforge/lanforge-scripts/py-scripts/zoom_automation/test_results/"
        self.audio = True
        self.video = True

    def dynamic_wait(self,waittime):
        return WebDriverWait(self.driver, waittime)
    
    def setupdriver(self):
        chrome_options = Options()
        
        prefs = {
            "profile.managed_default_content_settings.notifications": 1,
            "profile.managed_default_content_settings.geolocation": 1,
            "profile.managed_default_content_settings.media_stream": 1
        }
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 90)


    def start_zoom(self):
        self.setupdriver()
        self.read_credentials()
        self.get_meetin_link_and_password()
        self.zoom_login()
        # After starting Zoom, retrieve new_login_url and new_password
        self.get_stats_flags()
        time.sleep(5)
        while self.start_time is None or self.end_time is None:
            self.get_start_and_end_time()
            time.sleep(5)
        print("end_time and srtrt time is", self.start_time,self.end_time)
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
        with open(f'{self.hostname}.csv', 'w+',encoding='utf-8', errors='replace', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header) 
            while self.end_time > datetime.now(self.tz).isoformat():
                print("monitoring the test","time remaining is")
                print(self.start_time,self.end_time)
                print()
                stats = self.collecting_stats()
                csv_writer.writerow(stats)
                time.sleep(5)
        print("test has been completed")
        self.transfer_files(f"{self.hostname}.csv")
        self.stop_zoom()


    def stop_zoom(self):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,".footer__leave-btn-container button")))
        self.driver.execute_script("document.querySelector('.footer__leave-btn-container button').click()")
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,".leave-meeting-options__btn.leave-meeting-options__btn--default")))
        self.driver.execute_script("document.querySelector('.leave-meeting-options__btn.leave-meeting-options__btn--default').click()")
        time.sleep(1)
        self.driver.quit()

    def zoom_login(self):
        self.driver.get("https://app.zoom.us/wc/join")
        
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#joinMeeting input.join-meetingId"))).send_keys(self.new_login_url)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#joinMeeting ~ footer button.btn-join"))).click()
        time.sleep(1)
        vel = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="webclient"]')))
        self.driver.switch_to.frame(vel)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#input-for-pwd"))).send_keys(self.new_login_passwd)
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#input-for-name"))).send_keys(self.hostname)
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".preview-meeting-info button.preview-join-button"))).click()
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                     "#voip-tab button.join-audio-by-voip__join-btn")))
        self.driver.execute_script("document.querySelector('#voip-tab button.join-audio-by-voip__join-btn').click()")
        time.sleep(1)
        action = webdriver.ActionChains(self.driver)
        action.move_by_offset(10, 20).perform()
        time.sleep(1)
        audio_join_btn = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                     ".footer-button-base__button.join-audio-container__btn")))
        self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")
        time.sleep(1)
        if audio_join_btn.text == "Join Audio":
            print("audio not joined")
            self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                     "#voip-tab button.join-audio-by-voip__join-btn")))
            self.driver.execute_script("document.querySelector('#voip-tab button.join-audio-by-voip__join-btn').click()")
            time.sleep(3)
            self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")

        elif audio_join_btn.text == "Unmute":
            print("it is muted")
            self.driver.execute_script("document.querySelector('button.footer-button-base__button.join-audio-container__btn').click()")
            
        elif audio_join_btn.text == "Mute":
            print("already unmuted")
        self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                     "//*[@id='audioOptionMenu']")))
        self.driver.execute_script("document.querySelector('#audioOptionMenu button').click()")
        time.sleep(2)
        
        setting_options = self.driver.find_elements(By.CSS_SELECTOR,"#audioOptionMenu a")
        for el in setting_options:
            if el.text == "Audio Settings":
                el.click()
                break
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#video")))
        self.driver.execute_script("document.querySelector('#video').click()")
        time.sleep(1)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                     ".footer-button-base__button.send-video-container__btn")))
        
        self.driver.execute_script("document.querySelector('button.footer-button-base__button.send-video-container__btn').click()")
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#stats")))
        self.driver.execute_script("document.querySelector('#stats').click()")
        time.sleep(1)

    def get_meetin_link_and_password(self):
        try:
            self.get_login_id()
            self.get_login_passwd()
            print("pasword and email fetched succesfuly for login")
        except Exception as e:
            print("error in gettig password and meeting id",e)

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

    def capture_audio_stats(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                    "//*[@id='Audio']"))).click()
        time.sleep(1)
        freq = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                            "//*[@id='Audio-tab']/div/table/tbody/tr[1]/td[2]"))).text
        freq = freq.replace(" khz", "")
        freq_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                "//*[@id='Audio-tab']/div/table/tbody/tr[1]/td[3]"))).text
        freq_rec = freq_rec.replace(" khz", "")
        lat = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                           "//*[@id='Audio-tab']/div/table/tbody/tr[2]/td[2]"))).text
        lat = lat.replace(" ms", "")
        lat_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                               "//*[@id='Audio-tab']/div/table/tbody/tr[2]/td[3]"))).text
        lat_rec = lat_rec.replace(" ms", "")
        jitt = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                            "//*[@id='Audio-tab']/div/table/tbody/tr[3]/td[2]"))).text
        jitt = jitt.replace(" ms", "")
        jitt_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                "//*[@id='Audio-tab']/div/table/tbody/tr[3]/td[3]"))).text
        jitt_rec = jitt_rec.replace(" ms", "")
        pack = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                            "//*[@id='Audio-tab']/div/table/tbody/tr[4]/td[2]"))).text
        packet_loss = re.sub(r'\s*\(.*?\)', '', pack)
        packet_loss_ = packet_loss.replace('%', '')
        pack_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                "//*[@id='Audio-tab']/div/table/tbody/tr[4]/td[2]"))).text
        packet_rec = re.sub(r'\s*\(.*?\)', '', pack_rec)
        packet_rec_ = packet_rec.replace('%', '')
        return [freq if freq != "-" else "0",lat if lat != "-" else "0",jitt if jitt != "-" else "0",packet_loss_ if packet_loss_ != "-" else "0",freq_rec if freq_rec != "-" else "0",lat_rec if lat_rec != "-" else "0",jitt_rec if jitt_rec != "-" else "0",packet_rec_ if packet_rec_ != "-" else "0"]

    def capture_video_stats(self):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='Video']"))).click()
        time.sleep(1)
        latency = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                               "//*[@id='Video-tab']/div/table/tbody/tr[1]/td[2]"))).text
        latency = latency.replace(" ms", "")
        latency_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                   "//*[@id='Video-tab']/div/table/tbody/tr[1]/td[3]"))).text
        latency_rec = latency_rec.replace(" ms", "")
        jitter = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                              "//*[@id='Video-tab']/div/table/tbody/tr[2]/td[2]"))).text
        jitter = jitter.replace(" ms", "")
        jitter_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                  "//*[@id='Video-tab']/div/table/tbody/tr[2]/td[3]"))).text
        jitter_rec = jitter_rec.replace(" ms", "")
        packet_loss = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                   "//*[@id='Video-tab']/div/table/tbody/tr[3]/td[2]"))).text
        packet_loss_vi = re.sub(r'\s*\(.*?\)', '', packet_loss)
        packet_loss_vi = packet_loss_vi.replace('%', '')
        packet_loss_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                       "//*[@id='Video-tab']/div/table/tbody/tr[3]/td[3]"))).text
        packet_loss_vi_rec = re.sub(r'\s*\(.*?\)', '', packet_loss_rec)
        packet_loss_vi_rec = packet_loss_vi_rec.replace('%', '')
        resolution = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                              "//*[@id='Video-tab']/div/table/tbody/tr[4]/td[2]"))).text
        resolution_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                  "//*[@id='Video-tab']/div/table/tbody/tr[4]/td[3]"))).text
        frames_per_second = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                         "//*[@id='Video-tab']/div/table/tbody/tr[5]/td[2]"))).text
        frames_per_second = frames_per_second.replace(" fps", "")
        frames_per_second_rec = self.wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                             "//*[@id='Video-tab']/div/table/tbody/tr[5]/td[3]"))).text
        frames_per_second_rec = frames_per_second_rec.replace(" fps", "")
        # return [latency if latency != "-" else "0",latency_rec if latency_rec != "-" else "0",jitter if jitter != "-" else "0",jitter_rec if jitter_rec != "-" else "0",packet_loss if packet_loss != "-" else "0",packet_loss_rec if packet_loss_rec != "-" else "0",resolution if resolution != "-" else "0",resolution_rec if resolution_rec != "-" else "0",frames_per_second if frames_per_second != "-" else "0",frames_per_second_rec if frames_per_second_rec != "-" else "0"]
        return [latency if latency != "-" else "0",jitter if jitter != "-" else "0",packet_loss_vi if packet_loss_vi != "-" else "0",resolution if resolution != "-" else "0",frames_per_second if frames_per_second != "-" else "0",latency_rec if latency_rec != "-" else "0",jitter_rec if jitter_rec != "-" else "0",packet_loss_vi_rec if packet_loss_vi_rec != "-" else "0",resolution_rec if resolution_rec != "-" else "0",frames_per_second_rec if frames_per_second_rec != "-" else "0"]
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
            audio_stats = self.capture_audio_stats()
        else:
            audio_stats = ["0","0","0","0","0","0","0","0"]
        if self.video:
            video_stats = self.capture_video_stats()
        else:
            video_stats = ["0","0","0","0","0","0","0","0","0","0"]
        return [self.get_formated_time(datetime.now(self.tz).isoformat())]+audio_stats+video_stats

    def get_formated_time(self,timestamp_str):
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
                print(data,str(data))
                print(type(data))
                self.new_login_url = data.get('login_url')
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
            else:
                print(f"Failed to fetch remote login password. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {e}")

    def transfer_files(self,filename):
        
        username = 'lanforge'
        password = 'lanforge'
        
        # Get the full path of the CSV file
        local_file_path = os.path.join(os.path.dirname(__file__), f'{filename}')
        
        # Ensure the file exists
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"The file {filename} does not exist in the current directory.")
        
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(self.server_ip.split(":")[0], username=username, password=password)
            
            # Use SFTP to transfer the file
            sftp = ssh.open_sftp()
            remote_file_path = self.path
            print("transfering ",local_file_path,"to ",remote_file_path)
            print(self.server_ip.split(":")[0])
            sftp.put(local_file_path, os.path.join(remote_file_path, filename))
            sftp.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
        finally:
            ssh.close()

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
    # Example usage:
    zoom_client = ZoomClient()  # Replace with your actual server IP
    zoom_client.start_zoom()
