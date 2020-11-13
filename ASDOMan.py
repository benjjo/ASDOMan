import sys
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import os
import time
import datetime
from tqdm import tqdm
import subprocess

path = ''
coachList = []


class IPMan:
    """
    Class IPMan is our ancient hero who downloads the ASDO logs for the list of coaches sent to it.
    Using mad python Kung Fu style object programming, together we can overcome the horror that is ASDO!

    Author:     Ben McGuffog, Technical Engineer
    Version:    2020-Oct

    """

    def __init__(self):
        self.cpsdict = {
            # SEATED
            "15001": "10.128.33.21", "15002": "10.128.34.21", "15003": "10.128.35.21",
            "15004": "10.128.36.21", "15005": "10.128.37.21", "15006": "10.128.38.21",
            "15007": "10.128.39.21", "15008": "10.128.40.21", "15009": "10.128.41.21",
            "15010": "10.128.42.21", "15011": "10.128.43.21",
            # CLUB
            "15101": "10.128.65.21", "15102": "10.128.66.21", "15103": "10.128.67.21",
            "15104": "10.128.68.21", "15105": "10.128.69.21", "15106": "10.128.70.21",
            "15107": "10.128.71.21", "15108": "10.128.72.21", "15109": "10.128.73.21",
            "15110": "10.128.74.21",
            # ACCESSIBLE
            "15201": "10.128.97.21", "15202": "10.128.98.21", "15203": "10.128.99.21",
            "15204": "10.128.100.21", "15205": "10.128.101.21", "15206": "10.128.102.21",
            "15207": "10.128.103.21", "15208": "10.128.104.21", "15209": "10.128.105.21",
            "15210": "10.128.106.21", "15211": "10.128.107.21", "15212": "10.128.108.21",
            "15213": "10.128.109.21", "15214": "10.128.110.21",
            # SLEEPER
            "15301": "10.128.129.21", "15302": "10.128.130.21", "15303": "10.128.131.21",
            "15304": "10.128.132.21", "15305": "10.128.133.21", "15306": "10.128.134.21",
            "15307": "10.128.135.21", "15308": "10.128.136.21", "15309": "10.128.137.21",
            "15310": "10.128.138.21", "15311": "10.128.139.21", "15312": "10.128.140.21",
            "15313": "10.128.141.21", "15314": "10.128.142.21", "15315": "10.128.143.21",
            "15316": "10.128.144.21", "15317": "10.128.145.21", "15318": "10.128.146.21",
            "15319": "10.128.147.21", "15320": "10.128.148.21", "15321": "10.128.149.21",
            "15322": "10.128.150.21", "15323": "10.128.151.21", "15324": "10.128.152.21",
            "15325": "10.128.153.21", "15326": "10.128.154.21", "15327": "10.128.155.21",
            "15328": "10.128.156.21", "15329": "10.128.157.21", "15330": "10.128.158.21",
            "15331": "10.128.159.21", "15332": "10.128.161.21", "15333": "10.128.162.21",
            "15334": "10.128.163.21", "15335": "10.128.164.21", "15336": "10.128.165.21",
            "15337": "10.128.166.21", "15338": "10.128.167.21", "15339": "10.128.168.21",
            "15340": "10.128.169.21",
        }

        self.cpgdict = {
            # SEATED
            "15001": "10.128.33.2", "15002": "10.128.34.2", "15003": "10.128.35.2",
            "15004": "10.128.36.2", "15005": "10.128.37.2", "15006": "10.128.38.2",
            "15007": "10.128.39.2", "15008": "10.128.40.2", "15009": "10.128.41.2",
            "15010": "10.128.42.2", "15011": "10.128.43.2",
            # CLUB
            "15101": "10.128.65.2", "15102": "10.128.66.2", "15103": "10.128.67.2",
            "15104": "10.128.68.2", "15105": "10.128.69.2", "15106": "10.128.70.2",
            "15107": "10.128.71.2", "15108": "10.128.72.2", "15109": "10.128.73.2",
            "15110": "10.128.74.2",
        }

    def getCPG(self, coach):
        """
        Returns the CPG dictionary item for the argument coach.
        Will default to home 127.0.0.1 for case None.
        Will cast int arguments to strings.
        :param coach:
        :return self.cpgdict.get(coach):
        """
        if type(coach) is int:
            coach = str(coach)

        return self.cpgdict.get(coach)

    def getCPS(self, coach):
        """
        Returns the CPS dictionary item for the argument coach.
        Will default to home 127.0.0.1 for case None.
        Will cast int arguments to strings.
        :param coach:
        :return self.cpsdict.get(coach):
        """
        if type(coach) is int:
            coach = str(coach)

        return self.cpsdict.get(coach)

    def getLogs(self, coach):
        """
        Automatically downloads the log files from the remote /var/opt/logs folder.
        Utilises the ssh port 22 protocols.
        :param coach:
        :return none:
        """
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
            self.makeLogDir(coach)
            # This is a little bit of a hack. SCPClient doesn't allow you to pass a wild
            # character to the string, it just sees it as a literal character.
            # Sanitize gets around this with lambda magic.
            with SCPClient(client.get_transport(), sanitize=lambda x: x, progress=IPMan.progress) as scp:
                scp.get('/var/opt/logs/ASDO*', path)
            scp.close()
        except paramiko.ssh_exception.NoValidConnectionsError:
            print("Failed connection to " + str(coach))
            IPMan.writeToLogfile("Failed connection to " + str(coach))

    def getRake(self, coaches):
        """
        Grabs the logs for an entire coach rake by iterating through a list of coaches.
        :param coaches:
        :return none:
        """
        for coach in coaches:
            self.getLogs(coach)

    def makeCoachList(self, coaches):
        """
        Creates a list of coaches from the CPS list that are currently reachable.
        :param coaches:
        :return none:
        """
        coaches.clear()
        print("""
        
     _             _                         _   _   _
    | |_ _ __ __ _(_)_ __    ___ _ __   ___ | |_| |_(_)_ __   __ _
    | __| '__/ _` | | '_ \  / __| '_ \ / _ \| __| __| | '_ \ / _` |
    | |_| | | (_| | | | | | \__ \ |_) | (_) | |_| |_| | | | | (_| |_ _ _
     \__|_|  \__,_|_|_| |_| |___/ .__/ \___/ \__|\__|_|_| |_|\__, (_|_|_)
                                |_|                          |___/
     
        """)
        for coach in tqdm(self.cpsdict.keys()):
            if self.isCoachReachable(coach, self.getCPS(coach)):
                coaches.append(coach)
                IPMan.writeToLogfile("Downloaded: " + str(coach) + " at: " + str(self.getCPS(coach)))
    
    @staticmethod
    def makeLogDir(coach):
        """
        Attempts to make a directory for the current download session.
        Returns the new folder as a string is successful, else returns None.
        :param coach:
        :return none:
        """
        global path
        path = 'logs/' + str(coach) + '/' + str(time.strftime('%Y%m%d', time.localtime()))
        try:
            os.makedirs(path, exist_ok=True)
        except OSError:
            print('Creation of the directory %s has failed' % path)
            IPMan.writeToLogfile('Creation of the directory %s has failed' % path)
        else:
            print('Successfully uploaded logs to %s ' % path)
            IPMan.writeToLogfile('Successfully uploaded logs to %s ' % path)

    @staticmethod
    def isCoachReachable(coachNumber, coachIP):
        """
        Returns true if coach is currently reachable.
        :param coachNumber:
        :param coachIP:
        :return boolean:
        """
        response = not subprocess.call('ping -n 1 -w 100 ' + str(coachIP), stdout=subprocess.PIPE)
        if response:
            IPMan.writeToLogfile(str(coachNumber) + " contact confirmed at " + str(coachIP))
        else:
            IPMan.writeToLogfile(str(coachNumber) + " unreachable at " + str(coachIP))
        return response

    @staticmethod
    def writeToLogfile(logString):
        """
        Writes to a logfile named ASDOMan_logfile.txt.
        :param logString:
        :return none:
        """
        f = open("ASDOMan_logfile.txt", "a")
        f.write(str(datetime.datetime.utcnow().strftime("%b%d-%H:%M:%S.%f")[:-4]) + " " + logString + "\n")
        f.close()

    @staticmethod
    def progress(filename, size, sent):
        """
        Define progress callback that prints the current percentage completed for the file
        :param filename:
        :param size:
        :param sent:
        :return none:
        """
        sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent) / float(size) * 100))


def main():
    """
    Instantiates a class object of type IPMan and makes a list of ping-able coaches.
    Using this list, each coach is then sent an SCP protocol to download the logs from the
    root@COACH_IP_ADDRESS:/var/opt/logs folder and save them to the local machine.
    :return:
    """
    global coachList
    getRakeLogs = IPMan()
    getRakeLogs.makeCoachList(coachList)
    if coachList:
        print("""
                             _                                 _      _
     ___  ___  __ _ _ __ ___| |__     ___ ___  _ __ ___  _ __ | | ___| |_ ___
    / __|/ _ \/ _` | '__/ __| '_ \   / __/ _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \
    \__ \  __/ (_| | | | (__| | | | | (_| (_) | | | | | | |_) | |  __/ ||  __/
    |___/\___|\__,_|_|  \___|_| |_|  \___\___/|_| |_| |_| .__/|_|\___|\__\___|
                                                        |_|
        """)
        print('Found: ' + ', '.join(coachList))
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
               ASDO Man Version 2.1 Panda Distro 
            Author: Ben McGuffog, Technical Engineer

        """)
        print('****** Logs gathered for: ' + ', '.join(coachList))
    else:
        print("""
        
        
        
        
        
                                          _.---**""**-.       
                                  ._   .-'           /|`.     
                                   \`.'             / |  `.   
                                    V              (  ;    \  
                                    L       _.-  -. `'      \ 
                                   / `-. _.'       \         ;
        YOU HAVE ANGERED ASDO MAN :            __   ;    _   |
         ARE YOU EVEN CONNECTED   :`-.___.+-*"': `  ;  .' `. |
              TO THE TRAIN?       |`-/     `--*'   /  /  /`.\|
                         \        : :              \    :`.| ;
                          \       | |   .           ;/ .' ' / 
                                  : :  / `             :__.'  
                                   \`._.-'       /     |      
                                    : )         :      ;      
                                    :----.._    |     /       
                                   : .-.    `.       /        
                                    \     `._       /         
                                    /`-            /          
                                   :             .'           
                                    \ )       .-'             
                                     `-----*"'     
                                     
        Try connecting to T2 on the Train Switch or directly to the CPS.
        Try setting your IP address to 10.128.33.10, MASK: 255.224.0.0
        Try setting your IP address to automatic.
        
        """)

    input("Press any key to exit")


if __name__ == "__main__":
    main()
