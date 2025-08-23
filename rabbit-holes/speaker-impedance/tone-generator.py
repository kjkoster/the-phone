import numpy as np
import sounddevice as sd

samplerate = 44100
frequency = 1000
amplitude = 0.2
phase = 0.0
phase_increment = 2 * np.pi * frequency / samplerate

devices = sd.query_devices()
jack_index = None
for i, d in enumerate(devices):
    print(d)
    if "headphone" in d["name"].lower():
        jack_index = i
        break

if jack_index is None:
    raise RuntimeError("No headphone jack device found")

sd.default.device = jack_index

def callback(outdata, frames, time, status):
    global phase, amplitude
    t = phase + np.arange(frames) * phase_increment
    outdata[:, 0] = amplitude * np.sin(t)
    phase = (t[-1] + phase_increment) % (2 * np.pi)

with sd.OutputStream(channels=1, samplerate=samplerate, callback=callback):
    try:
        while True:
            val = input("Volume (0.0–1.0): ")
            amplitude = max(0.0, min(1.0, float(val)))
    except KeyboardInterrupt:
        pass
