# Parse and display an iGo (Nav'n'Go) 8.3 pin file (PIN_V4.sav)
# Usage: igo_parse_pin_v4.py <filename>
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
    """Print unknown data as binary."""
    return ' '.join(["%02X"%ord(x) for x in src])

def get_pin(file):
    """Retrieve a single pin's data. Validates our assumptions about 
    the pin file format while reading it, prints errors."""

    ver = file.read(1)
    if (ord(ver) != 2):
        print "Format error! Version != 2"

    stuff = file.read(8) # unknown binary data, at this stage
    
    # pin UID
    txt = file.read(4)
    uid = struct.unpack('<I', txt)[0];

    # pin location
    geo = file.read(8) # unknown binary data, at this stage
    # probably 32 bits lat, 32 bits lon

    txt = get_unicode_string(file) # unknown string 1; maybe pin color?
    txt = get_unicode_string(file) # always 'sys'
    if (txt != 'sys'):
        print "Format error!"
        print "sys=", txt

    # Size of the 'human-readable location' string   
    txt = file.read(4)
    loc_length = struct.unpack('<I', txt)[0]; 

    # The next two strings are always equal in value; both contain human-
    # readable location of the pin
    txt = get_unicode_string(file) 
    loc = get_unicode_string(file)
    if (txt != loc):
        print "Format error!"
        print "txt=", txt
        print "loc=", loc
    if (loc_length != len(loc)):
        print "Format error!"
        print "location_len=", loc_length, 
        print "loc=", loc

    return {'uid': uid,
            'location': loc,
            'geo': geo,
            'stuff': stuff }

inp = open(args[0], 'rb')
pin_count = get_pin_count(inp)
print 'Total number of pins:', pin_count

actual_count = 0
while actual_count < pin_count:
    pin = get_pin(inp)
    print "UID", pin['uid'], pin['location'].encode('cp862', 'replace')
    print "    Geo", hex_print(pin['geo']), "Other data", hex_print(pin['stuff'])
    actual_count += 1

inp.close()
