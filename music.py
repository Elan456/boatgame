import pygame

pygame.mixer.init()

pygame.mixer.music.load("music\\maintheme.mp3")


class Music:
    def __init__(self):
        pygame.mixer.music.play(-1)
        self.song_being_played = None
        self.music_muted = False

    def play_song(self, name):
        # Checking if a new song needs to be loaded
        if self.song_being_played != name and not self.music_muted:
            pygame.mixer.music.load("music\\" + name + ".mp3")
            pygame.mixer.music.play(-1)
            self.song_being_played = name

    def toggle_mute(self):
        if self.music_muted:
            self.music_muted = False
            pygame.mixer.music.unpause()
        else:
            self.music_muted = True
            # Stop playing music
            pygame.mixer.music.pause()
