#!/bin/bash

on_success="DONE"
on_fail="FAIL"
white="\e[1;37m"
green="\e[1;32m"
red="\e[1;31m"
blue="\e[1;34m"
nc="\e[0m"

function _spinner() {
    case $1 in
        start)
            let column=$(tput cols)-${#2}-8
            echo -ne ${2}
            printf "%${column}s"
            i=1
            sp='\|/-'
            delay=${SPINNER_DELAY:-0.15}
            while :
            do
                printf "\b${sp:i++%${#sp}:1}"
                sleep $delay
            done
            ;;
        stop)
            if [[ -z ${3} ]]; then
                #echo "spinner is not running.."
                exit 1
            fi
            kill $3 > /dev/null 2>&1
            echo -en "\b["
            if [[ $2 -eq 0 ]]; then
                echo -en "${green}${on_success}${nc}"
            else
                echo -en "${red}${on_fail}${nc}"
            fi
            echo -e "]"
            ;;
        *)
            #echo "invalid argument, try {start/stop}"
            exit 1
            ;;
    esac
}

function start_spinner {
    _spinner "start" "${blue}${1}${nc}" &
    _sp_pid=$!
    disown
}

function stop_spinner {
    _spinner "stop" $1 $_sp_pid
    unset _sp_pid
}

function exitc {
	stop_spinner $?
    echo -en "\n${red}Exited${nc}\n"
    exit;
}

trap exitc INT

device=$(hostname -I)
curl -k -X POST -F "started=${device}" https://app-dev.uropenn.se/updatemusicbox/index.php > /dev/null 2>&1;

sudo sed -i 's/raspberrypi/raspberry/g' /etc/hosts
sudo bash -c 'echo -e "
      __   __   __   ___
|  | |__) /  \ |__) |__  |\ | |\ |
\__/ |  \ \__/ |    |___ | \| | \|
            __          ___            ___ ___  ___
 |\/| |  | /__\` | |__/ |__  |\ | |__| |__   |  |__  |\ |
 |  | \__/ .__/ | |  \ |___ | \| |  | |___  |  |___ | \|

" > /etc/motd' > /dev/null 2>&1;

start_spinner "Updating apt sources"
sudo apt update > /dev/null 2>&1;
stop_spinner $?
start_spinner "Removing Raspberry Pi GUI"
sudo apt -y remove --purge x11-common plymouth > /dev/null 2>&1;
sudo systemctl stop gldriver-test.service > /dev/null 2>&1;
sudo systemctl disable gldriver-test.service > /dev/null 2>&1;
if grep -q "splash" /boot/cmdline.txt ; then
    sudo sed -i /boot/cmdline.txt -e "s/ quiet//"
    sudo sed -i /boot/cmdline.txt -e "s/ splash//"
    sudo sed -i /boot/cmdline.txt -e "s/ plymouth.ignore-serial-consoles//"
fi
if [[ -d "/home/pi/Desktop" ]]; then
    rm -R /home/pi/Desktop > /dev/null 2>&1;
    rm -R /home/pi/Documents > /dev/null 2>&1;
    rm -R /home/pi/Downloads > /dev/null 2>&1;
    sudo rm -R /home/pi/ftp > /dev/null 2>&1;
    rm -R /home/pi/MagPi > /dev/null 2>&1;
    rm -R /home/pi/Music > /dev/null 2>&1;
    rm -R /home/pi/Pictures > /dev/null 2>&1;
    rm -R /home/pi/Public > /dev/null 2>&1;
    rm -R /home/pi/Templates > /dev/null 2>&1;
    rm -R /home/pi/Videos > /dev/null 2>&1;
fi
stop_spinner $?
start_spinner "Updating Raspberry Pi"
sudo apt -y full-upgrade > /dev/null 2>&1;
stop_spinner $?
start_spinner "Installing dependencies"
sudo apt -y install git ufw omxplayer libdbus-1-dev libglib2.0-dev python-pip python-alsaaudio build-essential zlib1g-dev libssl-dev libpam0g-dev libselinux1-dev > /dev/null 2>&1;
pip install omxplayer-wrapper pathlib > /dev/null 2>&1;
stop_spinner $?
start_spinner "Enabling firewall and allow only 22/ssh"
sudo ufw allow 22 > /dev/null 2>&1;
sudo ufw --force enable > /dev/null 2>&1;
sudo ufw limit ssh/tcp > /dev/null 2>&1;
stop_spinner $?
start_spinner "Disabling auto login"
sudo systemctl set-default multi-user.target > /dev/null 2>&1;
sudo ln -fs /lib/systemd/system/getty@.service /etc/systemd/system/getty.target.wants/getty@tty1.service > /dev/null 2>&1;
if [[ -f "/etc/systemd/system/getty@tty1.service.d/autologin.conf" ]]; then
    sudo rm /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null 2>&1;
fi
stop_spinner $?
start_spinner "Disabling bluetooth"
grep -qxF 'dtoverlay=disable-bt' /boot/config.txt || sudo bash -c 'echo "dtoverlay=disable-bt" >> /boot/config.txt' > /dev/null 2>&1;
sudo systemctl disable hciuart.service > /dev/null 2>&1;
sudo systemctl disable bluetooth.service > /dev/null 2>&1;
stop_spinner $?
start_spinner "Removing uneccessary packages"
sudo apt -y remove --purge vsftpd > /dev/null 2>&1;
sudo apt -y autoremove > /dev/null 2>&1;
sudo apt -y autoclean > /dev/null 2>&1;
grep -qxF 'net.ipv4.tcp_timestamps = 0' /etc/sysctl.conf || sudo bash -c 'echo "net.ipv4.tcp_timestamps = 0" >> /etc/sysctl.conf' && sudo sysctl -p > /dev/null 2>&1;
stop_spinner $?
#start_spinner "Setting volume to 80%"
#sudo amixer -q -M sset 'Headphone' 80% > /dev/null 2>&1
#stop_spinner $?
start_spinner "Creating service"
if [[ ! -f "/etc/systemd/system/instore_music.service" ]]; then
    sudo bash -c 'echo -e "
[Unit]
Description=Play in-store music
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=pi
ExecStart=/usr/bin/python /home/pi/instore-music/music.py

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/instore_music.service' > /dev/null 2>&1;
    sudo systemctl enable instore_music > /dev/null 2>&1;
    #sudo systemctl start instore_music > /dev/null 2>&1;
fi
stop_spinner $?
start_spinner "Updating OpenSSH"
cd /home/pi
wget -c https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-8.4p1.tar.gz > /dev/null 2>&1;
tar -xzf openssh-8.4p1.tar.gz > /dev/null 2>&1;
cd openssh-8.4p1/
./configure --with-md5-passwords --with-pam --with-selinux --with-privsep-path=/var/lib/sshd/ --sysconfdir=/etc/ssh > /dev/null 2>&1;
make > /dev/null 2>&1;
sudo make install > /dev/null 2>&1;
sudo rsync -avP /usr/local/sbin/sshd /usr/sbin/sshd > /dev/null 2>&1;
sudo rsync -avP /usr/local/bin/ssh /usr/bin/ssh > /dev/null 2>&1;
cd /home/pi
rm /home/pi/openssh-8.4p1.tar.gz
rm -R /home/pi/openssh-8.4p1
stop_spinner $?
start_spinner "Restarting in 5 secs (CTRL + C to cancel)"
curl -k -X POST -F "done=${device}" https://app-dev.uropenn.se/updatemusicbox/index.php > /dev/null 2>&1;
sleep 1
stop_spinner $?
sleep 5
sudo reboot