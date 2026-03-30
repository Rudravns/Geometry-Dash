from utility import *
import pygame
import pygame.mixer
pygame.mixer.init()


class Music:
    def __init__(self, song):
        self.song = song
        self.main_mpath = "asset/Sounds/Music"
        self.speed = 0
        self.song_player = 0

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
        if self.music_playing[self.song]: 
            pygame.mixer.music.play()
            self.song_player = start_pos // 100
        else: 
            pygame.mixer.music.stop()
            self.song_player = 0

    def draw(self, screen, speed, xscroll, spawn_pos):
        if not self.music_playing[self.song]: return False

        self.song_player = (pygame.mixer.music.get_pos() * speed) // 10 + spawn_pos[0] - xscroll

        os.system("cls" if os.name == "nt" else "clear")
        print(round(self.song_player, 2))
        
        pygame.draw.line(screen, (255, 0, 0), (self.song_player, 0), (self.song_player, screen.get_height()), 2)

    def get_frequency(self):
        return pygame.mixer.music.get_volume()
    

class SoundManager:
    def __init__(self):
        """
        :EXAMPLE USAGE: \n
        self.sound = Sound.SoundManager()\n
        self.sound.load_sfx("Hit", "hitHurt.wav")\n
        self.sound.load_sfx("Tree Broken", "Tree_broken.wav")\n
        self.sound.load_sfx("Tree Hit", "Tree_hit.wav")\n
        self.sound.load_sfx("DEATH", "Death.wav")\n
        self.sound.load_sfx("beacon upgrade", "Beacon upgrade.wav")\n
        self.sound.load_sfx("beacon add feul", "beacon_feul.wav")\n
        self.sound.load_music("main menu music", "glacial_ambient.wav")\n

        :CALL: \n
        self.sound.play_sfx("Hit", volume=0.5)\n
        self.sound.play_music("main menu music", loops=-1, volume=0.7, fade_ms=1000)\n
        
        """


        # Initialize the pygame mixer if it hasn't been already
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        # Dictionary to store loaded Sound objects (for SFX)
        self.sfx_dict = {}
        
        # Dictionary to store music file paths (music is streamed, not pre-loaded into memory)
        self.music_dict = {}

    # --- Sound Effects (SFX) Methods ---
    
    def load_sfx(self, name, filename):
        """Loads a sound effect into memory using the load_sound helper."""
        try:
            # We just pass the filename (e.g., "jump.wav") to the helper
            self.sfx_dict[name] = load_sound(filename)
        except FileNotFoundError as e:
            # If load_sound fails, it passes the error message up to here
            print(f"Warning: {e}")

    def play_sfx(self, name, volume=1.0):
        """Plays a loaded sound effect."""
        if name in self.sfx_dict:
            sound = self.sfx_dict[name]
            sound.set_volume(volume)
            sound.play()
        else:
            print(f"Warning: SFX '{name}' not loaded.")

    # --- Background Music (BGM) Methods ---

    def load_music(self, name, filepath):
        """Registers a background music track."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.abspath(
            os.path.join(script_dir, "Assets", "Sounds", "Music")
        )
        final_path = os.path.join(BASE_DIR, filepath)
        if os.path.exists(final_path):
            
            self.music_dict[name] = final_path
        else:
            print(f"Warning: Music file not found at {final_path}")

    def play_music(self, name, loops=-1, volume=1.0, fade_ms=0):
        """Plays a registered music track. loops=-1 plays indefinitely."""
        if name in self.music_dict:
            pygame.mixer.music.load(self.music_dict[name])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
        else:
            print(f"Warning: Music '{name}' not loaded.")

    def stop_music(self, fade_ms=0):
        """Stops the currently playing music."""
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

    def pause_music(self):
        """Pauses the background music."""
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Resumes paused background music."""
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        """Dynamically adjusts the music volume (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(volume)

if __name__ == "__main__":
    p = Music(1)
    p.music_controls()