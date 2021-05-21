import paramiko
from scp import SCPClient

class lanforge_reports:

    def pull_reports(self,hostname="localhost", username="lanforge", password="lanforge", report_location="/home/lanforge/html-reports/"):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password, allow_agent=False, look_for_keys=False)

        with SCPClient(ssh.get_transport()) as scp:
            scp.get(report_location,recursive=True)
            scp.close()
