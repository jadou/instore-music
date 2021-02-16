#!/usr/bin/python

from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
import socket
import math
import os

MUSIC_STREAM = 'http://31.24.224.22/proxy/storetunes_urbanfash?mp=/stream'
GAP = 600 #in seconds
REMOTE_SERVER = '1.1.1.1'

dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, 'announce')

def is_connected(hostname):
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80), 4)
        s.close()
        return True
    except:
        pass
    print("No internet connection.")
    return False

def main():
    if is_connected(REMOTE_SERVER):
        try:
            player.quit()
        except:
            pass
        print("im here")
        announcements = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        player = OMXPlayer(MUSIC_STREAM, args='--no-keys -o local', dbus_name='org.mpris.MediaPlayer2.omxplayer1')
        print("Playing %s" % MUSIC_STREAM)
        player.set_volume(1)
        if announcements:
            announce(announcements, player)

    else:
        print("Not connected to the internet. Retrying in 5 seconds.")
        sleep(5)
        main()

def announce(a, p, t=0):
    try:
        if t < GAP:
            if is_connected(REMOTE_SERVER):
                t += 1
                sleep(1)
                announce(a, p, t)
            else:
                p.quit()
                print("from GAP")
                main()
        for i in a:
            p.set_volume(0.8)
            sleep(1)
            p.set_volume(0.6)
            sleep(1)
            p.set_volume(0.4)
            sleep(1)
            p.set_volume(0.2)
            sleep(1)
            p.set_volume(0)
            player_announce = OMXPlayer(os.path.join(path, i), args='--no-keys -o local', dbus_name='org.mpris.MediaPlayer2.omxplayer2')
            player_announce.set_volume(1)
            duration = int(math.ceil(player_announce.duration()))
            sleep(duration)
            player_announce.quit()
            p.set_volume(0.2)
            sleep(1)
            p.set_volume(0.4)
            sleep(1)
            p.set_volume(0.6)
            sleep(1)
            p.set_volume(0.8)
            sleep(1)
            p.set_volume(1)
            sleep(GAP)
        announce(a, p)
    except:
        print("from announce except")
        main()

if __name__ == '__main__':
    print("started")
    main()