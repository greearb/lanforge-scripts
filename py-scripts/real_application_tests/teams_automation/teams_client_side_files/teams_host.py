from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pyperclip
import os
import requests
import sys
import argparse
import logging
import traceback
from datetime import datetime
import socket
import pytz
import pyautogui

pyautogui.FAILSAFE = False

# 1. Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "teams_host.log",
            mode="w",
        ),  # Writes to file
        logging.StreamHandler(sys.stdout),  # Writes to terminal
    ],
)

# 2. Create the logger instance
logger = logging.getLogger(__name__)


class TeamsHost:
    def __init__(
        self,
        server_ip=None,
    ):

        self.prefs = {
            "profile.default_content_setting_values.media_stream_mic": 1,  # Allow microphone access
            "profile.default_content_setting_values.media_stream_camera": 1,  # Allow camera access
        }
        self.opt = Options()
        # self.opt.add_experimental_option("debuggerAddress","localhost:8989")
        # self.opt.add_argument("--disable-extensions")
        self.opt.add_experimental_option("prefs", self.prefs)
        # self.opt.add_argument("--use-fake-ui-for-media-stream")
        # self.opt.add_argument("--use-fake-device-for-media-stream")
        # self.opt.add_experimental_option("debuggerAddress","localhost:8989")
        self.opt.add_argument("--disable-extensions")
        self.opt.add_argument("--disable-popup-blocking")
        self.opt.add_argument("--disable-blink-features=AutomationControlled")
        self.opt.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.opt.add_experimental_option("useAutomationExtension", False)
        # self.opt.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=self.opt)
        self.driver.maximize_window()
        self.email = None
        self.passwd = None
        self.no_of_devices = None
        self.server_ip = server_ip
        self.participants_req = None
        self.tz = pytz.timezone("Asia/Kolkata")
        self.base_url = f"http://{self.server_ip}:5005"
        self.start_time = None
        self.end_time = None
        self.audio = None
        self.video = None
        self.stop_signal = False

    def wait_for_element(self, xpathvalue):
        try:
            return WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.XPATH, xpathvalue))
            )
        except Exception as e:
            logger.error(f"Element not found: {xpathvalue}. Error: {e}")
            return None

    def login(
        self,
    ):
        try:
            self.driver.get("https://teams.microsoft.com/v2/")
            # wait for the emailid field
            email_input = self.wait_for_element('//*[@id="i0116"]')
            # enter email id into the field
            email_input.send_keys(self.email)

            nextButton = self.wait_for_element('//*[@id="idSIButton9"]')
            nextButton.click()

            # wait for password field
            passElement = WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.ID, "i0118"))
            )
            # enter password
            passElement.click()
            if sys.platform.startswith("linux"):
                pyautogui.write(self.passwd, interval=0.05)
            else:
                passElement.send_keys(self.passwd)

            signin = self.wait_for_element('//*[@id="idSIButton9"]')
            signin.click()

            yesbutton = self.wait_for_element('//*[@id="idSIButton9"]')
            yesbutton.click()

            # switchnow=self.wait_for_element('//*[@id="ngdialog1"]/div[2]/div/div/div/div[2]/div/div/button')
            # if(switchnow):
            #     switchnow.click()

        except Exception as e:
            self.driver.quit()
            logger.error(f"An error occurred while login: {e}")
            traceback.print_exc()
            sys.exit(1)

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f"{self.base_url}/check_stop"

            response = requests.get(endpoint_url)  # Replace with your Flask server URL
            if response.status_code == 200:

                stop_signal_from_server = response.json().get("stop", False)

                # Only update if the server's stop signal is True
                if stop_signal_from_server:
                    self.stop_signal = True
                    logger.info(
                        "Stop signal received from the server. Exiting the loop."
                    )
                else:

                    logger.info("No stop signal received from the server. Continuing.")
            return self.stop_signal
        except Exception as e:
            logger.error(f"Error checking stop signal: {e}")

    def start_meeting(
        self,
    ):

        try:

            calendar_button = WebDriverWait(self.driver, 120).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label, 'Calendar')]")
                )
            )

            logger.info("Calendar button found! App is fully loaded.")

            self.driver.execute_script("arguments[0].click();", calendar_button)
            logger.info("Calendar button clicked via JavaScript.")

            meet_now = WebDriverWait(self.driver, 180).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'button[data-tid="calendar_header_open_meet_now_flyout_button"]',
                    )
                )
            )
            meet_now.click()

            time.sleep(3)

            start_meet = self.wait_for_element('//button[text()="Start meeting"]')

            start_meet.click()

            time.sleep(3)

            join_now = self.wait_for_element('//*[@id="prejoin-join-button"]')

            join_now.click()

            meeting_link_button = self.wait_for_element(
                '//button[@data-tid="share_meeting_invite_dialog_copy_link_button"]'
            )
            meeting_link_button.click()

            time.sleep(3)

            self.meeting_link = pyperclip.paste()

            # self.meeting_link = self.driver.current_url

            close_pope_up = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button.ui-button.ui-dialog__headerAction[title='Close']",
                    )
                )
            )
            close_pope_up.click()

            time.sleep(3)

            camera_button = self.wait_for_element('//*[@id="video-button"]')
            camera_button.click()

            time.sleep(3)

        except Exception as e:
            self.driver.quit()
            logger.error(f"An error occurred while starting the meeting: {e}")
            traceback.print_exc()
            sys.exit(1)

    def network_stats(
        self,
    ):
        try:
            view_more = self.wait_for_element(
                "//button[@data-tid='call-health-category-Network']"
            )

            view_more.click()

            self.nw_send_limit = self.wait_for_element(
                "//span[@data-tid='network-sent-bw-estimate']"
            ).text

            self.nw_recevie_limit = self.wait_for_element(
                "//span[@data-tid='network-received-bw-estimate']"
            ).text

            self.nw_rtt = self.wait_for_element(
                "//span[@data-tid='network-send-rtt-avg']"
            ).text

            # it is in percentage
            self.nw_recevied_pkt_loss = self.wait_for_element(
                "//span[@data-tid='network-recv-loss-rate-avg']"
            ).text

            back = self.wait_for_element(
                "//button[@data-tid='rail-header-back-button']"
            )
            back.click()

            self.netstat_data = [
                self.nw_recevie_limit,
                self.nw_recevie_limit,
                self.nw_rtt,
                self.nw_recevied_pkt_loss,
            ]

            return self.netstat_data

        except Exception as e:
            self.driver.quit()
            logger.error(f"An error occurred while fetching network stats: {e}")
            traceback.print_exc()
            sys.exit(1)

    def get_stats_flags(self):
        endpoint_url = f"{self.base_url}/stats_opt"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                data = response.json()
                self.audio = data.get("audio_stats")
                self.video = data.get("video_stats")
            else:
                logger.error(
                    f"Failed to fetch stats flag. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            logger.error(f"Request error in get_stats_flags: {e}")
        return None

    def audio_stats(
        self,
    ):

        try:
            view_more = self.wait_for_element(
                "//button[@data-tid='call-health-category-Audio']"
            )
            view_more.click()

            # audio sent bitrate in Kbps
            self.au_sent_bitrate = self.wait_for_element(
                "//span[@data-tid='audio-send-bps']"
            ).text
            self.au_sent_bitrate = self.au_sent_bitrate.replace("Kbps", "").strip()
            if self.au_sent_bitrate and self.au_sent_bitrate != "--":
                self.au_sent_bitrate = float(self.au_sent_bitrate)
            else:
                self.au_sent_bitrate = 0.0

            # Audio sent packets
            self.au_sent_pkts = self.wait_for_element(
                "//span[@data-tid='audio-rtp-packets-sent']"
            ).text
            self.au_sent_pkts = self.au_sent_pkts.replace("packets", "").strip()
            if self.au_sent_pkts and self.au_sent_pkts != "--":
                self.au_sent_pkts = int(self.au_sent_pkts)
            else:
                self.au_sent_pkts = 0

            # Audio RTT in ms
            self.au_rtt = self.wait_for_element(
                "//span[@data-tid='audio-send-rtt-avg']"
            ).text
            self.au_rtt = self.au_rtt.replace("ms", "")
            if self.au_rtt and self.au_rtt != "--":
                self.au_rtt = float(self.au_rtt)
            else:
                self.au_rtt = 0.0

            # Audio sent codec
            self.au_sent_codec = self.wait_for_element(
                "//span[@data-tid='audio-send-codec']"
            ).text
            if self.au_sent_codec and self.au_sent_codec == "--":
                self.au_sent_codec = "NA"
            else:
                self.au_sent_codec = self.au_sent_codec.strip()

            # Audio Recevied Jitter
            self.au_recv_jitter = self.wait_for_element(
                "//span[@data-tid='audio-nw-jitter-avg']"
            ).text
            self.au_recv_jitter = self.au_recv_jitter.replace("ms", "")
            if self.au_recv_jitter and self.au_recv_jitter.strip() != "--":
                self.au_recv_jitter = float(self.au_recv_jitter)
            else:
                self.au_recv_jitter = 0.0

            # Audio recevied packets lost percentage
            self.au_recv_pkt_loss = self.wait_for_element(
                "//span[@data-tid='audio-recv-loss-rate-avg']"
            ).text
            self.au_recv_pkt_loss = self.au_recv_pkt_loss.replace("%", "").strip()
            if self.au_recv_pkt_loss and self.au_recv_pkt_loss != "--":
                self.au_recv_pkt_loss = float(self.au_recv_pkt_loss)
            else:
                self.au_recv_pkt_loss = 0.0

            # audio recevied packets
            self.au_recv_pkts = self.wait_for_element(
                "//span[@data-tid='audio-rtp-packets-received']"
            ).text
            self.au_recv_pkts = self.au_recv_pkts.replace("packets", "").strip()
            if self.au_recv_pkts and self.au_recv_pkts != "--":
                self.au_recv_pkts = int(self.au_recv_pkts)
            else:
                self.au_recv_pkts = 0

            self.au_recv_codec = self.wait_for_element(
                "//span[@data-tid='audio-received-codec']"
            ).text
            if self.au_recv_codec and self.au_recv_codec == "--":
                self.au_recv_codec = "NA"
            # time.sleep(3)
            back = self.wait_for_element(
                "//button[@data-tid='rail-header-back-button']"
            )
            back.click()

            # audio_stats_data=[self.au_sent_bitrate,self.au_sent_pkts,self.au_rtt,self.au_sent_codec,self.au_recv_jitter,self.au_recv_pkt_loss,self.au_recv_pkts,self.au_recv_codec]

            audio_stats_data = {
                "au_sent_bitrate": self.au_sent_bitrate,
                "au_sent_pkts": self.au_sent_pkts,
                "au_rtt": self.au_rtt,
                "au_sent_codec": self.au_sent_codec,
                "au_recv_jitter": self.au_recv_jitter,
                "au_recv_pkt_loss": self.au_recv_pkt_loss,
                "au_recv_pkts": self.au_recv_pkts,
                "au_recv_codec": self.au_recv_codec,
            }

            return audio_stats_data

        except Exception as e:
            self.driver.quit()
            logger.error(f"An error occurred in collecting audio stats: {e}")
            traceback.print_exc()
            sys.exit(1)

    def video_stats(
        self,
    ):

        try:

            view_more = self.wait_for_element(
                "//button[@data-tid='call-health-category-Video']"
            )
            view_more.click()

            # video sent bitrate in Mbps
            self.vi_sent_bitrate = self.wait_for_element(
                "//span[@data-tid='video-send-current-bitrate']"
            ).text
            if self.vi_sent_bitrate and self.vi_sent_bitrate != "--":
                self.vi_sent_bitrate = self.vi_sent_bitrate.replace("Mbps", "").strip()
                self.vi_sent_bitrate = float(self.vi_sent_bitrate)
            else:
                self.vi_sent_bitrate = 0.0

            # Video received bitrate in Kbps
            self.vi_recv_bitrate = self.wait_for_element(
                "//span[@data-tid='video-receive-current-bitrate']"
            ).text
            if self.vi_recv_bitrate and self.vi_recv_bitrate != "--":
                self.vi_recv_bitrate = self.vi_recv_bitrate.replace("Mbps", "").strip()
                self.vi_recv_bitrate = float(self.vi_recv_bitrate)
            else:
                self.vi_recv_bitrate = 0.0

            # Video Sent frame rate in fps
            self.vi_sent_frame_rate = self.wait_for_element(
                "//span[@data-tid='video-send-current-frame-rate']"
            ).text
            if self.vi_sent_frame_rate and self.vi_sent_frame_rate != "--":
                self.vi_sent_frame_rate = self.vi_sent_frame_rate.replace(
                    "fps", ""
                ).strip()
                self.vi_sent_frame_rate = float(self.vi_sent_frame_rate)
            else:
                self.vi_sent_frame_rate = 0.0

            # Video sent resolution in px
            self.vi_sent_res = self.wait_for_element(
                "//span[@data-tid='video-send-resolution']"
            ).text
            if self.vi_sent_res and self.vi_sent_res != "--":
                self.vi_sent_res = self.vi_sent_res.replace("px", "").strip()
            else:
                self.vi_sent_res = "NA"

            # Video RTT in ms
            self.vi_rtt = self.wait_for_element(
                "//span[@data-tid='video-send-rtt-avg']"
            ).text
            self.vi_rtt = self.vi_rtt.replace("ms", "")
            if self.vi_rtt != "--" and self.vi_rtt:
                self.vi_rtt = float(self.vi_rtt)
            else:
                self.vi_rtt = 0.0

            # Video sent packets
            self.vi_sent_pkts = self.wait_for_element(
                "//span[@data-tid='video-rtp-packets-sent']"
            ).text
            if self.vi_sent_pkts and self.vi_sent_pkts != "--":
                self.vi_sent_pkts = self.vi_sent_pkts.replace("packets", "").strip()
                self.vi_sent_pkts = int(self.vi_sent_pkts)
            else:
                self.vi_sent_pkts = 0

            # video sent codec
            self.vi_sent_codec = self.wait_for_element(
                "//span[@data-tid='video-sent-codec-name']"
            ).text
            if self.vi_sent_codec and self.vi_sent_codec == "--":
                self.vi_sent_codec = "NA"
            else:
                self.vi_sent_codec = self.vi_sent_codec.strip()

            # Video processing type
            self.vi_processing = self.wait_for_element(
                "//span[@data-tid='video-processing-type']"
            ).text
            # time.sleep(3)
            back = self.wait_for_element(
                "//button[@data-tid='rail-header-back-button']"
            )

            back.click()

            video_stats_data = [
                self.vi_sent_bitrate,
                self.vi_recv_bitrate,
                self.vi_sent_frame_rate,
                self.vi_sent_res,
                self.vi_rtt,
                self.vi_sent_pkts,
                self.vi_sent_codec,
                self.vi_processing,
            ]

            video_stats_data = {
                "vi_sent_bitrate": self.vi_sent_bitrate,
                "vi_recv_bitrate": self.vi_recv_bitrate,
                "vi_sent_frame_rate": self.vi_sent_frame_rate,
                "vi_sent_res": self.vi_sent_res,
                "vi_rtt": self.vi_rtt,
                "vi_sent_pkts": self.vi_sent_pkts,
                "vi_sent_codec": self.vi_sent_codec,
                "vi_processing": self.vi_processing,
            }

            return video_stats_data

        except Exception as e:
            self.driver.quit()
            logger.error(f"An error occurred in collecting video stats: {e}")
            traceback.print_exc()
            sys.exit(1)

    def open_call_health(
        self,
    ):
        try:
            show_more = self.wait_for_element(
                '//button[@id="callingButtons-showMoreBtn"]'
            )

            show_more.click()

            time.sleep(3)

            settings = self.wait_for_element('//div[@id="SettingsMenuControl-id"]')

            settings.click()

            call_health = self.wait_for_element('//*[@id="call-health-button"]')
            call_health.click()

        except Exception as e:
            self.driver.quit()
            logger.error(f"An error occurred in opening call health: {e}")
            traceback.print_exc()
            sys.exit(1)

    def get_credentials(self):
        try:
            response = requests.get(
                f"http://{self.server_ip}:5005/get_credentials", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.email = data["email"].strip()
                self.passwd = data["password"].strip()
            else:
                logger.error(
                    f"❌ Failed to get credentials: {response.json().get('log')}"
                )
                self.email = None
                self.passwd = None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error during credential request: {e}")
            self.email = None
            self.passwd = None

    def get_start_and_end_time(self):
        endpoint_url = f"{self.base_url}/get_start_end_time"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                data = response.json()
                self.start_time = data.get("start_time")
                self.end_time = data.get("end_time")
            else:
                logger.error(
                    f"Failed to fetch Start and End Time. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            logger.error(f"Request error in get_start_and_end_time: {e}")
        return None

    def update_participation(self):

        endpoint_url = f"{self.base_url}/set_participants_joined"
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:
                logger.info("Device participation status updated successfully.")
            else:
                logger.error(
                    f"Failed to update device participation status. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            logger.error(f"Request error in update_participation: {e}")

    def update_login_completed(self):
        endpoint_url = f"{self.base_url}/login_completed"
        data = {"login_completed": 1}

        try:
            response = requests.post(endpoint_url, json=data)
            if response.status_code == 200:
                logger.info("Login completed status updated successfully.")
            else:
                logger.error(
                    f"Failed to update login completed status. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            logger.error(f"Request error in update_login_completed: {e}")

    def send_stats_to_server(self, hostname, audio_stats, video_stats):
        if self.audio:
            payload = {
                hostname: {
                    "timestamp": datetime.now().isoformat(),
                    "audio_stats": audio_stats,
                }
            }
        if self.video:
            payload = {
                hostname: {
                    "timestamp": datetime.now().isoformat(),
                    "video_stats": video_stats,
                }
            }
        if self.audio and self.video:
            payload = {
                hostname: {
                    "timestamp": datetime.now().isoformat(),
                    "audio_stats": audio_stats,
                    "video_stats": video_stats,
                }
            }

        try:
            response = requests.post(f"{self.base_url}/upload_stats", json=payload)
            if response.status_code == 200:
                logger.debug(f"Stats uploaded for {hostname}")
            else:
                logger.error(
                    f"Failed to upload stats: {response.status_code} - {response.text}"
                )
        except Exception as e:
            logger.error(f"Exception during uploading stats: {e}")

    def send_meeting_link(self):
        payload = {"meet_link": self.meeting_link}

        try:
            response = requests.post(f"{self.base_url}/meeting_link", json=payload)
            if response.status_code == 200:
                logger.info("Meeting link updated successfully")
            else:
                logger.error(f"Failed to update meeting link: {response.text}")
        except Exception as e:
            logger.error(f"Error sending meeting link: {e}")


def main():
    team = None

    try:

        hostname = socket.gethostname()

        # netstats_header=['Teams Network Send Limit(Mbps)','Teams Network Receive Limit(Mbps)','Network Received Round Trip Time(ms)','Network Received Packet Loss(%)']

        parser = argparse.ArgumentParser(description="Zoom Automation Script")
        parser.add_argument("--ip", required=True, help="Server endpoint ip")
        parser.add_argument("--env", action="extend", nargs="+", default=[])

        args = parser.parse_args()
        for argument in args.env:
            arg = argument.split("=")
            os.environ[arg[0]] = arg[1]

        team = TeamsHost(
            server_ip=args.ip,
        )
        team.get_stats_flags()
        team.get_credentials()
        team.login()
        team.start_meeting()
        team.send_meeting_link()
        time.sleep(3)
        team.update_login_completed()
        team.update_participation()
        team.open_call_health()
        while team.start_time is None or team.end_time is None:
            team.get_start_and_end_time()
            time.sleep(2)

        while team.start_time > datetime.now(team.tz).isoformat():
            time.sleep(2)
            logger.info("waiting for the start time of the Test")

        while team.end_time > datetime.now(team.tz).isoformat():
            logger.info("monitoring the test")
            team.check_stop_signal()
            if team.stop_signal:
                logger.info("Stop signal received from server. Exiting the loop.")
                break
            if team.audio:
                audio_stats = team.audio_stats()

            if team.video:
                video_stats = team.video_stats()
            if team.audio and team.video:
                team.send_stats_to_server(hostname, audio_stats, video_stats)
            elif team.audio:
                team.send_stats_to_server(hostname, audio_stats, None)
            elif team.video:
                team.send_stats_to_server(hostname, None, video_stats)
            time.sleep(1)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        if team and team.driver:
            team.driver.quit()


if __name__ == "__main__":
    main()
