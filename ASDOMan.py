import sys
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import os
import time
import datetime
from tqdm import tqdm
import subprocess
import gzip


class DownloadManager:
    """
    Class DownloadManager is our ancient hero who downloads remote log files from the list of "coaches" sent to it.
    Using mad python KungFu style object programming, together we can overcome the laborious task of log downloads!

    Author:     Ben McGuffog, Support Engineer
    Version:    2021-Jan

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
            # TEST
            # "pi": "172.24.22.246",
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

        self.HMIdict = {
            # SEATED
            "15001": "10.128.33.2", "15002": "10.128.34.2", "15003": "10.128.35.2",
            "15004": "10.128.36.2", "15005": "10.128.37.2", "15006": "10.128.38.2",
            "15007": "10.128.39.2", "15008": "10.128.40.2", "15009": "10.128.41.2",
            "15010": "10.128.42.2", "15011": "10.128.43.2",
        }

        self.CPGKeyList = self.cpgdict.keys()
        self.localCPGList = list()
        self.path = str()
        self.viableCoachList = list()

    def getCPGAddress(self, coach):
        """
        Returns the CPG dictionary item for the argument coach.
        Will cast int arguments to strings.
        :param coach:
        :return self.cpgdict.get(coach):
        """
        if type(coach) is int:
            coach = str(coach)

        return self.cpgdict.get(coach)

    def getCPSAddress(self, coach):
        """
        Returns the CPS dictionary item for the argument coach.
        Will cast int arguments to strings.
        :param coach:
        :return self.cpsdict.get(coach):
        """
        if type(coach) is int:
            coach = str(coach)

        return self.cpsdict.get(coach)

    def getHMIAddress(self, coach):
        """
        Returns the CPG dictionary item for the argument coach.
        Will cast int arguments to strings.
        :param coach:
        :return self.HMIdict.get(coach):
        """
        if type(coach) is int:
            coach = str(coach)
        return self.HMIdict.get(coach)

    def getCPGList(self):
        """
        Getter for CPGKeyList
        :return self.CPGKeyList:
        """
        return self.CPGKeyList

    def getViableCoachList(self):
        """
        Getter for viableCoachList
        :return self.viableCoachList:
        """
        return self.viableCoachList

    def getPath(self):
        """
        Getter for path
        :return self.path:
        """
        return self.path

    def getLocalCPGList(self):
        """
        Getter for localCPGList
        :return self.localCPGList:
        """
        return self.localCPGList

    def setLocalCPGList(self, newList):
        """
        Sets the list variable self.localCPGList to a list of seated and
        club coaches that are currently on the local network.
        """
        self.localCPGList = list([x for x in newList if x in self.getCPGList()])

    def setPath(self, localPath):
        """
        Sets the list variable self.localCPGList to a list of seated and
        club coaches that are currently on the local network.
        """
        self.path = str(localPath)

    def clearViableCoachList(self):
        """
        Setter for the viableCoachList
        :return:
        """
        self.getViableCoachList().clear()

    def setViableCoachList(self, newCoach):
        """
        Setter for the viableCoachList
        :return:
        """
        self.getViableCoachList().append(newCoach)

    def getRemoteLogs(self, coach, remotePath, username, password, host, CPS=True):
        """
        Automatically downloads the log files from the remotePath folder.
        Utilises the ssh port 22 protocols.
        :param coach: The coach key for the dictionary lookup
        :param remotePath: Path for the remote logs
        :param username: Username for the remote host
        :param password: Password for the remote host
        :param host: Host IP address
        :param CPS: Defaults to True. Set to False for CPG downloads.
        :return: None
        """
        port = 22
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Attempt a scp connection to the host and get the logs for coach
        try:
            client.connect(host, port, username, password)
            self.makeLogDir(coach)
            # This is a little bit of a hack. SCPClient doesn't allow you to pass a wild
            # character to the string, it just sees it as a literal character.
            # Sanitize gets around this with lambda magic. Not sure why it needs Lambda to return the same variable.
            # https://stackoverflow.com/questions/47926123/using-wildcards-in-file-names-using-pythons-scpclient-library
            with SCPClient(client.get_transport(), sanitize=lambda x: x, progress=DownloadManager.progress) as scp:
                scp.get(remotePath, self.getPath())
            scp.close()
        except paramiko.ssh_exception.NoValidConnectionsError:
            print("Failed connection to " + str(coach))
            DownloadManager.writeToLogfile("Failed connection to " + str(coach))

        # Filter out the error logs by calling lineFilter
        if CPS:
            try:
                for logFile in os.listdir(self.getPath()):
                    if logFile.endswith('gz'):
                        self.lineFilter(logFile, True)
                    else:
                        self.lineFilter(logFile, False)
            except OSError:
                print("something went terribly wrong")
                pass

    def getRake(self, coaches, remoteDir, username, password, CPS):
        """
        Iterates through a list of coaches and calls the getLogs for each.
        :param password: The password for the remote host
        :param username: The username for the remote host
        :param remoteDir: The directory of the remote host logs
        :param coaches: The list of coaches to download from
        :param CPS: uses CPS list when true, else CPG list
        :return none:
        """
        for coach in coaches:
            if CPS:
                self.getRemoteLogs(coach, remoteDir, username, password, host=self.getCPSAddress(coach), CPS=True)
            else:
                print(self.getCPGAddress(coach))
                self.getRemoteLogs(coach, remoteDir, username, password, host=self.getCPGAddress(coach), CPS=False)

    def makeCoachList(self):
        """
        Creates a list of coaches from the CPS list that are currently reachable.
        :return none:
        """
        self.clearViableCoachList()

        print("""
        
        ________                _____                                 _____ _____ _____                  
        ___  __/______________ ____(_)_______ ________________ ______ __  /___  /____(_)_______ _______ _
        __  /   __  ___/_  __ `/__  / __  __ \__  ___/___  __ \_  __ \_  __/_  __/__  / __  __ \__  __ `/
        _  /    _  /    / /_/ / _  /  _  / / /_(__  ) __  /_/ // /_/ // /_  / /_  _  /  _  / / /_  /_/ / 
        /_/     /_/     \__,_/  /_/   /_/ /_/ /____/  _  .___/ \____/ \__/  \__/  /_/   /_/ /_/ _\__, /  
                                                      /_/                                       /____/   

     
        """)
        for coach in tqdm(self.cpsdict.keys()):
            if self.isCoachReachable(coach, self.getCPSAddress(coach)):
                self.setViableCoachList(coach)
                DownloadManager.writeToLogfile("Downloaded: " + str(coach) + " at: " + str(self.getCPSAddress(coach)))
        os.system('cls')

    def downloadHelper(self):
        self.getRake(self.getViableCoachList(), remoteDir='/var/opt/logs/ASDO*', username='root',
                     password='root', CPS=True)
        self.setLocalCPGList(self.getViableCoachList())
        self.getRake(self.getLocalCPGList(), remoteDir='/var/opt/asdo_hmi/log/asdo_hmi*', username='root',
                     password='root', CPS=False)

    def lineFilter(self, file, compressed):
        """
        Grabs a file and depending on whether or not its gzipped, will filter through
        and pullout all of the PTI and error lines.
        """
        fileLocation = (self.getPath() + '/' + file)
        errorLog = (self.getPath() + '/' + 'filtered_log.txt')
        logfile = open(errorLog, 'a')

        # Setup the open protocol
        if compressed:
            openIt = gzip.open
        else:
            openIt = open

        with openIt(fileLocation, 'rt') as log:
            for line in log:
                if 'error' in line or 'PTI' in line:
                    try:
                        logfile.write(line)
                    except OSError:
                        print("Failed to write to: " + errorLog)
        logfile.close()

    def makeLogDir(self, coach):
        """
        Attempts to make a directory for the current download session.
        Returns the new folder as a string is successful, else returns None.
        :param coach:
        :return none:
        """
        self.setPath('logs/' + str(coach) + '/' + str(time.strftime('%Y%m%d', time.localtime())))
        try:
            os.makedirs(self.getPath(), exist_ok=True)
        except OSError:
            print('Creation of the directory %s has failed' % self.getPath())
            DownloadManager.writeToLogfile('Creation of the directory %s has failed' % self.getPath())
        else:
            print('Successfully uploaded logs to %s ' % self.getPath())
            DownloadManager.writeToLogfile('Successfully uploaded logs to %s ' % self.getPath())

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
            DownloadManager.writeToLogfile(str(coachNumber) + " contact confirmed at " + str(coachIP))
        else:
            DownloadManager.writeToLogfile(str(coachNumber) + " unreachable at " + str(coachIP))
        return response

    @staticmethod
    def writeToLogfile(logString):
        """
        Writes to a logfile named ASDOMan_logfile.txt.
        :param logString:
        :return none:
        """
        try:
            f = open("ASDOMan_logfile.txt", "a")
            f.write(str(datetime.datetime.utcnow().strftime("%b%d-%H:%M:%S.%f")[:-4]) + " " + logString + "\n")
            f.close()
        except OSError:
            print("Failed to write to ASDOMan_logfile.txt")
            pass

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
    Instantiates a class object of type DownloadManager and makes a list of ping-able coaches.
    Using this list, each coach is then sent an SCP protocol to download the logs from the
    root@COACH_IP_ADDRESS:/var/opt/logs folder and save them to the local machine.
    :return:
    """

    getRakeLogs = DownloadManager()
    getRakeLogs.makeCoachList()
    if getRakeLogs.getViableCoachList():
        print('Search complete. Found: ' + ', '.join(getRakeLogs.getViableCoachList()))
        print("""
        ________                           ______               ______________
        ___  __ \______ ___      _________ ___  /______ ______ _______  /___(_)_______ _______ _
        __  / / /_  __ \__ | /| / /__  __ \__  / _  __ \_  __ `/_  __  / __  / __  __ \__  __ `/
        _  /_/ / / /_/ /__ |/ |/ / _  / / /_  /  / /_/ // /_/ / / /_/ /  _  /  _  / / /_  /_/ /
        /_____/  \____/ ____/|__/  /_/ /_/ /_/   \____/ \__,_/  \__,_/   /_/   /_/ /_/ _\__, /
                                                                                       /____/


        """)

        getRakeLogs.downloadHelper()

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
               ASDO Man Version 4.0b Panda Distro 
            Author: Ben McGuffog, Support Engineer

        """)
        print('****** Logs gathered for: ' + ', '.join(getRakeLogs.getViableCoachList()))
    else:
        print("""
        
        
        
        
        Ψσυ нλvε λπɢεгεd ΔЅDΘ ϻλπ!
                                          _.---**""**-.       
                                  ._   .-'           /|`.     
                                   \`.'             / |  `.   
                                    V              (  ;    \  
                                    L       _.-  -. `'      \ 
                                   / `-. _.'       \         ;
                                  :            __   ;    _   |
         Are you even connected   :`-.___.+-*"': `  ;  .' `. |
              to the train?       |`-/     `--*'   /  /  /`.\|
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
        
        Try connecting to T2 of the Train Switch or directly to the CPS
        Try setting your IP address to 10.128.33.10, mask 255.224.0.0
        Try setting you IP address to automatic. 
        
        """)

    input("Press Enter key to exit")


if __name__ == "__main__":
    main()
