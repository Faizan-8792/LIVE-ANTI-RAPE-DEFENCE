import pygame
import threading

siren_playing = False

def play_siren():
    global siren_playing
    if siren_playing:
        return
    siren_playing = True

    def siren():
        pygame.mixer.init()
        pygame.mixer.music.load("siren.wav")
        pygame.mixer.music.play(-1)

    threading.Thread(target=siren).start()

def stop_siren():
    global siren_playing
    if siren_playing:
        pygame.mixer.music.stop()
        siren_playing = False
        print("🛑 Siren stopped manually.")
