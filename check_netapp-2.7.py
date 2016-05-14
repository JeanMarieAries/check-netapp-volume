#!/usr/bin/env python
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The MIT License (MIT)
Copyright (c) 2016 Jean Marie ARIES

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CHECK_NETAPP_VOLUME
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
# Header
_author_ = 'Jean Marie ARIES'
__copyright__ = "Copyright 2016, Jean Marie ARIES"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Jean Marie ARIES"
__email__ = "jm.aries@wanadoo.fr"
__status__ = "Production"


import argparse
from fabric.api import *
import sys
import os

# Vars
#   replace the two following if necessary
filedir = '/tmp/'
outputfile = 'df-output'
warnlist = []
critlist = []


# Functions
def findscorebyvolume(l):
    try:
        percent = int(l.split(' ')[6].split('%')[0])
        volume = l.split(' ')[7].split('/')[2]
        if args.W < percent < args.C:
            warnlist.append(volume + ' ' + str(percent) + '%')
        if percent >= args.C:
            critlist.append(volume + ' ' + str(percent) + '%')
    except:
        print 'error in ', l
        sys.exit(3)


# START :)

# define arguments parser & help
parser = argparse.ArgumentParser(prog='check_netapp_volume', formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='''check_netapp_volume is a python/nagios plugin that allow you to check volume space, according thresholds defined.
    It use SSH connection to connect to the filer, get the entire volumes list, parse and output the result.
    Example of run :
    check_netapp_volume -H BIGFiler -W 85 -C 95 -U supervisor -P superpassword''',
                                 epilog="""Twitter : @skycoyotte / Jean marie ARIES""")
parser.add_argument('-H', dest='hostname', help='hostname/IP of the Netapp filer', metavar='hostname', required=True)
parser.add_argument('-W', type=int, default=80, help='Warning threshold usage in percent', metavar='warningThreshold')
parser.add_argument('-C', type=int, default=90, help='Critical threshold usage in percent', metavar='criticalThreshold')
parser.add_argument('-U', dest='username', help='SSH Login to connect to the Netapp filer', metavar='SSHUser',
                    required=True)
parser.add_argument('-P', dest='password', help='SSH password to connect to the Netapp filer', metavar='SSHPassword',
                    required=True)
parser.add_argument('-I', dest='ignorelist', help='Ignore volume(s) matching pattern',
                    metavar='Volume(s) name(s) to ignore, separated by comma')
args = parser.parse_args()

# SSH Connection and save stdout
env.host_string = args.hostname
env.user = args.username
env.password = args.password
fileout = open(filedir + outputfile, 'w')
output = run('df -h', shell=False, stdout=fileout)

# File processing, depend on args
number = 0
with open(filedir + outputfile, 'r') as f:
    for line in f:
        if number == 0:
            number += 1  # Ignore the first line of the file
        else:
            if args.ignorelist:
                ignorestrings = args.ignorelist.split(',')
                found = False
                for pattern in ignorestrings:
                    if pattern in line:
                        found = True
                        break
                if not found and '%' in line:
                    findscorebyvolume(' '.join(line.split()))
                    number += 1
            else:
                print ' '.join(line.split())
                number += 1

# Delete temp file
os.remove(filedir + outputfile)

# Report execution
if critlist:
    print 'CRITICAL :', critlist
    sys.exit(2)
elif warnlist:
    print 'WARNING :', warnlist
    sys.exit(1)
elif not critlist and not warnlist:
    print "OK"
    sys.exit(0)
else:
    print "UKNOWN"
    sys.exit(3)
