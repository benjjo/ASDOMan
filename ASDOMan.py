import paramiko
from paramiko import SSHClient
from scp import SCPClient
from pythonping import ping
import os
import time

path = ''
coachList = []

"""
Class IPMan is our ancient hero who downloads the ASDO logs for the list of coaches sent to it. 
Using mad python Kung Fu style object programming, together we can overcome the horror that is ASDO!

"""


class IPMan:

    def __init__(self):
        self.cpsdict = {
            "15001": "10.128.33.21",
            "15002": "10.128.34.21",
            "15003": "10.128.35.21",
            "15004": "10.128.36.21",
            "15005": "10.128.37.21",
            "15006": "10.128.38.21",
            "15007": "10.128.39.21",
            "15008": "10.128.40.21",
            "15009": "10.128.41.21",
            "15010": "10.128.42.21",
            "15011": "10.128.43.21",
            "15101": "10.128.65.21",
            "15102": "10.128.66.21",
            "15103": "10.128.67.21",
            "15104": "10.128.68.21",
            "15105": "10.128.69.21",
            "15106": "10.128.70.21",
            "15107": "10.128.71.21",
            "15108": "10.128.72.21",
            "15109": "10.128.73.21",
            "15110": "10.128.74.21",
            "15201": "10.128.97.21",
            "15202": "10.128.98.21",
            "15203": "10.128.99.21",
            "15204": "10.128.100.21",
            "15205": "10.128.101.21",
            "15206": "10.128.102.21",
            "15207": "10.128.103.21",
            "15208": "10.128.104.21",
            "15209": "10.128.105.21",
            "15210": "10.128.106.21",
            "15211": "10.128.107.21",
            "15212": "10.128.108.21",
            "15213": "10.128.109.21",
            "15214": "10.128.110.21",
            "15301": "10.128.129.21",
            "15302": "10.128.130.21",
            "15303": "10.128.131.21",
            "15304": "10.128.132.21",
            "15305": "10.128.133.21",
            "15306": "10.128.134.21",
            "15307": "10.128.135.21",
            "15308": "10.128.136.21",
            "15309": "10.128.137.21",
            "15310": "10.128.138.21",
            "15311": "10.128.139.21",
            "15312": "10.128.140.21",
            "15313": "10.128.141.21",
            "15314": "10.128.142.21",
            "15315": "10.128.143.21",
            "15316": "10.128.144.21",
            "15317": "10.128.145.21",
            "15318": "10.128.146.21",
            "15319": "10.128.147.21",
            "15320": "10.128.148.21",
            "15321": "10.128.149.21",
            "15322": "10.128.150.21",
            "15323": "10.128.151.21",
            "15324": "10.128.152.21",
            "15325": "10.128.153.21",
            "15326": "10.128.154.21",
            "15327": "10.128.155.21",
            "15328": "10.128.156.21",
            "15329": "10.128.157.21",
            "15330": "10.128.158.21",
            "15331": "10.128.159.21",
            "15332": "10.128.161.21",
            "15333": "10.128.162.21",
            "15334": "10.128.163.21",
            "15335": "10.128.164.21",
            "15336": "10.128.165.21",
            "15337": "10.128.166.21",
            "15338": "10.128.167.21",
            "15339": "10.128.168.21",
            "15340": "10.128.169.21",
        }

        self.cpgdict = {
            "15001": "10.128.33.2",
            "15002": "10.128.34.2",
            "15003": "10.128.35.2",
            "15004": "10.128.36.2",
            "15005": "10.128.37.2",
            "15006": "10.128.38.2",
            "15007": "10.128.39.2",
            "15008": "10.128.40.2",
            "15009": "10.128.41.2",
            "15010": "10.128.42.2",
            "15011": "10.128.43.2",
            "15101": "10.128.65.2",
            "15102": "10.128.66.2",
            "15103": "10.128.67.2",
            "15104": "10.128.68.2",
            "15105": "10.128.69.2",
            "15106": "10.128.70.2",
            "15107": "10.128.71.2",
            "15108": "10.128.72.2",
            "15109": "10.128.73.2",
            "15110": "10.128.74.2",
        }

    # Returns the CPG dictionary item for the argument coach.
    # Will default to home 127.0.0.1 for case None.
    # Will cast int arguments to strings.
    def getCPG(self, coach):
        if type(coach) is int:
            coach = str(coach)

        if self.cpgdict.get(coach) is None:
            coach = 'Home'

        return self.cpgdict.get(coach)

    # Returns the CPS dictionary item for the argument coach.
    # Will default to home 127.0.0.1 for case None.
    # Will cast int arguments to strings.
    def getCPS(self, coach):
        if type(coach) is int:
            coach = str(coach)

        if self.cpsdict.get(coach) is None:
            coach = 'Home'
        return self.cpsdict.get(coach)

    # Automatically downloads the log files from the remote /var/opt/logs folder.
    # Utilises the ssh port 22 protocols.
    def getLogs(self, coach):
        global path
        username = 'root'
        password = 'root'
        host = self.getCPS(coach)
        port = 22
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(host, port, username, password)
            client.exec_command('ls')
            self.makeLogDir(coach)
            # This is a little bit of a hack. SCPClient doesn't allow you to pass a wild
            # character to the string, it just sees it as a literal character.
            # Sanitize gets around this with lambda magic.
            with SCPClient(client.get_transport(), sanitize=lambda x: x) as scp:
                scp.get('/var/opt/logs/ASDO*', path)
            scp.close()
        except:
            print("Failed connection to " + str(coach))

    # Accepts a list as 'coaches' and pings each item in the list.
    def pingAttack(self, coaches):
        for c in coaches:
            print(c + ":\n" + str(ping(self.getCPS(c))))

    # Attempts to make a directory for the current download session.
    # Returns the new folder as a string is successful, else returns None.
    @staticmethod
    def makeLogDir(coach):
        global path
        path = 'logs/' + str(coach) + '/' + str(time.strftime('%Y%m%d', time.localtime()))
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            print('Creation of the directory %s has failed' % path)
            # return False
        else:
            print('Successfully uploaded logs to %s ' % path)
            # return True

    # Grabs the logs for an entire coach rake by iterating through a list of coaches.
    def getRake(self, coachList):
        for coach in coachList:
            self.getLogs(coach)

    # Returns true if coach is currently reachable.
    @staticmethod
    def isCoachReachable(coachIP):
        response = not os.system('ping -n 1 -w 100 ' + str(coachIP))
        return response

    # Creates a list of coaches from the CPS list that are currently reachable.
    def makeCoachList(self, coachList):
        coachList.clear()
        for coach in self.cpsdict.keys():
            print('********** ' + coach + ' **********')
            if self.isCoachReachable(self.getCPS(coach)):
                coachList.append(coach)


getRakeLogs = IPMan()
getRakeLogs.makeCoachList(coachList)
getRakeLogs.getRake(coachList)
print("""

        ░░░░░░░░██░▀▀▀▀▄██▄░░░░░░░░░░░░░
        ██▄░░░░░█░░░░░░▀▀▀▄░░░░░░░░░░░░░
        ░█▀▄▄░░█▀▄░░▄░░░░░█░░░░░░░░▄▄▄██
        ░█▄▄▄▀█▀█▀░▀██░░░█▄█▄░░░▄█████▀▀
        ▀█▄████▄░▄▄░░░░▄▄████████████▀░░
        ░▀██████▄▄▄▄▄██████████████▄█░░░
        ░░░▀█████████████████████▀▀░░░░░
        ░░░░░▀▀██████████████▀▀░░░░░░░░░
        ░░░░░░░█▀▀▀▀▀░░▀░░░▀█░░░░░░░░░░░
        ░░░░░░█░░░░░░░░░░░░░░█░░░░░░░░░░
        ░░░░░█░░░░░░░░░░░░░░░█░░░░░░░░░░
        ░░░░░█░░░░░░░░░░░░░░░█░░░░░░░░░░
        ░░░▄████▄▄░░░░░░░░░░██░░░░░░░░░░
        ░░▄████████░░░░░░░▄███░░░░░░░░░░
        ░░█████████▄▄▄▄███████░░░░░░░░░░
        ░░███████░░░░░░████████░░░░░░░░░
        ░░▀▀█████░░░░░░░▀▀████▀░░░░░░░░░
             ASDO Man Version 1.0
             
""")

print('****** Logs gathered for: ' + str(coachList))

time.sleep(5)
