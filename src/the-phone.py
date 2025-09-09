import os
import json
import hashlib
import subprocess
import numpy as np
import soundfile as sf
import sounddevice as sd

GAME_DIR = "../games"
AUDIO_DIR = "../.cache/audio"

SAMPLE_RATE = 8000 # Hz

def ensure_audio_dir():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

# XXX I prefer role-based cache file naming, but this will work for now...
# Stable filename based on hash of the phrase
def text_to_filename(text):
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    return f"{AUDIO_DIR}/{h}.wav"


# XXX Keep files in memory..

def generate_audio(text):
    """Generate audio for a phrase if not already cached."""
    filename = text_to_filename(text)
    if not os.path.exists(filename):
        print(f"generating {filename}...")

        subprocess.run(
            f'espeak "{text}" -v en --stdout | sox -r 22050 -t wav - -r {SAMPLE_RATE} -c 1 -b 16 "{filename}"',
            shell=True,
            check=True
        )

    return filename


def play_audio(filename):
    data, samplerate = sf.read(filename, dtype="float32", always_2d=False)
    print(f"playing {filename}@{samplerate} Hz...")
    if samplerate != SAMPLE_RATE:
        print(f"sample rate mismatch on {filename}: expected {SAMPLE_RATE}, found {samplerate}.")

    data = data * 6.0
    data = np.clip(data, -1.0, 1.0)

    sd.play(data, SAMPLE_RATE, device=0, blocking=True)


def preload_all_audio(game_state):
    for loc, node in game_state.items():
        generate_audio(node["description"])
        for phrase in node["prompt_phrases"]:
            generate_audio(phrase)
        for option in node["options"].values():
            generate_audio(option["option_phrase"])
            generate_audio(option["response_phrase"])


def play_game(game_state, start="Study"):
    location = start
    while True:
        node = game_state[location]

        play_audio(generate_audio(node["description"]))

        for option in node["options"].values():
            play_audio(generate_audio(option["option_phrase"]))

        choice = None
        while choice not in node["options"]:
            try:
                choice = input("Dial (type) a number: ").strip()
            except EOFError:
                return

        play_audio(generate_audio(node["options"][choice]["response_phrase"]))
        location = node["options"][choice]["next_location"]

def main():
    with open(f"{GAME_DIR}/first-game.json", "r", encoding="utf-8") as f:
        game_state = json.load(f)

    print("Default samplerate:", sd.default.samplerate)
    print("Default blocksize:", sd.default.blocksize)
    print("Default latency:", sd.default.latency)
    print("\nDefault output device:", sd.default.device)
    print("Device info:", sd.query_devices())

    # XXX search for and pre-select headphone device

    ensure_audio_dir()
    preload_all_audio(game_state)

    play_game(game_state)

if __name__ == "__main__":
    main()

