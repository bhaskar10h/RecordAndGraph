# python -m pip install pyaudio matplotlib numpy simpleaudio scipy
import pyaudio
import wave
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import simpleaudio as sa
from scipy import signal

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

pa = pyaudio.PyAudio()

stream = pa.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)

print('start recording')

seconds = 8
frames = []
second_tracking = 0
second_count = 0
for i in range(0, int(RATE / FRAMES_PER_BUFFER * seconds)):
    data = stream.read(FRAMES_PER_BUFFER)
    frames.append(data)
    second_tracking += 1
    if second_tracking == RATE / FRAMES_PER_BUFFER:
        second_count += 1
        second_tracking = 0
        print(f'Time Left: {seconds - second_count} seconds')

stream.stop_stream()
stream.close()
pa.terminate()

# Save audio to WAV file
obj = wave.open('lemaster_tech.wav', 'wb')
obj.setnchannels(CHANNELS)
obj.setsampwidth(pa.get_sample_size(FORMAT))
obj.setframerate(RATE)
obj.writeframes(b''.join(frames))
obj.close()

# Read audio file for plotting
file = wave.open('lemaster_tech.wav', 'rb')

sample_freq = file.getframerate()
frames = file.getnframes()
signal_wave = file.readframes(-1)

file.close()

time = frames / sample_freq

# if one channel use int16, if 2 use int32
audio_array = np.frombuffer(signal_wave, dtype=np.int16)

times = np.linspace(0, time, num=frames)

# Plot recorded audio in real-time
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

line1, = ax1.plot([], [])
ax1.set_ylabel('Signal Wave')
ax1.set_xlabel('Time (s)')
ax1.set_xlim(0, time)
ax1.set_title('The Thing I Just Recorded!!')

line2, = ax2.plot([], [])
ax2.set_ylabel('Frequency [Hz]')
ax2.set_xlabel('Time [sec]')
ax2.set_title('Spectrogram')

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2

def update(frame):
    line1.set_xdata(times[:frame])
    line1.set_ydata(audio_array[:frame])

    f, t, Sxx = signal.spectrogram(audio_array[:frame], fs=sample_freq, nperseg=256, noverlap=128)
    line2.set_data(t, f)

    return line1, line2

ani = animation.FuncAnimation(fig, update, frames=len(times), init_func=init, blit=True)

# Save additional metadata
metadata = {
    'date': '2023-12-03',
    'time': '14:30:00',
    'duration': f'{seconds} seconds',
    'sample_rate': f'{RATE} Hz',
    'channels': f'{CHANNELS} channel(s)',
}

with open('metadata.txt', 'w') as f:
    for key, value in metadata.items():
        f.write(f'{key}: {value}\n')

# Playback recorded audio
play_obj = sa.play_buffer(audio_array, num_channels=CHANNELS, bytes_per_sample=2, sample_rate=RATE)
play_obj.wait_done()

plt.show()
