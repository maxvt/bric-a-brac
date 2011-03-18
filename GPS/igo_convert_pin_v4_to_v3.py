# Convert an iGo (Nav'n'Go) 8.3 pin file (PIN_V4.sav) to a 8.0 pin file (PIN_V3.sav)
# Usage: igo_convert_pin_v4_to_v3.py <filename>
# The result will be written into a file named "out.bin"
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

def put_pin_count(file, pin_count):
    """Write out the pin count."""

    txt = struct.pack('<H', pin_count)
    file.write(txt)

def get_unicode_string(file):
    """Retrieve a null-terminated Unicode string."""
    txt = ''

    char = file.read(2)
    while (struct.unpack('H', char)[0] != 0) :
        txt = txt + char.decode('utf_16')
        char = file.read(2)

    return txt

def put_unicode_string(file, txt):
    """Write a null-terminated Unicode string."""
    for ch in txt:
        encoded = ch.encode('utf_16_be')
        file.write(encoded)
    
    term = struct.pack('H', 0);
    file.write(term)

def hex_print(src):
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

    txt = get_unicode_string(file) # unknown string 1; maybe pin color?
    txt = get_unicode_string(file) # always 'sys'
    if (txt != 'sys'):
        print "Format error!"
        print "sys=", txt

    # Always one char in length, looks like size of the 'readable location'
    # below ('untitled' => 0x07 0x00)
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

def put_pin(file, pin, pin_number_in_file):
    """Write out a single pin data in V3 format"""
    if (pin_number_in_file > 1):
        txt = struct.pack('<H', 0);
        file.write(txt)

    # version
    txt = struct.pack('B', 1);
    file.write(txt)

    file.write(pin['stuff'])

    txt = struct.pack('<I', pin_number_in_file)
    file.write(txt)

    file.write(pin['geo'])

    txt = struct.pack('<I', pin['uid'])
    file.write(txt)

    txt = struct.pack('<I', len(pin['location']))
    file.write(txt)

    put_unicode_string(file, pin['location'])

inp = open(args[0], 'rb')
pin_count = get_pin_count(inp)
print 'Total number of pins:', pin_count

outp = open('out.bin', 'wb')
put_pin_count(outp, pin_count)

actual_count = 0
while actual_count < pin_count:
    pin = get_pin(inp)
    #print pin['location'].encode('cp862', 'replace')
    actual_count += 1
    put_pin(outp, pin, actual_count)

inp.close()
outp.close()
