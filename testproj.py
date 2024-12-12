import pygame
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.fftpack import fft
import numpy as np
import threading
import sounddevice as sd
from pydub import AudioSegment

class EqualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Equalizer")

        # Load Button
        self.load_button = tk.Button(self.root, text="Load MP3", command=self.load_file)
        self.load_button.pack()

        # Play/Pause Buttons
        self.play_button = tk.Button(self.root, text="Play", command=self.play_music)
        self.play_button.pack()
        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_music)
        self.pause_button.pack()

        # Re-open Graph Button
        self.reopen_button = tk.Button(self.root, text="Re-open Graph", command=self.reopen_graph)
        self.reopen_button.pack()

        # Sliders for equalizer bands
        self.sliders = []
        for i in range(10):
            slider = tk.Scale(self.root, from_=0, to=10, orient=tk.HORIZONTAL)
            slider.pack()
            self.sliders.append(slider)

        self.plot_thread = None
        self.running = False
        self.audio_segment = None
        self.chunk_size = 1024  # Reduced chunk size for performance
        self.sample_rate = 44100
        self.audio_data = None
        self.current_pos = 0

        # Initialize the audio playback
        pygame.mixer.init(frequency=self.sample_rate)

    def load_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.audio_segment = AudioSegment.from_file(file_path)
            # Load the file to pygame
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.start_plot_thread()

    def play_music(self):
        pygame.mixer.music.unpause()

    def pause_music(self):
        pygame.mixer.music.pause()

    def start_plot_thread(self):
        if not self.running:
            self.running = True
            self.plot_thread = threading.Thread(target=self.update_plot)
            self.plot_thread.start()

    def update_plot(self):
        fig, ax = plt.subplots()
        x = np.linspace(0.0, self.sample_rate//2, self.chunk_size//2)  # Frequency axis (half)
        line, = ax.plot(x, np.zeros(self.chunk_size//2))

        ax.set_xlim(20, 8000)  # Limit x-axis to 8 kHz (human hearing range)
        ax.set_ylim(0, 1000)    # Adjust amplitude to a lower range for visibility
        ax.set_xscale('log')    # Log scale for the x-axis for better frequency visualization

        def animate(i):
            if not self.running:
                return
            # Capture the audio data in real time from sounddevice
            audio_data = self.get_audio_chunk()
            if audio_data is not None:
                # Perform FFT
                yf = fft(audio_data)
                xf = np.linspace(0.0, self.sample_rate//2, len(yf)//2)  # Adjust frequency axis to match FFT size
                y_data = 2.0/len(audio_data) * np.abs(yf[:len(audio_data)//2])  # Normalize the amplitude

                # Update the plot with the correct data
                line.set_ydata(y_data)  # Update y-values only
            return line,

        ani = FuncAnimation(fig, animate, interval=50)  # Reduce update interval to 50 ms
        plt.show()

    def get_audio_chunk(self):
        if self.audio_segment:
            # Calculate the current chunk to show based on the position in the audio
            start_ms = self.current_pos * (1000 / self.sample_rate)
            end_ms = start_ms + (self.chunk_size * (1000 / self.sample_rate))
            chunk = self.audio_segment[start_ms:end_ms]
            self.current_pos += 1
            if len(chunk) > 0:
                return np.array(chunk.get_array_of_samples())
        return None

    def reopen_graph(self):
        if not self.running:
            self.start_plot_thread()

    def close(self):
        self.running = False
        self.root.quit()
        self.root.destroy()

root = tk.Tk()
app = EqualizerApp(root)
root.protocol("WM_DELETE_WINDOW", app.close)
root.mainloop()
