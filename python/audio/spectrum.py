#!/usr/bin/env python
#-*-coding: utf-8 -*-
#
# Create a PNG representing the spectrum of a wav file
#

import numpy
import pylab
import struct
import sys
import wave


def main():
    if len(sys.argv) != 2:
        print "usage: %s <wav file>" % sys.argv[0]
        sys.exit(1)
    
    filename = sys.argv[1]
    
    print "Reading file: " + filename
    w = wave.open(filename)
    
    total_frames = w.getnframes()
    print "Number of frames:" + str(w.getnframes())
    
    sample_width = w.getsampwidth()
    framerate = w.getframerate()
    
    print "sample_width: " + str(sample_width)
    print "framerate: " + str(framerate)
    
    if sample_width != 2:
        print "sample width " + sample_width + " not supported"
        sys.exit(1)
    
    # change coeff to change fft samping rate
    coeff = 0.05
    std_n_frames = int(framerate * coeff)
    print "std_n_frames=%d" % std_n_frames
    
    print "\n"
    
    
    frames = w.readframes(int(framerate * coeff))
    n_frames = len(frames) / sample_width
    
    spectrum = numpy.array([numpy.zeros(int(std_n_frames / 2) + 1)])
    
    total_read_frames = n_frames
    while n_frames != 0:
        try:
            data = struct.unpack("%dh" % n_frames, frames)
        except:
            print "Unpack error " + str("%dh" % n_frames) + " (size of string:" + str(len(frames)) + ")"
    
    
        # compute fft
        fft = numpy.fft.rfft(data)
        fft = abs(fft)
        fft = 20 * numpy.log10(fft)
        fft = fft[::-1]
    
        try:
            spectrum = numpy.concatenate((spectrum, [fft]))
        except:
            print "*** Concat error"
    
            print "spectrum_shape = " + str(spectrum.shape)
            print "fft_shape = " + str(fft.shape)
    
        # get 5 top frequencies
        #n_top_freqs = 3
        #freqs = fft.argsort()[-n_top_freqs:][::-1]
        #max_freqs = {} 
        #for i in freqs:
        #    max_freqs[i / coeff] = fft[i]
    
        #print "max frequencies:"
        #for freq, val in sorted(max_freqs.iteritems(), key=lambda (k, v) : (v, k)):
        #    print freq, val
    
    
    
        #import pdb
        #pdb.set_trace()
    
        #print "Size of fft: " + str(len(fft))
        # plot fft
        #pylab.plot(abs(fft))
        #pylab.show()
    
        # loop

        frames = w.readframes(int(framerate * coeff))
        n_frames = len(frames) / sample_width
    
        # fill missing frames
        if n_frames != std_n_frames and n_frames != 0:
            print "read frames : " + "%d" % n_frames + " != " + "%d" % std_n_frames
            frames += "\x00\x00" * (std_n_frames - n_frames)
            print "Now n_frames = %d" % (len(frames) / sample_width)
            n_frames = std_n_frames
    
        total_read_frames += n_frames
        if round(total_read_frames * 100. / total_frames) == int(total_read_frames * 100. / total_frames):
            print "\r%d%%" % (100. * total_read_frames / total_frames),
            sys.stdout.flush()
        # uncomment to debug # of frames
        #print "read frames : " + str(total_read_frames) + "/" + str(total_frames)
    
    print spectrum.shape
    
    spectrum = spectrum.transpose()
    #spectrum = numpy.rollaxis(spectrum, 0)
    
    pylab.imshow(spectrum)
    pylab.show()
    print "saving png file..."
    pylab.imsave(".".join(filename.split(".")[:-1]) + ".png", spectrum)

main()
