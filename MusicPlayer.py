import pygame
from tkinter import Tk, filedialog, Button, Scale, Frame, VERTICAL
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Initialize Pygame
pygame.mixer.init()

# Set default volume to 100%
pygame.mixer.music.set_volume(1.0)

# Function to open a file dialog, select a music file, and play it
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        play_pause_button.config(text="Pause")

# Function to play or pause the music
def play_pause_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        play_pause_button.config(text="Play")
    else:
        pygame.mixer.music.unpause()
        play_pause_button.config(text="Pause")

# Function to restart the music
def restart_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.play()
    play_pause_button.config(text="Pause")

# Function to fast forward the music by 5 seconds
def fast_forward_music():
    pos = pygame.mixer.music.get_pos() / 1000 + 5
    pygame.mixer.music.set_pos(pos)

# Function to set the volume
def set_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

# Create a simple GUI
root = Tk()
root.title("Music Player")

# Frame to hold buttons horizontally
frame = Frame(root)
frame.pack()

# Add buttons for opening file, play/pause, restart, and fast forward
Button(frame, text="Open", command=open_file).pack(side="left")
play_pause_button = Button(frame, text="Play", command=play_pause_music)
play_pause_button.pack(side="left")
Button(frame, text="Restart", command=restart_music).pack(side="left")
Button(frame, text="Fast Forward", command=fast_forward_music).pack(side="left")

# Add a vertical volume control slider with correct volume logic
volume_slider = Scale(root, from_=100, to=0, orient=VERTICAL, label="Volume", command=set_volume)
volume_slider.pack(side="left")
volume_slider.set(100)

# Run the Tkinter event loop
root.mainloop()
