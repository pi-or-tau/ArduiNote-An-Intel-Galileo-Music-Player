import midi
import os

"""Python-based .midi to plaintext conversion script.

This module allows the user to convert a .midi file into a format that could be copy-pasted into an Arduino Sketch
or into the source code of a similar device with a piezoelectric buzzer. Its output will take the form of two lists,
the first containing the frequencies of each of the song's notes in order, the second containing the lengths of each
of those notes in order.

These lists can, for instance, be turned into two arrays called 'SongFrequencies' and 'SongDurations'. To play the song,
one can create a loop that increments a variable called 'i', playing a tone of frequency SongFrequencies[i] for
SongDurations[i] milliseconds before proceeding to the next note.

Uses the python-midi library written by vishnu-bob. Download it from here: https://github.com/vishnubob/python-midi

Try getting midi files from musescore.com; they're typically arranged such that it's easy to figure out which track corresponds with which instrument.
"""

class Song(object):
    """
    Create an object representing a particular .midi file.
    
    Note:
        Because the Arduino and Finch buzzers can only play one note at a time, it's currently not possible to play every part of a song with multiple instruments. You have
        to specifically look for .midi files with only one part. You can also use a .midi file with multiple parts if one of the parts is the melody while the
        other parts are unimportant.
        
        This class represents a song made up of individual notes played one at a time in sequential order, read from the particular 'track' and 'channel' of the
        .midi file that contains the song's main melody. All other parts of the .midi file (i.e. other musical accompaniment) won't be included.
    
    Arguments:
        midiPattern: 'pattern' of a song obtained by having the MIDI library analyze a .midi or .mid file; is divided into 'tracks'
        track: integer, represents the track that you want to read from; tracks contain 'Events' that are divided between different channels.
        channel: integer, represents the channel of the track that you want to read from.
    """

    def __init__(self, midiPattern, track, channel):
        self.currentTick = 0
        self.currentNoteIndex = 0
        self.bpm = 120 #This is just a default in case the .midi doesn't actually list a tempo.
        self.sheet = []
        self.resolution = midiPattern.resolution #ticks per quarter note
        
        self.usesNoteOff = self.usesNoteOffEvents(midiPattern, track) #The process for determining the length of a note is different if a song does or doesn't use NoteOffEvents.
        
        for i in midiPattern[0]: #Reads through Track 0 to look for a SetTempoEvent to determine the beats-per-minute of the song.
            if isinstance(i, midi.SetTempoEvent):
                self.bpm = i.bpm
        
        if not self.usesNoteOff:
            for i in midiPattern[track]: #Reads through the user-specified track; if the event is a NoteOnEvent and matches the user-specified channel, add it to the note sheet.
                if isinstance(i, midi.NoteOnEvent) and i.channel == channel:
                    self.sheet.append(MusicalNote(i.pitch, i.tick)) #Note list will only contain NoteOnEvents.
        else:
            for i in midiPattern[track]: #Does the same, but with NoteOffEvents instead.
                if isinstance(i, midi.NoteOffEvent) and i.channel == channel:
                    self.sheet.append(MusicalNote(i.pitch, i.tick)) #Note list will only contain NoteOffEvents.
                
    def usesNoteOffEvents(self, midiPattern, track):
        """
        Check to see if .midi track uses NoteOnEvents exclusively or a combination of NoteOn and NoteOffEvents.

        Note: MuseScore .mid files typically use the former while .midi's from NoteFlight typically use NoteOn and NoteOffEvents.
        
        Arguments:
            midiPattern: the .midi pattern to analyze
            track: the track to check
        """
        containsNoteOff = False
        for i in midiPattern[track]:
            if isinstance(i, midi.NoteOffEvent):
                containsNoteOff = True
        return containsNoteOff

    def getFrequencyList(self):
        """
        Return a list containing the frequencies of every individual note to be played in Hertz.
        
        Note: both NoteOnEvents and NoteOffEvents typically have associated frequencies.        
        """
        index = 0
        frequencyList = []
        
        while index < len(self.sheet) - 1:      
            frequencyList.append(self.sheet[index].frequency)
            index += 1
        frequencyList.append(-1)
        return frequencyList
        
    def getDurationList(self):
        """
        Return a list containing the durations of every individual note to be played in milliseconds.
        
        Note: 
            Every event in a .midi file has a 'tick' value, representing the number of ticks that must pass after the *previous* event
            before the current event can occur. The resolution of a .midi file is the number of ticks per beat of the song.
        """
        beatLength = 60.0 / self.bpm #the number of seconds per 'beat' of the song
        index = 0
        durationList = []
        
        if not self.usesNoteOff: #If song only uses NoteOnEvents, get the length of a note based on when the *next* note should start playing (i.e. tick value of next NoteOnEvent).
            while index < len(self.sheet) - 1:
                noteLengthTicks = self.sheet[index + 1].tick #length of the note in ticks
                noteLength = ((beatLength / self.resolution)) * noteLengthTicks * 1000 #length of note in milliseconds
                
                durationList.append(int(noteLength))
                index += 1
        else: #If song usese NoteOffEvents, get the length of a note based on when the note is supposed to stop playing (i.e. tick value of current NoteOffEvent).
            while index < len(self.sheet):
                noteLengthTicks = self.sheet[index].tick #length of the note in ticks
                noteLength = ((beatLength / self.resolution)) * noteLengthTicks * 1000 #length of note in milliseconds
                
                durationList.append(int(noteLength))
                index += 1
        durationList.append(-1)
        return durationList

    def shiftOctaveUp(self):
        """Raise the pitch of the entire song by an octave."""
        for note in self.sheet:
            note.changeFrequency(note.frequency*2)
            
    def shiftOctaveDown(self):
        """Lower the pitch of the entire song by an octave."""
        for note in self.sheet:
            note.changeFrequency(note.frequency/2)
            
    def doubleTempo(self):
        """Double the tempo of the entire song."""
        self.bpm = self.bpm * 2

class MusicalNote(object):
    """
    Create an object representing an individual musical note.
    
    Arguments:
        pitch: the 'pitch' given by a particular NoteOnEvent or NoteOffEvent; ranges from 0 to 127 and corresponds to a particular frequency in the .midi file format
        tick: the 'tick' value of the NoteOnEvent or NoteOffEvent
    """
    def __init__(self, pitch, tick):
        self.frequency = self.convertPitch(pitch)
        self.tick = tick

    def convertPitch(self, pitch):
        """Return the frequency corresponding to the given pitch"""
        conversionDictionary = {0:8.176, 1:8.662, 2:9.177, 3:9.7227, 4:10.3, 5:10.913, 6:11.562, 7:12.250, 8:12.978, 9:13.75, 10:14.568, 11:15.434, 12:16.351, 13:17.324, 14:18.354, 15:19.445, 16:20.601, 17:21.827, 18:23.12, 19:24.5, 20:25.957, 21:27.5, 22:29.135, 23:30.868, 24:32.703, 25:34.648, 26:36.708, 27:38.891, 28:41.506, 29:43.654, 30:46.249, 31:48.999, 32:51.913, 33:55, 34:58.27, 35:61.735, 36:65.406, 37:69.296, 38:69.296, 39:77.781, 40:82.407, 41:87.307, 42:92.499, 43:97.999, 44:103.826, 45:110, 46:116.54, 47:123.471, 48:130.813, 49:138.591, 50:146.832, 51:155.563, 52:164.814, 53:174.614, 54:184.997, 55:195.998, 56:207.652, 57:220, 58:233.081, 59:246.942, 60:261.626, 61:277.183, 62:293.665, 63:311.127, 64:329.628, 65:349.228, 66:369.994, 67:391.995, 68:415.305, 69:440,70:466.164, 71:493.883, 72:523.251, 73:554.365, 74:587.329, 75:622.254, 76: 659.255, 77: 698.456, 78: 739.988, 79: 783.991, 80: 830.609, 81: 880.0, 82: 932.327, 83: 987.767, 84: 1046.502, 85: 1108.731, 86: 1174.659, 87: 1244.508, 88: 1318.51, 89: 1396.913, 90: 1479.978, 91: 1567.981, 92: 1661.219, 93: 1760.0, 94: 1864.655, 95: 1975.533, 96: 2093.004, 97: 2217.461, 98: 2349.318, 99: 2489.015, 100: 2637.02, 101: 2793.806, 102: 2959.955, 103: 3135.963, 104: 3322.438, 105: 3520.0, 106: 3729.0, 107: 3951.066, 108: 4186.009, 109: 4434.922, 110: 4698.636, 111: 4978.031, 112: 5274.041, 113: 5587.651, 114: 5919.911, 115: 6271.927, 116: 6644.875, 117: 7040.0, 118: 7458.621, 119: 7902.1328, 120: 8372.018, 121: 8869.844, 122: 9397.273, 123: 9956.0635, 124: 10548.081, 125: 11175.303, 126: 11839.822, 127: 12543.854} 
        return int(conversionDictionary[pitch])

    def changeFrequency(self, newFrequency):
        """Change the frequency of a particular note."""
        self.frequency = newFrequency
        
def outputLists(filename, fileToOutput, track, channel):
    """
    Process a .midi file and print its frequencies and durations to the console and a text file.

    Arguments:
        filename: string containing the filename of the midi file to be played. File must be in same folder as midiConverter.py
        fileToOutput: this function outputs both lists to a text file; this is the filename of that text file
    """
    #os.chdir('C:\Users\?????\Documents\Python\Arduino') #If Python is having issues with finding your .midi files, uncomment and modify this line
    pattern = midi.read_midifile(filename)
    song = Song(pattern, track, channel)
    
    file = open(fileToOutput, "w")
    
    frequencyList = ''
    durationList = ''
    
    for i in str(song.getFrequencyList()):
        if i == '[':
            frequencyList = frequencyList + '{'
        elif i == ']':
            frequencyList = frequencyList + '}'
        else:
            frequencyList = frequencyList + i
    frequencyList = frequencyList + ';'

    for i in str(song.getDurationList()):
        if i == '[':
            durationList = durationList + '{'
        elif i == ']':
            durationList = durationList + '}'
        else:
            durationList = durationList + i
    durationList = durationList + ';'
    
    file.write("Frequencies (Hz): \n")
    file.write(frequencyList)
    file.write("\n\nDurations (ms): \n")
    file.write(durationList)

    print "Frequency List:"
    print song.getFrequencyList()
    print "Duration List:"
    print song.getDurationList()
    
    file.close()

#os.chdir('C:\Users\?????\Python\Documents\Arduino') #If Python is having issues with finding your .midi files, uncomment and modify this line

#outputLists('Poker_Face.mid', 'pokerFace_mod.txt', 0, 0) 
#outputLists('Imperial_March.mid', 'imperialMarch_mod.txt', 0, 0)
#outputLists('SuperMarioBrothers.mid', 'superMarioBrothers_mod.txt', 0, 0)
#outputLists('Never_Gonna_Give_You_Up.mid', 'neverGonnaGiveYouUp.txt', 0, 0)
#outputLists('turretOpera.mid', 'turretOpera.txt', 0, 0)
#outputLists('darudeSandstorm.mid', 'darudeSandstorm.txt', 1, 0)