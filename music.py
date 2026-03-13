from utility import *
import pygame
import pygame.mixer
pygame.mixer.init()

class Music:
    def __init__(self, song):
        self.song = song
        self.main_mpath = "asset/Sounds/Music"
        self.speed = 0

        self.musics:dict = {
            "Level 1" : f"{self.main_mpath}/level1.mp3",
            "Level 2" : f"{self.main_mpath}/level2.mp3",
            "Level 3" : f"{self.main_mpath}/level3.mp3"
        } #write path in here for each song

        self.music_playing:list = [False, False, False] #one for each song in the song list

    def music_controls(self, start_pos = 0):
        self.music_playing[self.song] = not self.music_playing[self.song]
        file = self.musics[f"Level {self.song}"]

        pygame.mixer.music.load(file)
        if self.music_playing[self.song]: pygame.mixer.music.play()
        else: pygame.mixer.music.stop()

    def draw(self, screen, speed, xscroll):
        if not self.music_playing[self.song]: return False

        linex = (pygame.mixer.music.get_pos() + speed) / 10 - xscroll

        os.system("cls" if os.name == "nt" else "clear")
        print(round(linex, 2))
        
        pygame.draw.line(screen, (255, 0, 0), (linex, 0), (linex, screen.get_height()), 2)

    def get_frequency(self):
        return pygame.mixer.music.get_volume()

if __name__ == "__main__":
    p = Music(1)
    p.music_controls()