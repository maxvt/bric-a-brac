# Converts Sony DVD Architect .SUB file to a .srt SubRip file
# Usage: dvd-architect-subs-to-subrip <filename>
# Result is written to filename with extension .srt
#
#
# Copyright (c) 2008 by Max Timchenko (www.maxvt.com)
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


import fileinput
import struct

subFormat = '4s 2x 8s 1x 2s 2x 8s 1x 2s 2x'

fi = fileinput.FileInput(openhook=fileinput.hook_encoded("utf_16_le"))
outfile = 0 # output file, sets value so that we wouldn't close the file
            # the first time round
insub = 0 # when 1, processing a multiline subtitle

while 1:
    line = fi.readline()
    print line
    if line == '':
        break
    
    # If new file, initialize the subtitle counter and open a new file
    if (fi.isfirstline()) :
        outfilename = (fi.filename())[0:len(fi.filename())-3]+u'srt';
        # close the previous file
        if outfile != 0 :
            outfile.close()
        outfile = open(outfilename, 'w')

    if (insub) :
        line = line.strip()
        if len(line) == 0 : 
            insub = 0
            continue
        outfile.write(line+'\n')

    else:
        num, start, startu, end, endu = struct.unpack_from(subFormat, line)
        text = line[32:]

        outfile.write(str(int(num)) + '\n')
        outfile.write(start + ',' + startu + '0 --> ' + end + ',' + endu + '0\n')
        outfile.write(text)
        insub = 1

outfile.close()
