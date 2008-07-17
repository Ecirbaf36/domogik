#!/usr/bin/python
#-*- encoding:utf-8 *-*

# Author: Maxence Dunnewind <maxence@dunnewind.net>
#
# This is the MPD support for MPRIS
# See mpris.py and http://wiki.xmms2.xmms.se/wiki/Media_Player_Interfaces

# Core dbus stuff
import dbus

# Core MPD stuff
import mpd


class Root(dbus.service.Object):

    def __init__(self, object_path):
        self.__mpd = mpd.MPDClient()
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/')
        
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def Identity(self):
        """
        Returns a string containing the media player identification
        """
        return "MPD %s" % (self.__mpd.mpd_version)

    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def Quit(self):
        """
        Makes the "Media Player" exit
        """
        pass

    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def MprisVersion(self):
        """
        Returns a struct that represents the version of the MPRIS spec being implemented, organized as follows:
            uint16 major version (Existing API change)
            uint16 minor version (API addition) 
        """
        return (1,0)
        pass

class TrackList(dbus.service.Object):

    def __init__(self, object_path):
        self.__mpd = mpd.MPDClient()
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/TrackList')
 
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def GetMetadata(self, position):
        """
        Gives all meta data available for element at given position in the TrackList, counting from 0. 
        """
        return self.__mpd.playlistinfo()[position]

    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def GetCurrentTrack(self):
        """
        Return the position of current URI in the TrackList
        The return value is zero-based, so the position of the first URI in the TrackList is 0.
        The behavior of this method is unspecified if there are zero elements in the TrackList.
        """
        return self.__mpd.currentsong()['pos']

    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def GetLength(self):
        """
        Number of elements in the TrackList
        """
        return self.__mpd.status['playlistlength']

    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')        
    def AddTrack(self, uri, playImmediately):
        """
        Appends an URI in the TrackList 
        """
        try:
            id = self.__mpd.addid(uri)
            if playImmediately:
                self.__mpd.playid(id)
        except:
            return 1
        else:
            return 0
        
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def DelTrack(self, track_position):
        """
        Removes an URI from the TrackList.
        """
        try:
            self.__mpd.deleteid(track_position)
        except:
            pass
        
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def SetLoop(self, loop):
        """
        Toggle playlist loop
        """
        if loop:
            self.__mpd.repeat(1)
        else:
            self.__mpd.repeat(0)
        
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def SetRandom(self, random):
        """
        Toggle playlist shuffle / random. It may or may not play tracks only once. 
        """
        if random:
            self.__mpd.random(1)
        else:
            self.__mpd.random(0)

class Player(dbus.service.Object):

    def __init__(self, object_path):
        __mpd = mpd.MPDClient()
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/Player')

    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def Next(self):
        """
        Goes to the next element
        """
        self.__mpd.next()
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def Prev(self):
        """
        Goes to the previous element
        """
        self.__mpd.previous()
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def Pause(self):
        """
        If playing : pause. If paused : unpause
        """
        self.__mpd.pause()
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def Stop(self):
        """
        Stop playing
        """
        self.__mpd.stop()
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def Play(self):
        """
        If playing : rewind to the beginning of current track, else : start playing
        """
        self.__mpd.play()
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def Repeat(self, repeat):
        """
        Toggle the current track repeat
        """
        pass
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def GetStatus(self):
        """
        Return the status of "Media Player" as a struct of 4 ints:
            First integer: 0 = Playing, 1 = Paused, 2 = Stopped.
            Second interger: 0 = Playing linearly , 1 = Playing randomly.
            Third integer: 0 = Go to the next element once the current has finished playing , 1 = Repeat the current element
            Fourth integer: 0 = Stop playing once the last element has been played, 1 = Never give up playing
        """
        state = {'play':0,'pause':1,'stop':2}
        status = self.__mpd.status()
        return (state[status['state']], int(state['random']), 0, int(state['repeat']))
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def GetMetadata(self):
        """
        Gives all meta data available for the currently played element 
        """
        return self.__mpd.currentsong()
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def GetCaps(self):
        """
        Return the "media player"'s current capabilities
            * CAN_GO_NEXT	There is a current next track, or at least something that equals to it 
              (that is, the remote can call the 'Next' method on the interface, and expect something to happen, heh)
            * CAN_GO_PREV	Same as for NEXT, just previous track/something
            * CAN_PAUSE	Can currently pause. This might not always be possible, and is yet another hint for frontends as to what to indicate
            * CAN_PLAY	Whether playback can currently be started. 
              This might not be the case if e.g. the playlist is empty in a player, 
              or similar conditions. Here, again, it is entirely up to the player to decide when it can play or not, 
              and it should signalize this using the caps API.
            * CAN_SEEK	Whether seeking is possible with the currently played stream (UIs/frontends can then enable/disable seeking controls)
            * CAN_PROVIDE_METADATA	Whether metadata can be acquired for the currently played stream/source using GetMetadata at all.
            * CAN_HAS_TRACKLIST
            	Whether the media player can hold a list of several items 
        """
        res = 0
        #CAN_GO_NEXT
        if ( int(self.__mpd.currentsong()['pos']) < int(self.__mpd.status()['playlistlength']) - 1 ) or ( self.__mpd.status()['repeat'] == 1 ) :
            res += 2
        #CAN_GO_PREV
        if ( int(self.__mpd.currentsong()['pos']) > 0 or ( self.__mpd.status()['repeat'] == 1 ) :
            res += 4
        #CAN_PAUSE
        if ( self.__mpd.status['state'] != 'stop' ):
            res += 8
        #CAN_PLAY
        if ( self.__mpd.status['playlistlength'] != 0 ):
            res += 16
        #CAN_SEEK
        #Can't find why we couldn't seek, except if there is no current song
        if ( self.__mpd.currentsong() != {} ):
            res += 32
        #CAN_PROVIDE_METADATA
        #Why couldn't we provide this ?
            res += 64
        #CAN_HAS_TRACKLIST
        #Why couldn't we provide this ?
            res += 128
        return res
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def VolumeSet(self, level):
        """
        Sets the volume (argument must be in [0;100]) 
        """
        self.__mpd.setvol(level)
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def VolumeGet(self):
        """
        Returns the current volume (must be in [0;100])
        """
        self.__mpd.status()['volume']
        
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')    
    def PositionSet(self, position):
        """
        Sets the playing position (argument must be in [0;<track_length>] in milliseconds) 
        """
        self.__mpd.seekid(int(self.__mpd.currentsong()['id']), position)
    
    @dbus.service.method(dbus_interface='org.freedesktop.MediaPlayer')
    def PositionGet(self):
        """
        Returns the playing position (will be [0;<track_length>] in milliseconds) 
        """
        return self.__mpd.status()['time'].split(':')[0]
    
    @dbus.service.signal(dbus_interface='org.freedesktop.MediaPlayer')    
    def TrackChange(self, items, values):
        """
        Signal is emitted when the "Media Player" plays another "Track". 
        Argument of the signal is the metadata attached to the new "Track"
        """
        res = {}
        for i in range(items.__len__()):
            res[items[i]] = values[i]
        return res
            
    
    @dbus.service.signal(dbus_interface='org.freedesktop.MediaPlayer')    
    def StatusChange(self, state, random, repeat, loop):
        """
        Signal is emitted when the status of the "Media Player" change. 
        The argument has the same meaning as the value returned by GetStatus.
        """ 
        state = {'play':0,'pause':1,'stop':2}
        status = self.__mpd.status()
        return (state[status['state']], int(state['random']), 0, int(state['repeat']))
    
    @dbus.service.signal(dbus_interface='org.freedesktop.MediaPlayer')    
    def CapsChange(self, capabilities):
        """
        Signal is emitted when the "Media Player" changes capabilities, see GetCaps method.
        """
        return 
        
    @dbus.service.signal(dbus_interface='org.freedesktop.MediaPlayer')    
    def  TrackListChange(self, elementsCount):
        """
        Signal is emitted when the "TrackList" content has changed: 
            * When one or more elements have been added
            * When one or more elements have been removed
            * When the ordering of elements has changed
        The argument is the number of elements in the TrackList after the change happened. 
        """
        pass