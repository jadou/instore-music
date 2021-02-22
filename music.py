#!/usr/bin/python

from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
import math
import commands
import os

MUSIC_STREAM = 'https://uop.link/in-store-music'
ALT_MUSIC_STREAM = 'http://19293.live.streamtheworld.com/SP_R3449667_SC'
GAP = 600 #in seconds

os.system('sudo shutdown -r 23:00')
hostname = commands.getoutput('hostname -I')
h_split = hostname.split()
i_split = h_split[0].split('.')
country = 'sweden'
if i_split[1] == '7':
    country = 'finland'
store_start = 'FI6' if i_split[1] == '7' else i_split[1]
store_end = '%02d' % (int(i_split[2]))
store = store_start + store_end
print("Detected store: %s" % (store))
dir_path = os.path.dirname(os.path.realpath(__file__))
announcements_path = os.path.join(dir_path, os.path.join('announce', country))
alt_music_list_path = os.path.join(dir_path, 'alt_music_list.txt')

announcements = []
alt_music_list = []

def main():
    global announcements
    try:
        print("Starting player...")
        print("Selecting stream...")
        if os.path.exists(alt_music_list_path) and os.path.isfile(alt_music_list_path):
            alt_music_list_file = open(alt_music_list_path, 'r')
            alt_music_list = [f.strip() for f in alt_music_list_file.readlines()]
        if store in alt_music_list:
            STREAM = ALT_MUSIC_STREAM
        else:
            STREAM = MUSIC_STREAM
        player = OMXPlayer(STREAM, args='--no-keys -o local', dbus_name='org.mpris.MediaPlayer2.omxplayer1')
        print("Playing %s" % STREAM)
        player.set_volume(1)
        print("Checking for announcements...")
        if os.path.exists(announcements_path):
            announcements = [f for f in os.listdir(announcements_path) if not f.startswith('.') and os.path.isfile(os.path.join(announcements_path, f))]
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
                    player_announce = OMXPlayer(os.path.join(announcements_path, announce), args='--no-keys -o local', dbus_name='org.mpris.MediaPlayer2.omxplayer2')
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