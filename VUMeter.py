import numpy as np
import pyaudio
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class RealTimeVUMeter:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time VU Meter")

        # Matplotlib figure setup
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_ylim(100, 160)  # Adjusted amplitude range for better detail
        self.ax.set_xlim(20, 20000)  # Frequency range (20 Hz to 20 kHz)
        self.ax.set_xscale("log")  # Logarithmic scale for frequency
        self.ax.set_yscale("log")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Amplitude")

        self.frequency_bands = np.logspace(np.log10(20), np.log10(20000), num=25)
        self.amplitudes = np.zeros_like(self.frequency_bands)

        # Create bar plot for VU meter
        self.bars = self.ax.bar(
            self.frequency_bands,
            self.amplitudes,
            width=np.diff(
                np.concatenate(([self.frequency_bands[0]], self.frequency_bands))
            ),
            align="edge",
            color="green",
            edgecolor="black",
        )

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Audio stream setup
        self.sample_rate = 44100
        self.chunk_size = 2048
        self.p = pyaudio.PyAudio()

        # List available audio input devices and prompt the user to select one
        self.input_device_index, self.channels = self.get_system_audio_device_index()

        # Open the audio stream
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.input_device_index,
            frames_per_buffer=self.chunk_size,
        )

        # Start updating the VU meter
        self.update_vu_meter()

    def get_system_audio_device_index(self):
        """
        List available audio devices and find the index for the system audio loopback.
        """
        print("Available audio devices:")
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            print(f"{i}: {info['name']}, Max Input Channels: {info['maxInputChannels']}")

        print("\nEnter the device index for system audio loopback:")
        device_index = int(input())

        # Get the maximum input channels for the selected device
        max_channels = self.p.get_device_info_by_index(device_index)["maxInputChannels"]

        if max_channels == 0:
            raise ValueError("Selected device does not support audio input.")

        return device_index, min(max_channels, 2)  # Use at most 2 channels (stereo)

    def update_vu_meter(self):
        try:
            # Read audio data from the input stream
            audio_chunk = np.frombuffer(
                self.stream.read(self.chunk_size, exception_on_overflow=False), dtype=np.int16
            )

            # If stereo, average the channels to convert to mono
            if self.channels == 2:
                audio_chunk = audio_chunk.reshape(-1, 2)
                audio_chunk = audio_chunk.mean(axis=1).astype(np.int16)

            # Perform FFT to get the frequency spectrum
            spectrum = np.abs(np.fft.rfft(audio_chunk))
            freqs = np.fft.rfftfreq(len(audio_chunk), d=1 / self.sample_rate)

            # Compute the amplitudes for each frequency band
            self.amplitudes = self.get_band_amplitudes(freqs, spectrum)

            # Update the bar heights
            for bar, height in zip(self.bars, self.amplitudes):
                bar.set_height(height)

            # Redraw the canvas
            self.canvas.draw()

            # Schedule the next update
            self.root.after(10, self.update_vu_meter)
        except Exception as e:
            print(f"Error: {e}")
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

    def get_band_amplitudes(self, freqs, spectrum):
        amplitudes = np.zeros_like(self.frequency_bands)

        # Calculate amplitude in each frequency band
        for i, band in enumerate(self.frequency_bands):
            lower_bound = band / np.sqrt(10)
            upper_bound = band * np.sqrt(10)

            band_indices = np.where((freqs >= lower_bound) & (freqs <= upper_bound))[0]
            if len(band_indices) > 0:
                amplitudes[i] = np.sum(spectrum[band_indices])

        # Normalize amplitudes
        # MIGHT CHANGE AGAIN, WAS CAUSING PROBLEMS WITH MAXING OUT VALUES TOO LOW
        """
        if np.max(amplitudes) > 0:
            amplitudes /= np.max(amplitudes)

        return amplitudes
        """
        #NOW DISPLAYS VALUES IN DECIBALS, AND SINCE VOLUME IS LOGARITHMIC, IT NOW DISPLAYS LOGARITHMICALLY
        amplitudes_db = 20 * np.log10(amplitudes + 1e-12)

        amplitudes_db = np.clip(amplitudes_db, 100, 160)

        return amplitudes_db

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeVUMeter(root)
    root.mainloop()
