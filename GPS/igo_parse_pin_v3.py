# Parse and display an iGo (Nav'n'Go) 8.0 pin file (PIN_V3.sav)
# Usage: igo_parse_pin_v3.py <filename>
#
#
# Copyright (c) 2010 by Max Timchenko (www.maxvt.com)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from optparse import OptionParser
import struct

parser = OptionParser()
(options, args) = parser.parse_args()

def get_pin_count(file):
    """Retrieve the pin count."""
    txt = file.read(2)
    return struct.unpack('<H', txt)[0]

def get_unicode_string(file):
    """Retrieve a null-terminated Unicode string."""
    txt = ''

    char = file.read(2)
    while (struct.unpack('H', char)[0] != 0) :
        txt = txt + char.decode('utf_16')
        char = file.read(2)

    return txt

def hex_print(src):
    print ' '.join(["%02X"%ord(x) for x in src])

def get_pin(file, actual_count):
    """Retrieve a single pin's data. Validates our assumptions about 
    the pin file format while reading it, prints errors."""
    if (actual_count > 0):
        txt = file.read(2) # discard first 2 bytes
        if (struct.unpack('H', txt)[0] != 0):
            print "Format error! Discarded bytes not 0"
    
    txt = file.read(21) # unknown binary data, at this stage
    hex_print(txt)

    # pin UID
    txt = file.read(4)
    uid = struct.unpack('<I', txt)[0];

    # Length of the location string
    txt = file.read(4)
    loc_length = struct.unpack('<I', txt)[0];

    # Human-readable location of the pin
    loc = get_unicode_string(file)
    if (loc_length != len(loc)):
        print "Format error!"
        print "location_len=", loc_length, 
        print "loc=", loc

    return {'uid': uid, 
            'location': loc }

inp = open(args[0], 'rb')
pin_count = get_pin_count(inp)
print 'Total number of pins:', pin_count

actual_count = 0
while actual_count < pin_count:
    pin = get_pin(inp, actual_count)
    #print pin['location'].encode('cp862', 'replace')
    #print pin['uid']
    actual_count += 1

inp.close()
