#!/usr/bin/python

from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
import math
import commands
import os

MUSIC_STREAM = 'https://uop.link/in-store-music-finland'
GAP = 600 #in seconds

os.system('sudo shutdown -r 23:00')
hostname = commands.getoutput('hostname -I')
h_split = hostname.split()
i_split = h_split[0].split('.')
country = 'sweden'
if i_split[1] == '7':
    country = 'finland'

dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, os.path.join('announce', country))

def main():
    try:
        print("Starting player...")
        announcements = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        player = OMXPlayer(MUSIC_STREAM, args='--no-keys -o local', dbus_name='org.mpris.MediaPlayer2.omxplayer1')
        print("Playing %s" % MUSIC_STREAM)
        player.set_volume(1)
        if announcements:
            print("Announcements found for %s" % country)
            while True:
                for announce in announcements:
                    for n in range(GAP):
                        if not player.is_playing():
                            print("Player not playing. Restarting")
                            raise Exception("Player not playing. Restarting")
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
        else:
            print("No announcements found for %s" % country)
    except:
        try:
            player.quit()
        except:
            pass
        print("Exception")
        main()

if __name__ == '__main__':
    main()