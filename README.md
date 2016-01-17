Introduction
============

This is a prototype touchpad keyboard.

The idea is you should be able to type messages on a touchpad even if the letters themselves aren't visible on that touchpad. I got this idea when I bought my new Steam controller and tried to type a message on it. Using the two trackpads like mice seems neeeearly good enough, but it just isn't very fast.

I felt like I just wanted to type with my thumbs. I wanted to press where the keys maybe were and let Valve figure out the rest.

To test if this vague sorta keyboarding is possible, I built this touchpad keyboard. It lets you type on a tiny laptop trackpad (tested on a Lenovo x201). For people who are familiar with the layout of a regular keyboard, I expect it would be quite intuitive.

Ideally it could be ported to a Steam controller in split keyboard mode.

The downside to this sorta keyboard is that you really need to lean on heavyweight autocomplete-style statistics. That means you can't be typing very technical things, or you can't be typing things that you don't have a reference on. For instance, it's probably not a good idea to try to program with an interface like this, but using such an interface to communicate with your friends should be okay.

You can see the keyboard in operation here: https://youtu.be/ec3d1kan4jg

Using
=============

You'll need a laptop running a Linux distribution with a touchpad that supports absolute input mode. I install all my pip packages with --user so I don't screw up system stuff. You can do whatever you want.

First get a copy of this repository on your computer with

    git clone https://github.com/bbbales2/keyboard.git

You'll need to install a bunch of libraries to get this to work.

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

If any of that is unclear, I have video of me walking through it here: https://youtu.be/_2fxj0EjiBM

nltk
-------------

nltk is the other dependency that is a little tricky to set up. I use it to parse the corpus to guess what text you're typing.

    pip install --user nltk

This should install the libraries. You'll also need to download some datasets for nltk to work (or it'll give you errors when you run my script)

In a Python terminal:

    import nltk
    nltk.download()

A window should appear. Download the book corpora.

![Corpora Screenshot](https://raw.githubusercontent.com/bbbales2/keyboard/master/corpora_download.png)

Other things
--------------

Other than this you'll need

    scipy > 14.0
    numpy
    matplotlib

The scipy that comes with Ubuntu 14.04 is slightly older than that. To upgrade it

    pip install --user --upgrade scipy

Corpus
-------------

You'll need a corpus for the script to use. 

    wget https://www.gutenberg.org/ebooks/345.txt.utf-8 345.txt

That should do the trick. Put the file 345.txt in the same folder as the keyboard.py script.

You're ready!
-------------

Just type

    python keyboard.py

and you should be prompted to select your keyboard and touchpad. If you're able to select those, then after a few seconds (the script needs to parse the Dracula corpus) you're ready to type.

Just start typing things on your touchpad. To end a word press space. To delete a character press delete. To quit press escape!

Have fun!

Theory of Operation
==================

So the theory here is pretty simple. We have mapped positions on the touchpad to the a-z keys on a keyboard. When we press a certain place on the touchpad, the computer generates a list of distances from the place we touch to the positions of all the letters on the keyboard. From these distances, we compute a probability that a given press is a certain letter. We compute the probabilities from the distances with some made up Gaussians. Look at the code for details.

So for a given press we have a list of 24 probabilities that it was a certain letter.

Now given the user has made a number of presses on the keyboard, we have a list of probabilities that each touch is a letter and a length of word (number of presses). We simply evaluate the probabilities of every word of the given length (from a dictionary) and see which is most likely. Our dictionary in this case is Dracula. It could be anything.

So if we have 3 presses, and we wanted to see how likely the word 'cat' was we do:

p(press 1 was a 'c') * p(press 2 was an 'a') * p(press 3 was a 't')

In the code we use logs so that looks like:

-ln(p(press 1 was a 'c')) - ln(p(press 2 was an 'a')) - ln(p(press 3 was a 't'))

Maximizing the probabilities is the same in theory as maximizing those sums of logs. The numbers are just nicer with the logs.
