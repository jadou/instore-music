#!/usr/bin/python

from mplayer import Player
from pathlib import Path
from time import sleep
import math, commands, os, sys, json, urllib

#https://uop.link/in-store-music
#MUSIC_STREAM = 'http://31.24.224.22/proxy/storetunes_hipsterp?mp=/stream'
#https://uop.link/in-store-music-alt
#ALT_MUSIC_STREAM = 'http://19293.live.streamtheworld.com/SP_R3449667_SC'
GAP = 600 #in seconds

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
sys.stdout.flush()
dir_path = os.path.dirname(os.path.realpath(__file__))
announcements_path = os.path.join(dir_path, os.path.join('announce', country))
alt_music_list_path = os.path.join(dir_path, 'alt_music_list.txt')

def main():
    try:
        print("Selecting stream...")
        sys.stdout.flush()
        if os.path.isfile(alt_music_list_path):
            alt_music_list_file = open(alt_music_list_path, 'r')
            alt_music_list = [f.strip() for f in alt_music_list_file.readlines()]
            print("Alternative list available")
            sys.stdout.flush()
        else:
            alt_music_list = []
        if store in alt_music_list:
            CODE = 'f6403f66f656451f8fcbf4b4fe881d9b'
        else:
            CODE = '79c6519c9d1b46fc8d6d341d92f4eb4d'
        CURL = commands.getoutput("curl -s 'https://api.rebrandly.com/v1/links/%s' -H 'apikey: 77a44fcac24946679e800fadc4f84958'" % CODE)
        JSON = json.loads(CURL)
        STREAM = JSON["destination"]
        print("Checking stream...")
        sys.stdout.flush()
        if int(urllib.urlopen(STREAM).getcode()) != 200:
            raise Exception("Stream not available. Restarting")
        print("Starting player...")
        sys.stdout.flush()
        player = Player(args=('-ao alsa:device=hw=1.0'))
        player.loadfile(STREAM)
        print("Playing %s" % STREAM)
        sys.stdout.flush()
        print("Checking for announcements...")
        sys.stdout.flush()
        if os.path.exists(announcements_path):
            announcements = [f for f in os.listdir(announcements_path) if not f.startswith('.') and os.path.isfile(os.path.join(announcements_path, f))]
        else:
            announcements = []
        if announcements:
            print("Announcements found for %s" % country)
            sys.stdout.flush()
            print("Waiting for cache. Sleeping for 2 mins")
            sys.stdout.flush()
            sleep(120)
            while True:
                for announce in announcements:
                    for n in range(GAP):
                        if not player.is_alive():
                            raise Exception("Player not playing. Restarting")
                        if player.filename is None:
                            raise Exception("No internet connected. Restarting")
                        sleep(1)
                    player.pause()
                    player_announce = Player(os.path.join(announcements_path, announce))
                    sleep(1)
                    duration = int(math.ceil(player_announce.length)) - 1
                    sleep(duration)
                    player_announce.quit()
                    player.pause()
        else:
            print("No announcements found for %s" % country)
            sys.stdout.flush()
            print("Waiting for cache. Sleeping for 2 mins")
            sys.stdout.flush()
            sleep(120)
            while True:
                if not player.is_alive():
                    raise Exception("Player not playing. Restarting")
                if player.filename is None:
                    raise Exception("No internet connected. Restarting")
                sleep(1)
    except Exception as e:
        try:
            player.quit()
        except:
            pass
        print(e)
        sys.stdout.flush()
        main()

if __name__ == '__main__':
    main()
