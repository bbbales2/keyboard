Introduction
============

This is a prototype touchpad keyboard.

The idea is you should be able to type messages on a touchpad even if the letters themselves aren't visible on that touchpad.

My issue with touch typing interfaces is the regular typing ones make you press actual key buttons on a screen. I think touch typing interfaces should be more liberal about applying spellchecking/word replacement technology.

I get that this doesn't work everywhere (for instance, typing urls where things can be mispelled and stuff), but a lot of my typing on touchscreens is just quick e-mails to my family or dumb messages to my friends. I don't need precision. I just need some speed and a half-assed interface and they can figure out the rest.

I prototyped this up on my Ubuntu laptop in hopes of eventually using the technology on a Steam controller.

Using
=============

You'll need a laptop running a Linux distribution with a touchpad that supports absolute input mode. I install all my pip packages with --user so I don't screw up system stuff. You can do whatever you want.

evdev
-------------

You'll need to install the Python evdev libraries

    pip install --user evdev

To actually configure your trackpad, you'll need to add the line

    Option "Mode" "Absolute"

to your xorg.conf file. Ubuntu 14.04 just concatenates everything in /etc/X11/xorg.conf.d together as an xorg.conf.d file (https://wiki.ubuntu.com/X/Config). For me I edited the bit of /usr/share/X11/xorg.conf.d/10-evdev.conf labeled "touchpad" to look like:

    Section "InputClass"
            Identifier "evdev touchpad catchall"
            MatchIsTouchpad "on"
            MatchDevicePath "/dev/input/event*"
            Driver "evdev"
            Option "Mode" "Absolute"
    EndSection

I also moved the files /etc/X11/xorg.conf.d/50-synaptics.conf and /etc/X11/xorg.conf.d/51-synaptics-quirks.conf out of the directory. After you do this you'll need to restart X11. The easiest way to do this is restart your computer.

I'm not sure I really had to move the Synaptics files out, but I did.

To test your evdev, go get a copy of evtest.py from gvalkov's Github: https://raw.githubusercontent.com/gvalkov/python-evdev/master/bin/evtest.py

You'll probably need to run that as sudo to get it to work. Verify that you have a keyboard and touchpad in the list of devices (mine shown below):

    ID  Device               Name                                Phys
    ---------------------------------------------------------------------------------------
    0   /dev/input/event0    Lid Switch                          PNP0C0D/button/input0
    1   /dev/input/event1    Sleep Button                        PNP0C0E/button/input0
    2   /dev/input/event2    Power Button                        LNXPWRBN/button/input0
    3   /dev/input/event3    AT Translated Set 2 keyboard        isa0060/serio0/input0
    4   /dev/input/event4    Video Bus                           LNXVIDEO/video/input0
    5   /dev/input/event5    ThinkPad Extra Buttons              thinkpad_acpi/input0
    6   /dev/input/event6    HDA Intel MID Mic                   ALSA
    7   /dev/input/event7    HDA Intel MID Dock Mic              ALSA
    8   /dev/input/event8    HDA Intel MID Dock Headphone        ALSA
    9   /dev/input/event9    HDA Intel MID Headphone             ALSA
    10  /dev/input/event10   HDA Intel MID HDMI/DP,pcm=3         ALSA
    11  /dev/input/event11   SynPS/2 Synaptics TouchPad          isa0060/serio1/input0
    12  /dev/input/event12   TPPS/2 IBM TrackPoint               synaptics-pt/serio0/input0

So my keyboard is available as ID 3 and the touchpad as device 11. Test that both are working. If you select the touchpad, you should see a (pages and pages) of text on your screen as you move your finger around on the touchpad.

    time 1452990543.87    type 3 (EV_ABS), code 1    (ABS_Y), value 873
    time 1452990543.87    type 3 (EV_ABS), code 24   (ABS_PRESSURE), value 4
    time 1452990543.87    type 3 (EV_ABS), code 28   (ABS_TOOL_WIDTH), value 6
    time 1452990543.87    --------- SYN_REPORT --------
    time 1452990543.89    type 3 (EV_ABS), code 57   (ABS_MT_TRACKING_ID), value -1
    time 1452990543.89    type 3 (EV_ABS), code 24   (ABS_PRESSURE), value 2
    time 1452990543.89    type 3 (EV_ABS), code 28   (ABS_TOOL_WIDTH), value 0
    time 1452990543.89    type 1 (EV_KEY), code 325  (BTN_TOOL_FINGER), value 0

Likewise, for the keyboard you should do the same (and see tons of output for keypresses).

    time 1452990595.7     type 4 (EV_MSC), code 4    (MSC_SCAN), value 28
    time 1452990595.7     --------- SYN_REPORT --------
    time 1452990596.79    type 4 (EV_MSC), code 4    (MSC_SCAN), value 57
    time 1452990596.79    type 1 (EV_KEY), code 57   (KEY_SPACE), value 1
    time 1452990596.79    --------- SYN_REPORT --------
    time 1452990596.86    type 4 (EV_MSC), code 4    (MSC_SCAN), value 57
    time 1452990596.86    type 1 (EV_KEY), code 57   (KEY_SPACE), value 0

Make sure that the EV_KEY, code #s for space is 57, escape is 1, and backspace is 14. I have those values hardcoded into the demo, so if your keyboard is different you'll need to track down that code and change it.

For my code to access the trackpad and keyboard inputs, you'll either need to run my script as sudo or give yourself non-sudo access to the /dev/input/events* corresponding to your touchpad and keyboard. Either thing is terrible, but it'd make me feel better if you didn't run scripts I write as sudo :D.

    chmod a+r /dev/input/events3
    chmod a+r /dev/input/events11

Would do the trick if you had my computer, but adjust them for yours.

nltk
-------------

nltk is the other dependency that is a little tricky to set up. I use it to parse the corpus to guess what text you're typing.

    pip install --user nltk

This should install the libraries. You'll also need to download some datasets for nltk to work (or it'll give you errors when you run my script)

In a Python terminal:

    import nltk
    nltk.download()

A window should appear. Download the 

![Corpora Screenshot](/path/to/img.jpg)

You'll need a bunch of Python libraries. I'll walk you through the installation process, but there are probably things here that don't translate to non-Ubuntu 14.04 computers or non-Lenovo x201 computers :D.


http://www.gutenberg.org/cache/epub/345/pg345.txt