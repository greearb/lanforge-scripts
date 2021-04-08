from paramiko import SSHClient
from scp import SCPClient

class lanforge_reports:

    def pull_reports(self,hostname="localhost", username="lanforge", password="lanforge",report_location="/home/lanforge/html-reports/"):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname=hostname,username=username,password=password)

        with SCPClient(ssh.get_transport()) as scp:
            scp.get(report_location,recursive=True)
            scp.close()
