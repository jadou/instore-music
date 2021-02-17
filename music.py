#!/usr/bin/python

from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
import socket
import math
import os

MUSIC_STREAM = 'http://31.24.224.22/proxy/storetunes_urbanfash?mp=/stream'
GAP = 600 #in seconds

hostname = socket.gethostname()
print(hostname)
local_ip = socket.gethostbyname(hostname)
print(local_ip)

dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, 'announce')

def main():
    try:
        print("Starting main")
        announcements = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        player = OMXPlayer(MUSIC_STREAM, args='--no-keys -o local', dbus_name='org.mpris.MediaPlayer2.omxplayer1')
        print("Playing %s" % MUSIC_STREAM)
        player.set_volume(1)
        if announcements:
            while True:
                for announce in announcements:
                    for n in range(GAP):
                        if not player.is_playing():
                            raise Exception("Not playing...")
                        sleep(1)
                    player.set_volume(0.8)
                    sleep(1)
                    player.set_volume(0.6)
                    sleep(1)
                    player.set_volume(0.4)
                    sleep(1)
                    player.set_volume(0.2)
                    sleep(1)
                    player.set_volume(0)
                    player_announce = OMXPlayer(os.path.join(path, announce), args='--no-keys -o local', dbus_name='org.mpris.MediaPlayer2.omxplayer2')
                    player_announce.set_volume(1)
                    duration = int(math.ceil(player_announce.duration()))
                    sleep(duration)
                    player_announce.quit()
                    player.set_volume(0.2)
                    sleep(1)
                    player.set_volume(0.4)
                    sleep(1)
                    player.set_volume(0.6)
                    sleep(1)
                    player.set_volume(0.8)
                    sleep(1)
                    player.set_volume(1)
    except:
        try:
            player.quit()
        except:
            pass
        print("Exception")
        main()

if __name__ == '__main__':
    main()