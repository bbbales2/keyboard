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

> pip install --user evdev

To actually configure your trackpad, you'll need to add the line

> Option "Mode" "Absolute"

to your xorg.conf file. Ubuntu 14.04 just concatenates everything in /etc/X11/xorg.conf.d together as an xorg.conf.d file (https://wiki.ubuntu.com/X/Config). For me I edited the bit of /usr/share/X11/xorg.conf.d/10-evdev.conf labeled "touchpad" to look like:

>Section "InputClass"
>        Identifier "evdev touchpad catchall"
>        MatchIsTouchpad "on"
>        MatchDevicePath "/dev/input/event*"
>        Driver "evdev"
>        Option "Mode" "Absolute"
>EndSection

You'll need a bunch of Python libraries. I'll walk you through the installation process, but there are probably things here that don't translate to non-Ubuntu 14.04 computers or non-Lenovo x201 computers :D.


http://www.gutenberg.org/cache/epub/345/pg345.txt