# https://github.com/dannyvoid/VPN-Killswitch
# How to deploy 7.2.2020
# Open Task Scheduler with Admin and Create Task and Import Kill Switch.xml
# it's ideal to put this script in 
# C:\Windows\System32\drivers\etc
# where only admin can edit/delete

import os
import os.path
import socket
import subprocess
import time
import ctypes

from datetime import datetime
from requests import get
from apscheduler.schedulers.background import BackgroundScheduler

adapter_vpn = 'Local Area Connection'   # name of vpn adapter (should be Local Area Connection, not ethernet!)
adapter_wifi = 'Wi-Fi 2'                # name of your primary network adaptor (most likely wifi)
socket_url = 'www.google.com'           # don't change
# https gets rejected in mitm - handshake fail, need to allow pass through
ip_url = 'http://api.ipify.org'         # don't change
int_is_vpn = 30                         # interval in seconds to check your vpn state
int_is_stuck = 30                       # interval in minutes to check if your machine needs to reboot
auto_reboot = False                     # restarts machine if offline for an extended period
auto_start = False                      # starts VPN-Killswitch on windows startup
debug = False                           # prints your IP on each check

# server ip prefix
vpn_prefix = ['34.72']

def is_online():
    try:
        socket.create_connection((socket_url, 80))
        return True
    except Exception:
        pass
    return False

# ***
def is_vpn():

    if is_online():

        try:

            # api call
            ip = get(ip_url).text

            if ip.startswith(tuple(vpn_prefix)):

                print('{} - {} - VPN Working!'.format(str(datetime.now()),ip))

                if debug:

                    print('{} - {}'.format(str(datetime.now()), ip))
                
            else:

                print('{} - {} - VPN Not Detected! Kill Wifi.'.format(str(datetime.now()), ip))

                subprocess.call('Netsh WLAN disconnect interface="{}"'.format(adapter_wifi), stdout=open(os.devnull, 'wb'))
               
                if debug:

                    print('{} - {}'.format(str(datetime.now()), ip))

        except Exception:

            print('exception')
            pass

    else:

        print('{} - Network Offline!'.format(str(datetime.now())))
# ***

def is_stuck():
    if auto_reboot:
        if not is_online:
            print('{} - Machine has been offline for {} minutes.'.format(str(datetime.now()), str(int_is_stuck)))
            print('{} - Rebooting in 60 seconds!'.format(str(datetime.now())))
            subprocess.call('shutdown -t 60 -r -f', stdout=open(os.devnull, 'wb'))
        else:
            print('{} - Checking for errors again in {} minutes.'.format(str(datetime.now()), str(int_is_stuck)))
            pass
    else:
        pass


def startup_management():
    startup_dir = 'C:/Users/{}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup'.format(os.getlogin())
    startup_file = os.path.join(startup_dir, 'VPN-Killswitch.bat')

    if auto_start:
        delete_file(startup_file)

        with open(startup_file, 'w') as batch:
            batch_file = (
                '@echo off\n\n'

                'net session >nul\n'
                'REM if %errorlevel% neq 0 goto elevate >nul\n'
                'goto :start\n\n'

                ':elevate\n'
                'cd /d %~dp0\n'
                'mshta \"javascript: var shell = new ActiveXObject(\'shell.application\');'
                'shell.ShellExecute(\'%~nx0\', \'\', \'\', \'runas\', 1);close();\" >nul\n'
                'exit\n\n'

                ':start\n'
                'cd /d "{}"\n'
                'ping -n 30 -w 1 127.0.0.1>nul\n'
                'python kill.py\n\n'.format(os.getcwd())
            )
            batch.write('{}'.format(batch_file))
    else:
        delete_file(startup_file)


def delete_file(file):
    try:
        os.remove(file)
    except OSError:
        pass


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(is_vpn, 'interval', seconds=int_is_vpn, coalesce=True)
    scheduler.add_job(is_stuck, 'interval', minutes=int_is_stuck)
    scheduler.start()

    print('############################')
    print('###  VPN-Killswitch 2.5  ###')
    print('### Created by DannyVoid ###')
    print('### edit by ap27 6.25.20 ###')
    print('############################')
    print('\nStarted at {}'.format(str(datetime.now())))
    print('-------------------------------------\n')

    startup_management()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()