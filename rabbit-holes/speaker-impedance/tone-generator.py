import numpy as np
import sounddevice as sd

samplerate = 44100
frequency = 1000
amplitude = 0.2

t = np.arange(0, samplerate) / samplerate
base_waveform = np.sin(2 * np.pi * frequency * t)

devices = sd.query_devices()
print(devices)
jack_index = None
for i, d in enumerate(devices):
    print(d)
    print(d["name"])
    if "headphone" in d["name"].lower():
        jack_index = i
        break

if jack_index is None:
    raise RuntimeError("No headphone jack device found")

sd.default.device = jack_index

def callback(outdata, frames, time, status):
    global amplitude
    outdata[:] = (amplitude * base_waveform[:frames]).reshape(-1, 1)

with sd.OutputStream(channels=1, samplerate=samplerate, callback=callback):
    try:
        while True:
            val = input("Volume (0.0–1.0): ")
            amplitude = max(0.0, min(1.0, float(val)))
    except KeyboardInterrupt:
        pass
