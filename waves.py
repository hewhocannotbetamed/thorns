#!/usr/bin/env python

from __future__ import division

__author__ = "Marek Rudnicki"

import numpy as np

golden = 1.6180339887
pi = np.pi

# TODO: help, testdoc
def detect_peaks(fs, signal):
    d = np.diff(signal)
    s = np.sign(d)

    sd = np.diff(s)

    peak_idx = np.where(sd==-2)[0] + 1
    peak_val = signal[peak_idx]

    assert ((signal[peak_idx-1] < signal[peak_idx]).all() and
            (signal[peak_idx+1] < signal[peak_idx]).all())

    return peak_idx, peak_val



def root_mean_square(s):
    return np.sqrt( np.sum(s**2) / len(s) )

rms = root_mean_square




def set_dbspl(p0, p1):
    if np.isscalar(p0) and isinstance(p1, np.ndarray):
        dB, signal = p0, p1
    elif np.isscalar(p1) and isinstance(p0, np.ndarray):
        signal, dB = p0, p1
    else:
        assert False, "Input not correct, must be scalar and array"

    p0 = 2e-5                   # Pa
    squared = signal**2
    rms = np.sqrt( np.sum(squared) / len(signal) )

    if rms == 0:
        r = 0
    else:
        r = 10**(dB / 20.0) * p0 / rms;

    return signal * r * 1e6     # uPa




def make_time(fs, s):
    """
    Return time vector for signal `s' in ms.

    fs: sampling frequency in Hz
    s: signal

    >>> make_time(10, [2,3,4,4,5])
    array([   0.,  100.,  200.,  300.,  400.])
    """
    tmax = 1000 * (len(s)-1) / fs
    return np.linspace(0, tmax, len(s))

t = make_time



# TODO: allow values to be 0, change default values
def generate_ramped_tone(fs, freq,
                         tone_duration=50,
                         ramp_duration=2.5,
                         pad_duration=55,
                         dbspl=None):
    """ Generate ramped tone singal.

    fs: sampling frequency (Hz)
    freq: frequency of the tone (Hz)
    tone_durations: ms
    ramp_duration:
    pad_duration:
    dbspl:

    """
    t = np.arange(0, tone_duration, 1000/fs)
    s = np.sin(2 * np.pi * t * freq/1000)
    if dbspl != None:
        s = set_dbspl(dbspl, s)

    ramp = np.linspace(0, 1, np.ceil(ramp_duration * fs/1000))
    s[0:len(ramp)] = s[0:len(ramp)] * ramp
    s[-len(ramp):] = s[-len(ramp):] * ramp[::-1]

    pad = np.zeros(pad_duration * fs/1000)
    s = np.concatenate( (s, pad) )

    return s


def generate_amplitude_modulated_tone(fs, fm, fc,
                                      modulation_depth=1,
                                      tone_duration=100):
    """ Generates amplitude modulated signals.

    fs: sampling frequency (Hz)
    fm: modulation frequency (Hz)
    fc: carrier frequency (Hz)
    modulation_depth: modulation depth
    tone_duration: tone duration (ms)

    """
    m = modulation_depth
    t = np.arange(0, tone_duration/1000, 1/fs)
    s = (1 + m*np.sin(2*pi*fm*t)) * np.sin(2*pi*fc*t)

    return s


generate_am_tone = generate_amplitude_modulated_tone


def now():
    from datetime import datetime
    t = datetime.now()

    now = "%04d%02d%02d-%02d%02d%02d" % (t.year,
                                         t.month,
                                         t.day,
                                         t.hour,
                                         t.minute,
                                         t.second)
    return now


def time_stamp(fname):
    from os import path

    root,ext = path.splitext(fname)
    return root + "__" + now() + ext

tstamp = time_stamp


def meta_stamp(fname, *meta_args, **meta_kwargs):
    """ Add meta data string to the file name.

    >>> meta_stamp('/tmp/a.txt', {'b':1, 'c':3}, d=12, e=13.6)
    '/tmp/a__c=3__b=1__e=13.6__d=12.txt'

    """
    from os import path

    root,ext = path.splitext(fname)
    meta_str = str()

    for meta_dict in meta_args:
        for meta_key in meta_dict:
            meta_str += _meta_sub_string(meta_key, meta_dict[meta_key])

    for meta_key in meta_kwargs:
        meta_str += _meta_sub_string(meta_key, meta_kwargs[meta_key])

    new_fname = root + meta_str + ext
    new_fname = new_fname.replace(' ', '_')
    return new_fname

mstamp = meta_stamp

def _meta_sub_string(var, value):
    return '__' + str(var) + '=' + str(value)



def generate_biphasic_pulse(fs, pulse_width, gap_width,
                            amplitude=1,
                            fstim=None,
                            stimulus_duration=None,
                            polarity='a'):
    """ Generate biphasic pulse for electrical stimulation.

    fs: Hz
    pulse_width: us
    gap_width: us
    amplitude: mA
    fstim: Hz
    stimulus_duration: ms
    polarity: 'c': cathodic, 'a': anodic

    """
    def idx(width):
        """ fs: Hz, width: us """
        return np.round(fs*width/1e6)

    if fstim is None:
        fstim = 1e6 / (2*pulse_width + gap_width) # Hz
    stim = np.zeros(np.round( fs/fstim ))

    stim[ 0:idx(pulse_width) ] = amplitude
    stim[ idx(pulse_width+gap_width):idx(2*pulse_width+gap_width) ] = -amplitude

    if stimulus_duration is not None:
        times = np.ceil(stimulus_duration / (len(stim)*1000/fs))
        stim = np.tile(stim, times)
        stim = stim[0:np.ceil(stimulus_duration*fs/1000)]

    if polarity == 'c':
        stim = -stim

    return stim


def plot_signal(fs, s):
    import biggles

    t = make_time(fs, s)

    plot = biggles.FramedPlot()
    plot.add( biggles.Current(t, s) )
    plot.xlabel = Time (ms)

    return plot



if __name__ == "__main__":
    import doctest

    print "Doctest start:"
    doctest.testmod()
    print "done."
