import paramiko
from scp import SCPClient

class lanforge_reports:

    def pull_reports(self, hostname="localhost", port=22, username="lanforge", password="lanforge",
                     report_location="/home/lanforge/html-reports/",
                     local_path="../../../reports/"):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password, port=port)

        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_path=report_location, local_path=local_path, recursive=True)
            scp.close()

