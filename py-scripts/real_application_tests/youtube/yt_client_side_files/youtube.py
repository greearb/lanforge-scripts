#!/usr/bin/python3

# use python version 3.9.x
# use pip 24
# Intsall selenium > 4.17.x
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import argparse
import time
from datetime import datetime, timedelta
import requests
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import platform


class YouTube(object):

    def __init__(self, url, resolution, host, port, duration, device_name, driver):
        self.url = url
        self.resolution = resolution
        self.device_name = device_name
        self.host = host
        self.port = port
        self.driver = driver
        self.duration = duration
        self.dataset = []
        self.stop_signal = False

    def simulate_human_movements(self):
        try:
            actions = ActionChains(self.driver)
            for _ in range(random.randint(2, 5)):
                actions.move_by_offset(random.randint(-20, 20), random.randint(-20, 20))
                actions.perform()
                time.sleep(random.uniform(0.1, 0.3))
            print("Simulated human movements.")
        except Exception as e:
            print(f"Error simulating mouse movements: {e}")

    def get_video_id(self):
        return self.url.split("=")[1]

    def load_video(self):
        print("Loading url...")
        self.driver.get(self.url)
        return True

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f"http://{self.host}:5002/check_stop"

            response = requests.get(endpoint_url)  # Replace with your Flask server URL
            if response.status_code == 200:

                stop_signal_from_server = response.json().get("stop", False)

                # Only update if the server's stop signal is True
                if stop_signal_from_server:
                    self.stop_signal = True
                    print("Stop signal received from the server. Exiting the loop.")
                else:

                    print("No stop signal received from the server. Continuing.")
            return self.stop_signal
        except Exception as e:
            print(f"Error checking stop signal: {e}")

    def select_resolution(self):
        # Don't bother selecting resolution for Auto
        if self.resolution == "Auto":
            print("Playing in Auto resolution.")
            return True

        print("Selecting resolution...")
        time.sleep(0.2)
        sb = self.driver.find_element(
            By.CSS_SELECTOR, ".ytp-button.ytp-settings-button"
        )
        sb.click()
        time.sleep(0.3)
        try:
            res = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-menuitem-label")
            for item in res:
                if item.text == "Quality":
                    item.click()
                    break
        except Exception:
            print("no quality element found")
        time.sleep(0.3)
        try:
            res = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-menuitem-label")
            print(res)
            for item in res:
                print(item.text)
                if self.resolution in item.text:
                    item.click()
                    print("Selected", self.resolution)
                    return True
            print("No quality matched.Selecting Auto")
            for item in res:
                if "Auto" in item.text:
                    item.click()
            return True
        except Exception as e:
            print(e)
            return False

    def enable_stats(self):
        movie_player = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".html5-video-container"))
        )
        movie_player = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".html5-video-container"))
        )
        self.hover = ActionChains(self.driver).move_to_element(movie_player)
        self.hover.perform()
        movie_player = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".html5-video-container"))
        )
        ActionChains(self.driver).context_click(movie_player).perform()
        options = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-menuitem")
        for option in options:
            option_child = option.find_element(By.CSS_SELECTOR, ".ytp-menuitem-label")
            if option_child.text == "Stats for nerds":
                option_child.click()
                print("Enabled stats collection.")
                return True
        try:
            self.driver.execute_script(
                'document.getElementsByClassName("ytp-menuitem")[6].click();'
            )
            return True
        except Exception:
            return False

    def get_stats(self):
        elem = self.driver.find_element(
            By.CSS_SELECTOR, ".html5-video-info-panel-content.ytp-sfn-content"
        )
        stats_data = elem.text
        stats_data = stats_data.replace(" ", "")
        viewport_match = re.search(
            r"Viewport/Frames([\d+x]+)(?:\*[\d.]+)?/([\d]+)droppedof([\d]+)", stats_data
        )
        current_optimal_res_match = re.search(
            r"Current/OptimalRes([\d@x]+)/([\d@x]+)", stats_data
        )
        # Initialize an empty dictionary to store extracted values
        data = {}
        # Check and assign the extracted values if matches were found
        if viewport_match:
            data["Viewport"] = viewport_match.group(1)  # e.g., '1280x720'
            data["DroppedFrames"] = viewport_match.group(2)  # e.g., '0'
            data["TotalFrames"] = viewport_match.group(3)  # e.g., '3930'

        if current_optimal_res_match:
            data["CurrentRes"] = current_optimal_res_match.group(
                1
            )  # e.g., '1920x1080@60'
            data["OptimalRes"] = current_optimal_res_match.group(
                2
            )  # e.g., '1920x1080@60'

        buffer_health_match = re.search(r"BufferHealth([\d.]+)s", stats_data)
        if buffer_health_match:
            data["BufferHealth"] = buffer_health_match.group(1)

        current_time = datetime.now().strftime("%H:%M:%S")
        data["Timestamp"] = current_time

        return data

    def get_current_seek(self):
        elem = self.driver.find_element(By.CSS_SELECTOR, ".ytp-time-current")
        return elem.text

    def get_video_duration(self):
        elem = self.driver.find_element(By.CSS_SELECTOR, ".ytp-time-duration")
        return elem.text

    def enable_loop(self):
        movie_player = self.driver.find_element(
            By.CSS_SELECTOR, ".html5-video-container"
        )
        self.hover = ActionChains(self.driver).move_to_element(movie_player)
        self.hover.perform()
        ActionChains(self.driver).context_click(movie_player).perform()
        options = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-menuitem")
        for option in options:
            option_child = option.find_element(By.CSS_SELECTOR, ".ytp-menuitem-label")
            if option_child.text == "Loop":
                option_child.click()
                print("Enabled loop playback.")
                return True
        try:
            self.driver.execute_script(
                'document.getElementsByClassName("ytp-menuitem")[0].click();'
            )
            return True
        except Exception:
            return False

    def full_screen(self):
        try:
            elem = self.driver.find_element(
                By.CSS_SELECTOR, ".ytp-fullscreen-button.ytp-button"
            )
            elem.click()
        except Exception:
            print("Unable to do full screen")

    def play(self):
        if not self.load_video():
            self.stop()
            return
        self.simulate_human_movements()

        if not self.enable_stats():
            self.stop()
            return
        if self.duration:
            if not self.enable_loop():
                self.stop()
                return

        if not self.select_resolution():
            self.stop()
            return

        self.video_duration = self.get_video_duration()
        time.sleep(1)
        print("start playing")
        self.start()
        self.full_screen()
        if self.duration:
            end_time = datetime.now() + timedelta(minutes=self.duration)
            while datetime.now() <= end_time:
                if self.check_stop_signal():
                    break
                stats = self.get_stats()
                self.dataset.append(stats)
                self.send_stats_to_api(stats, self.device_name)
                time.sleep(1)
            stats = self.get_stats()
            self.dataset.append(stats)
            self.send_stats_to_api(stats, self.device_name, stop=True)
        else:
            time_array = self.video_duration.split(":")
            time_array = list(map(int, time_array))
            if len(time_array) == 3:
                delta = timedelta(
                    hours=time_array[0], minutes=time_array[1], seconds=time_array[2]
                )
            else:
                delta = timedelta(minutes=time_array[0], seconds=time_array[1])
            end_time = datetime.now() + timedelta(seconds=delta.total_seconds())
            while datetime.now() < end_time:
                stats = self.get_stats()
                self.dataset.append(stats)
                self.send_stats_to_api(stats, self.device_name)
                time.sleep(1)
            stats = self.get_stats()
            self.dataset.append(stats, self.device_name)
            self.send_stats_to_api(stats, stop=True)

        print("stop playing")
        self.stop()
        pass

    def start(self):
        self.driver.execute_script(
            'if(document.getElementsByClassName("ytp-play-button ytp-button")[0].dataset.titlenotooltip=="Play")document.getElementsByClassName("ytp-play-button ytp-button")[0].click();'
        )
        elem = self.driver.find_element(By.CSS_SELECTOR, ".ytp-play-button.ytp-button")
        if elem.get_attribute("data-title-no-tooltip") != "Pause":
            elem.click()

    def stop(self):
        print("Closing driver...")
        self.driver.close()
        print("Done\n\n")

    def send_stats_to_api(self, stats, device_name, stop=False):
        try:
            url = f"http://{self.host}:5002/youtube_stats"
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                device_name: stats,  # Device name as the key and stats as the value
                "stop": stop,  # Stop remains as a separate key
            }

            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                print("Successfully sent stats to API.")
            else:
                print(
                    f"Failed to send stats to API. Status code: {response.status_code}"
                )
        except Exception as e:
            print(f"An error occurred while sending stats to API: {e}")


def main():

    parser = argparse.ArgumentParser(
        prog="youtube.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
        Youtube streaming automation
         """,
        description="""\
NAME: youtube.py
PURPOSE: This script will open youtube over browser and play it for mentioned duration or single loop and get the reporting stats

Example:
    # for running a single loop of any url with Auto video resolution

        python3 youtube.py --url <video url>

    # for running a single loop of any url with required video quality

        python3 youtube.py --url <video url> --res <resoultion>

    # for running a video for certain amount of time

        python3 youtube.py --url <video url> --duration <duration in minuites>
    PS: If we mentioned the duration the loop option of video will be enabled automatically

    --res <resolution>
         144p
         240p
         360p
         480p
         720p
         1080p
    if resoultion is not there in options then video will play with Auto quality

    --duration <duration in minitues>
         If we mentioned the duration the loop option of video will be enabled automatically
         and if not then video will play only once

    --env <enviornment variable>=<enviornment value>
        If required to assign multiple envirnment variable just use --env key=value again for other values
        example python3 youtube.py --env python=python3 --env DISPLAY=:0
          """,
    )

    parser.add_argument(
        "--url", type=str, default="https://www.youtube.com/watch?v=4GnVDPD01as"
    )
    parser.add_argument("--res", type=str, default="Auto")
    parser.add_argument("--duration", default=0, type=int)
    parser.add_argument("--env", action="extend", nargs="+", default=[])

    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--port", type=str, default=8000)
    parser.add_argument("--device_name", type=str, required=True)

    args = parser.parse_args()

    for argument in args.env:
        arg = argument.split("=")
        os.environ[arg[0]] = arg[1]
    print(os.environ)
    service = Service()
    options = webdriver.ChromeOptions()
    options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
    )
    # # Performance-related options
    # options.add_argument("--process-per-site")
    # options.add_argument("--renderer-process-limit=4")
    # options.add_argument("--disable-background-timer-throttling")
    # options.add_argument("--disable-backgrounding-occluded-windows")
    # options.add_argument("--enable-low-res-tiling")
    # options.add_argument("--force-gpu-mem-available-mb=4096")
    # options.add_argument("--memory-pressure-thresholds-mb=2048")
    # options.add_experimental_option("detach", True)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if platform.system() == "Windows":
        adguard_path = os.path.join(
            "C:\\", "Program Files (x86)", "LANforge-Server", "adguard"
        )
    elif platform.system() == "Linux":
        adguard_path = os.path.join(os.sep, "home", "lanforge", "adguard")
    elif platform.system() == "Darwin":  # macOS
        adguard_path = os.path.join(os.sep, "Users", "lanforge", "adguard")
    else:
        raise Exception("Unsupported OS")

    options.add_argument(f"load-extension={adguard_path}")

    driver = webdriver.Chrome(
        service=service, options=options
    )  # Or choose the appropriate webdriver for your browser

    yt = YouTube(
        args.url,
        args.res,
        args.host,
        args.port,
        args.duration,
        args.device_name,
        driver,
    )
    if args.duration != 0:
        yt.duration = args.duration
    yt.play()

    pass


if __name__ == "__main__":
    main()