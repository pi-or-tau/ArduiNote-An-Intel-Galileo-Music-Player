import midi
import os

'''Analyze .midi files to identify tracks and channels that contain music.

In order to properly use the midiConverter module, one has to know the track and channel of the .midi file that
actually contains the track you want. Oftentimes, you can just use track 0 and channel 0 and still be fine, but
that won't always work. This module can be helpful in those situations.

Uses the python-midi library written by vishnu-bob. Download it from here: https://github.com/vishnubob/python-midi
'''

def printEvents(pattern, track, noOfEvents):
    '''
    Print an arbitrary number of events from the first part of a track to the console.
    
    Arguments:
        pattern: the .midi pattern to analyze
        track: the track to analyze
        noOfEvents: the function will print this many events, starting from event 0
    '''
    for i in pattern[track][0:noOfEvents]:
        print i

def analyzeChannelFrequency(pattern, track):
    '''Returns a dictionary listing channels 0 through 9, along with the number of notes occurring in each of those channels.'''
    channelFrequency = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
    for i in pattern[track]:
        if isinstance(i, midi.NoteOnEvent):
            channelFrequency[i.channel] += 1
    return channelFrequency

#os.chdir('C:\Users\?????\Documents\Python\Arduino') #If Python is having issues with finding your .midi files, uncomment and modify this line
pattern = midi.read_midifile('darudeSandstorm.mid')
#printEvents(pattern, 0)
#print analyzeChannelFrequency(pattern, 0)