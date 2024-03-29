#!/bin/bash

cat << EOF > /home/pi/.asoundrc
pcm.!default {
  type asym
  playback.pcm {
    type plug
    slave.pcm "output"
  }
  capture.pcm {
    type plug
    slave.pcm "input"
  }
}

pcm.output {
  type hw
  card 1
}

ctl.!default {
  type hw
  card 1
}
EOF
amixer set Headphone 96%