import midi
import os

'''
Use this script to figure out which track and which channel you ought to read from.
If the .midi file only has one part, then you can just read from track 0 and channel 0 and you'll probably be fine.
'''

def printEvents(pattern, track):
    '''
    function: prints the first 30 events associated with the given pattern and track
    '''
    for i in pattern[track][0:30]:
        print i

def analyzeChannelFrequency(pattern, track):
    '''
    function: analyzes a given track to determine how many notes occur in each channel
    returns: a dictionary listing channels 0 through 9, along with the number of notes occurring in each of those channels
    '''
    channelFrequency = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
    for i in pattern[track]:
        if isinstance(i, midi.NoteOnEvent):
            channelFrequency[i.channel] += 1
    return channelFrequency

os.chdir('C:\Users\Yilin\Documents\Python\Arduino') #Change this
pattern = midi.read_midifile('SuperMarioBrothers.mid')
#printEvents(pattern, 0)
print analyzeChannelFrequency(pattern, 0)

'''
'SuperMarioBrothers.mid' has one track and one channel; it has 646 notes, all of which are on track 0, channel 0.
'''