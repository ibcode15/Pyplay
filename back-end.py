
import time
import scrapetube
import vlc
import pafy
import random
from urllib.parse import urlsplit, parse_qs
import threading
from pynput import keyboard

class Song:
    def __init__(self, YTID):
        self.YTID = YTID
        self.Init()
        self.CurrentTime = 0
    def GetLink(self, YTID):
        self.video = pafy.new(YTID, ydl_opts={'nocheckcertificate': True})
        self.title = self.video.title
        self.best = self.video.getbestaudio()
        return self.best.url
    def BreakDownQuery(self,link):
        return parse_qs(urlsplit(link).query)
    def IsLinkValid(self):
        return int(time.time()) < int(self.CurrentQuery['expire'][0])
    def Init(self):
        self.MP3link = self.GetLink(self.YTID)
        self.CurrentQuery = self.BreakDownQuery(self.MP3link)
        self.LinkValid = self.IsLinkValid()
        self.Player = vlc.MediaPlayer(self.MP3link) 
    def Play(self):
        if not self.IsLinkValid():
            print("test")
            Init()
        self.Player.play()
        self.Player.set_time(self.CurrentTime)
        
    #def Set(self,ms):
    #    self.Player.set_time(ms)
    def Change(self,amount_in_ms): 
        self.CurrentTime = self.Player.get_time() + amount_in_ms
        self.Player.set_time(self.CurrentTime)
    def Stop(self):
        self.Player.stop()
        self.CurrentTime = self.Player.get_time()
    def State(self):
        return self.Player.get_state()
    def Pause(self):
        self.Player.pause()
        self.CurrentTime = self.Player.get_time()
    def __str__(self):
        return f"Song(Name={self.title} ID={self.YTID})"
    def __repr__(self):
        return f"Song(Name={self.title} ID={self.YTID})"
    
class PlayList:
    def __init__(self, PlayListID,log=True,autoplay=True, Keyboard=True):
        self.PlayList = scrapetube.get_playlist(PlayListID)
        self.music = []
        self.log = log
        self.autoplay = autoplay
        for track in self.PlayList:
            if self.log:
                print(f'[Loading] {track["title"]["runs"][0]["text"]}') 
            self.music.append(Song(track['videoId']))
        del self.PlayList
        self.SongPointer = 0
        self.threads = []
        if autoplay:
            self.Autoplaythread = threading.Thread(target=self.autoplayFunc)
            self.Autoplaythread.start()
            self.threads.append(self.Autoplaythread)
        if Keyboard:
            self.Keyboardlistener = keyboard.Listener(on_press=self.on_press)
            self.Keyboardlistener.start()
            self.threads.append(self.Keyboardlistener)
        for t in self.threads:
            t.join()
                
        
    def on_press(self,key):
        if key == keyboard.Key.right and not (self.music[self.SongPointer].State() == vlc.State.Stopped):
            self.music[self.SongPointer].Change(5000)
        elif key == keyboard.Key.left:
            self.music[self.SongPointer].Change(-5000)
        elif key == keyboard.Key.space:
            if self.music[self.SongPointer].State() == vlc.State.Playing:
                self.music[self.SongPointer].Pause()
            else:
                self.music[self.SongPointer].Play()
        
    def shuffle(self):
        if not (self.music[self.SongPointer].State() == vlc.State.Stopped):
            self.Stop()
        random.shuffle(self.music)
        self.SongPointer = 0
        if self.autoplay:
            self.Play()
    def autoplayFunc(self):
        self.Play()
        while True:
            if self.music[self.SongPointer].State() == vlc.State.Ended:
                if self.SongPointer == len(self.music):
                    self.Reset()
                else:
                    self.Next()
    def Play(self):
        if self.log:
            print(f"[Playing] {self.music[self.SongPointer].title}") 
        self.music[self.SongPointer].Play()
    def Stop(self):
        if self.log:
            print(f"[Stop] {self.music[self.SongPointer].title}") 
        self.music[self.SongPointer].Stop()
    def Pause(self):
        if self.log:
            print(f"[Pause] {self.music[self.SongPointer].title}") 
        self.music[self.SongPointer].Pause()
    def GoTo(self,songindex):
        if songindex > len(self.music):
            if autoplay:
                print("[Error] Index too big")
        else:
            self.SongPointer = songindex
            
    def Reset(self):
        self.Stop()
        self.SongPointer = 0
        if self.autoplay:
            self.Play()
    def Next(self):
        self.Stop()
        self.SongPointer += 1
        if self.autoplay:
            self.Play()
        
        
