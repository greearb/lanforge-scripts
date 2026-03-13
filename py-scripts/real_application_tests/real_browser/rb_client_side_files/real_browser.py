from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import argparse
from datetime import datetime, timedelta
import requests
import socket
from statistics import mean
import platform
import subprocess


class RealBrowser():
    def __init__(self, url, count, driver, duration, device_name, server):
        self.url = url

        self.count = count
        self.driver = driver
        self.dataset = []
        self.duration = duration
        self.error = 0
        self.successful_load = 0
        self.tries = 0
        self.load_times = []
        self.load_time = None
        self.device_name = device_name
        self.server = server
        self.sock = None
        self.hostname = socket.gethostname()
        self.stop_signal = False
        self.uc_min = None
        self.uc_max = None
        self.uc_avg = None

    def load_url(self):

        print(self.url)
        self.driver.get(self.url)

    def start(self):
        self.start_time = datetime.now()
        self.end_time = None
        if self.duration:
            self.end_time = self.start_time + timedelta(minutes=self.duration)
        self.tries = 0
        self.error = 0
        self.successful_load = 0
        while ((datetime.now() < self.end_time)):

            if (self.check_stop_signal()):
                break

            try:
                self.load_url()
                self.tries += 1
                # Execute JavaScript to get performance timing data
                performance_data = self.driver.execute_script("return window.performance.timing")

                # Calculate load time
                navigation_start = performance_data['navigationStart']
                load_event_end = performance_data['loadEventEnd']
                if (load_event_end > navigation_start):

                    self.load_time = (load_event_end - navigation_start) / 1000  # Convert milliseconds to seconds

                    self.load_times.append(self.load_time)

                    print(f"Page Load Time: {self.load_time} seconds {self.url}")
                    self.successful_load += 1
                    laptop_stats = {
                        self.hostname: {
                            "url": self.url,
                            "name": self.hostname,
                            "url_loaded": self.tries,
                            "total_urls": self.successful_load,
                            "total_err": self.error,
                            "uc_min": min(self.load_times),
                            "uc_max": max(self.load_times),
                            "uc_avg": mean(self.load_times),
                            "start_time": self.start_time.isoformat()
                        }
                    }
                    self.send_stats(laptop_stats)
            except Exception:

                self.error += 1
                if (len(self.load_times) > 0):
                    self.uc_min = min(self.load_times)
                    self.uc_max = max(self.load_times)
                    self.uc_avg = mean(self.load_times)
                else:
                    self.uc_min = 0.0
                    self.uc_max = 0.0
                    self.uc_avg = 0.0

                laptop_stats = {
                    self.hostname: {
                        "url": self.url,
                        "name": self.hostname,
                        "url_loaded": self.tries,
                        "total_urls": self.successful_load,
                        "total_err": self.error,

                        "uc_min": self.uc_min,
                        "uc_max": self.uc_max,
                        "uc_avg": self.uc_avg,
                        "start_time": self.start_time.isoformat()
                    }
                }
                print("error occured")
                self.send_stats(laptop_stats)
        print("checking whether statments are reaching upto this or not")

    def stop(self):
        self.driver.close()

    def check_stop_signal(self):
        """Check the stop signal from the Flask server."""
        try:
            endpoint_url = f'http://{self.server}:5003/check_stop'
            # endpoint_url = f'http://10.253.8.108:5003/check_stop'

            response = requests.get(endpoint_url)  # Replace with your Flask server URL
            if response.status_code == 200:
                # Get the 'stop' value from the server's response
                stop_signal_from_server = response.json().get('stop', False)

                # Only update if the server's stop signal is True
                if stop_signal_from_server:
                    self.stop_signal = True
                    print("Stop signal received from the server. Exiting the loop.")
                else:
                    # Do not change self.stop_signal if the server's response is False
                    print("No stop signal received from the server. Continuing.")
            return self.stop_signal
        except Exception as e:
            print(f"Error checking stop signal: {e}")

    def send_stats(self, laptop_stats):
        try:
            endpoint_url = f'http://{self.server}:5003/upload_stats'
            # endpoint_url = f'http://10.253.8.108:5003/upload_stats'
            response = requests.post(endpoint_url, json=laptop_stats)
            print(response)
        except Exception as e:
            print("Failed to upload stats", e)

    def kill_chrome_processs(self,):
        os_name = platform.system()

        if os_name == "Linux":
            # Linux: Terminate Chrome processes
            try:
                subprocess.run(["pkill", "-f", "chrome"], check=True)
                subprocess.run(["pkill", "-f", "chromedriver"], check=True)
                subprocess.run(["pkill", "-f", "chrome for testing"], check=True)
            except subprocess.CalledProcessError:
                print("No matching Chrome processes found on Linux.")

        elif os_name == "Darwin":
            # macOS: Terminate Chrome processes
            try:
                subprocess.run(["pkill", "-f", "chrome for testing"], check=True)
                subprocess.run(["pkill", "-f", "chrome"], check=True)
                subprocess.run(["pkill", "-f", "chromedriver"], check=True)
            except subprocess.CalledProcessError:
                print("No matching Chrome processes found on macOS.")

        else:
            # Unsupported OS
            print("Unsupported operating system.")

    def init_driver(self,):
        service = Service()
        options = webdriver.ChromeOptions()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
        # options.add_experimental_option("detach", True)
        options.add_argument("--no-cache")
        options.add_argument('--disk-cache-size=0')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(service=service, options=options)  # Or choose the appropriate webdriver for your browser
        self.driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})


def main():

    parser = argparse.ArgumentParser(
        prog='real_browser.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''\
        Real Browser automation
         ''',
        description='''\
            NAME: real_browser.py
            PURPOSE: This script will open youtube over browser and play it for mentioned duration or single loop and get the reporting stats

                    '''
    )

    parser.add_argument('--url', type=str, default="https://www.youtube.com")
    parser.add_argument('--duration', default=None, type=str)
    parser.add_argument('--count', default=5, type=int)
    parser.add_argument('--test_name', default="", type=str)
    parser.add_argument('--device_name', default="", type=str)
    parser.add_argument('--server', default="", type=str)

    parser.add_argument('--env', action='extend', nargs='+', default=[])

    args = parser.parse_args()

    url = args.url

    duration = args.duration.replace("m", "")
    duration = int(duration)
    print(duration)
    if duration == "":
        exit(0)

    rb = RealBrowser(url=url, count=args.count, duration=duration, driver=None, device_name=args.device_name, server=args.server)
    laptop_stats = {
                        rb.hostname: {
                            "url": rb.url,
                            "name": rb.hostname,
                            "url_loaded": 0,
                            "total_urls": 0,
                            "total_err": 0,
                            "uc_min": 0,
                            "uc_max": 0,
                            "uc_avg": 0,
                            "start_time": datetime.now().isoformat()
                        }
                    }
    rb.send_stats(laptop_stats)
    rb.init_driver()
    rb.start()
    print(f"Total Tries: {rb.tries},Total Successfull Count :{rb.successful_load} ,Error Count :{rb.error}")
    rb.stop()


if __name__ == '__main__':
    main()