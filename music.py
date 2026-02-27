from utility import *
import pygame
import pygame.mixer
pygame.mixer.init()

class Music:
    def __init__(self, song):
        self.song = song
        self.main_pathway = "asset/Sounds"

        self.musics:dict = {
            "Level 1" : f"{self.main_pathway}/Music/level1.wav",
            "Level 2" : f"{self.main_pathway}/Music/level2.wav",
            "Level 3": f"{self.main_pathway}/Music/level3.wav"
        } #write path in here for each song

        self.music_playing:list = [False, False, False] #one for each song in the song list

    def music_controls(self, start_pos = 0):
        self.music_playing[self.song] = not self.music_playing[self.song]
        file = self.musics[f"Level {self.song}"]
        file.set_volume(100)
        if self.music_playing[start_pos]:
            file.play(loops=0, start=start_pos)
        else:
            file.stop()