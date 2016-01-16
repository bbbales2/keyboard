#%%

import scipy.interpolate
import numpy
import matplotlib.pyplot as plt
import scipy.cluster
import collections
import select
import itertools
import nltk
import re
import os
import sys
import evdev
# import InputDevice, ecodes

# This should be the path to the current directory
try:
    base = os.path.dirname(os.path.realpath(__file__))
except:
    base = '/home/bbales2/keyboard'

print "Searching for corpus"

if not os.path.exists(os.path.join(base, '345.txt')):
    while True:
        yn = raw_input("Would you like this script to download a corpus for you? (y/n): ").lower()
    
        if len(yn) >= 1 and yn[0] == 'y':
            import urllib2
            print "Downloading {0}".format('http://www.gutenberg.org/ebooks/345.txt.utf-8')
            url = urllib2.urlopen('http://www.gutenberg.org/ebooks/345.txt.utf-8')
            f = open(os.path.join(base, '345.txt'), 'w')
            f.write(url.read())
            f.close()
            
            break
        elif len(yn) >= 1 and yn[0] == 'n':
            print "Well download your own copy of Dracula from Gutenberg"
            print "  as a utf-8 encoded text and store it as {0}".format(os.path.join(base, '345.txt'))
            
            exit(0)
        else:
            print "- Only enter 'y' or 'n'"
            
print "Scanning input devices"

# These are the minimum and maximum coordinates reported by the evdev controller
#minx = 500.0
#miny = 500.0
#maxx = 6400.0
#maxy = 6400.0

# One of these should be a keyboard and the other should be a touchpad in absolute mode
devices = {}
for f in os.listdir('/dev/input'):
    if not re.match('event[0-9]+', f):
        continue
    
    devicePath = os.path.join('/dev/input', f)
    #print devicePath
    if os.access(devicePath, os.R_OK):
        dev = evdev.InputDevice(devicePath)
        devices[dev.fd] = dev

        print dev.fd, ' : ', dev.name

if len(devices) < 2:
    print "You must have a touchpad and keyboard available for reading"
    print "  Either run this script as sudo (boooo!) or use "
    print "  https://github.com/gvalkov/python-evdev/blob/master/bin/evtest.py"
    print "  to find what files in /dev/input/events are touchpads and keyboards"
    print "  and add read permissions (chmod a+r) for everyone"


def getDevice(prompt):
    while True:
        variable = raw_input(prompt)

        if variable.strip().isdigit():
            return int(variable)

keyboard = getDevice("Enter the device code of a keyboard: ")
touchpad = getDevice("Enter the device code of a touchpad in absolute mode: ")

devices = [ devices[keyboard], devices[touchpad] ]
devices = { dev.fd: dev for dev in devices }

#%%
print "Detecting touchpad limits"

# Find and get input ranges for trackpad

for dev in devices.values():
    caps = dev.capabilities(verbose = True)

    if ('EV_ABS', evdev.ecodes.EV_ABS) not in caps:
        continue

    codes = {}
    infos = {}
    for (name, code), absinfo in caps[('EV_ABS', evdev.ecodes.EV_ABS)]:
        codes[name] = code
        infos[name] = absinfo

    #[i for i, key in enumerate(absActions) if key[0] == 'ABS_X']
    minx = float(infos['ABS_X'].min)
    maxx = float(infos['ABS_X'].max)
    
    miny = float(infos['ABS_Y'].min)
    maxy = float(infos['ABS_Y'].max)
    
    minp = float(infos['ABS_PRESSURE'].min)
    maxp = float(infos['ABS_PRESSURE'].max)
    
    break
#%%
print "Building dictionary"
sys.stdout.flush()
#Import our dictionary
f = open(os.path.join(base, '345.txt'))
data = unicode(f.read(), 'utf-8')
#print data
tokens = nltk.word_tokenize(data)
f.close()

words = []
clear = re.compile('[^A-Za-z]')
number = re.compile('[0-9]')

# We only want letters
# Get rid of words with any numbers
# Delete any other errant characters
for token in tokens:
    if number.match(token):
        continue

    filtered = clear.sub('', token).lower()
    words.append(filtered)

# We only want the most frequent words
# wbL is a dictionary mapping word lengths to a list of words of that length
# lprobs is a dictionary mapping word names to empirical probabilities
counts = collections.Counter()
pcounts = collections.Counter()
lcounts = collections.Counter()

for word in words:
    counts[word] += 1

pruned = []
for word in words:
    if counts[word] > 1:
        pruned.append(word)
        pcounts[word] = counts[word]

wbL = {}

for word in pruned:
    if len(word) not in wbL:
        wbL[len(word)] = set()

    wbL[len(word)].add(word)

    for w in word:
        lcounts[w] += 1.0

# wprobs is word probabilty given word length
wprobs = {}

for length in wbL:
    wprobs[length] = {}

    totalWs = 0.0
    for w in wbL[length]:
        totalWs += pcounts[w]

    for w in wbL[length]:
        wprobs[length][w] = pcounts[w] / totalWs

# unconditional letter probabilities
lprobs = {}

totals = sum(lcounts.values())
for l in lcounts:
    lprobs[l] = lcounts[l] / totals
#%%

# We're building keyboard distributions
# We'll get two data structures
# dists is a dictionary mapping letters to distributions p(letter | absolute x & y)
# distsBi is a dictionary mapping two letters, l0, l1 (l1 coming after l0) to
#    p(l0, l1 | (x1, y1) & (x0, y0))
print "Setting up keyboard"
letters = ['qwertyuiop',
           'asdfghjkl',
           'zxcvbnm']

dx = 1.0 / 11.0

sigma = 0.2

letter_means = []

for i, row in enumerate(letters):
    uy = (i + 1) * 0.25
    for j, letter in enumerate(row):
        ux = i * dx * 0.5 + (j + 1) * dx

        letter_means.append((letter, ux, uy))

dists1 = {}

for letter, ux, uy in letter_means:
    dists1[letter] = scipy.stats.multivariate_normal([ux, uy], [[sigma**2, 0.0], [0.0, sigma**2]])

dists2 = {}

for (letter0, ux0, uy0), (letter1, ux1, uy1) in itertools.product(letter_means, repeat = 2):
    dists2[(letter0, letter1)] = scipy.stats.multivariate_normal([ux1 - ux0, uy1 - uy0], [[0.2**2, 0.0], [0.0, 0.2**2]])

#%%

def classify1(presses):
    if len(presses) < 1:
        return ''

    lps = []
    for x, y in presses:
        # Evaluate letter distributions
        results = [(key, dists1[key].pdf([x, y])) for key in dists1]

        totalP = sum([p for l, p in results])

        # For each press, save dictionary matching probability of each letter
        lps.append(dict([(l, -numpy.log(p / totalP)) for l, p in results]))

    tws = []
    for w in wbL[len(presses)]:
        total = 0.0
        for i in range(len(w)):
            total += lps[i][w[i]]  # + -numpy.log(lprobs[l])

        tws.append((w, total))# - numpy.log(wprobs[len(presses)][w])

    tws = sorted(tws, key = lambda x : x[1])

    return tws[0][0]#[w for w, p in tws[0:10]]
#%%
def classify2(presses):
    if len(presses) < 1:
        return ''

    blps = []
    for i in range(len(presses) - 1):
        x0, y0 = presses[i]
        x1, y1 = presses[i + 1]

        results = [((l0, l1), dists2[(l0, l1)].pdf([x1 - x0, y1 - y0]) * dists1[l0].pdf([x0, y0])) for l0, l1 in dists2]

        totalP = sum([p for l, p in results])

        blps.append(dict([(l, -numpy.log(p / totalP)) for l, p in results]))

    tws = []
    for w in wbL[len(presses)]:
        total = 0.0
        for i in range(len(w) - 1):#enumerate(w)
            total += blps[i][(w[i], w[i + 1])]# + -numpy.log(lprobs[l])

        tws.append((w, total - numpy.log(wprobs[len(presses)][w])))

    tws = sorted(tws, key = lambda x : x[1])

    return tws[0][0]
#%%
print "\nStart typing:"
peaks = []
last = None
startl = None
starth = None
    
ts = []
rs = []
xs = []
ys = []
ps = []

presses = []

lastWord = 0
words = []
#printWords = []

lastP = 0
lastX = 0
lastY = 0

getOut = False

lastClass = 0

while True:
    if getOut:
        break

    r, w, x = select.select(devices, [], [])
    for fd in r:
        if getOut:
            break
        #print devices[fd]

        for event in devices[fd].read():
            if event.type == evdev.ecodes.EV_KEY:
                if event.code == 1:  # Escape
                    getOut = True
                    break
                elif event.code == 57 and event.value == 1:  # Space
                    if lastWord != len(presses):
                        words.append((lastWord, len(presses) - lastWord))

                        lastWord = len(presses)

                        sys.stdout.write('\n')
                        sys.stdout.flush()
                elif event.code == 14 and event.value == 1:
                    if len(presses) > lastWord:
                        presses.pop()

                        sys.stdout.write("\r" + " " * 80)
                        sys.stdout.write("\r" + classify1(presses[lastWord : len(presses)]))
                        sys.stdout.flush()
                    #results = classify(ts, xs, ys, ps)

            if event.type == evdev.ecodes.EV_ABS:
                if event.code == codes['ABS_X']:
                    lastX = (float(event.value) - minx) / (maxx - minx)
                elif event.code == codes['ABS_Y']:
                    lastY = (float(event.value) - miny) / (maxy - miny)
                elif event.code == codes['ABS_PRESSURE']:
                    lastP = (float(event.value) - minp) / (maxp - minp)

                idx = len(rs)
                ts.append(event.timestamp())
                ps.append(lastP)
                rs.append(lastP < 0.1)
                ys.append(lastY)
                xs.append(lastX)

                newPeak = False

                if last is None:
                    last = rs[idx]

                    if last is True:
                        startl = idx
                    else:
                        starth = idx

                if last is True:
                    if not rs[idx]:
                        peaks.append((startl, (idx - 1 - startl), 0))
                        starth = idx
                        newPeak = True
                else:
                    if rs[idx]:
                        peaks.append((starth, (idx - 1 - starth), 1))
                        startl = idx
                        newPeak = True

                last = rs[idx]

                if newPeak:
                    start, length, press = peaks[-1]

                    if press:
                        presses.append((numpy.mean(xs[start : start + length]), numpy.mean(ys[start : start + length])))

                        #print lastWord, len(presses)
                        sys.stdout.write("\r" + " " * 80)
                        sys.stdout.write("\r" + classify1(presses[lastWord : len(presses)]))
                        sys.stdout.flush()

#%%


