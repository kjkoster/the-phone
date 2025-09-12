import os
import json
import time
import hashlib
import subprocess
import soundfile as sf
import sounddevice as sd
from gpiozero import Button

SAMPLE_RATE = 8000 # Hz

running = False

TOGGLE_A1_GPIO = 17
RADIO_A2_GPIO  = 27
RADIO_B_GPIO   = 22
SWITCH_C1_GPIO = 23
SWITCH_C2_GPIO = 24
SWITCH_C3_GPIO = 25
SWITCH_C4_GPIO = 8
SWITCH_C5_GPIO = 7

toggle_a1  = None
radio_a2   = None
radio_b    = None
switch_c1  = None
switch_c2  = None
switch_c3  = None
switch_c4  = None
switch_c5  = None

AUDIO_CACHE = {}

def load_audio(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Missing audio file: {filename}")

    data, samplerate = sf.read(filename, dtype="float32", always_2d=False)
    if samplerate != SAMPLE_RATE:
        print(f"sample rate mismatch on {filename}: expected {SAMPLE_RATE}, found {samplerate}.")

    AUDIO_CACHE[filename] = data


def play_audio(filename):
    data = AUDIO_CACHE[filename]
    print(f"playing {filename}...")
    sd.play(data, SAMPLE_RATE, device=0, blocking=True)


def preload_all_audio(game_state):
    for loc, node in game_state.items():
        load_audio(node["description"])
        for option in node["options"].values():
            load_audio(option["option_phrase"])
            load_audio(option["response_phrase"])


def play_game(game_state, start="Study"):
    location = start
    while True:
        node = game_state[location]

        play_audio(node["description"])

        for option in node["options"].values():
            play_audio(option["option_phrase"])

        choice = None
        while choice not in node["options"]:
            if switch_c1.is_pressed:
                choice = '1'
            elif switch_c2.is_pressed:
                choice = '2'
            elif switch_c3.is_pressed:
                choice = '3'
            else:
                time.sleep(0.05)

        play_audio(node["options"][choice]["response_phrase"])
        location = node["options"][choice]["next_location"]


def gpio_setup():
    global toggle_a1
    global radio_a2
    global radio_b
    global switch_c1
    global switch_c2
    global switch_c3
    global switch_c4
    global switch_c5

    toggle_a1 = Button(TOGGLE_A1_GPIO, pull_up=True, bounce_time=0.2)

    def a1_pressed():
        global running
        print("GPIO went LOW → starting program")
        running = True

    def a1_on_hook():
        print("GPIO went HIGH → shutting down")
        running = False
        os._exit(0)

    toggle_a1.when_pressed = a1_pressed
    toggle_a1.when_released = a1_on_hook

    radio_a2 = Button(RADIO_A2_GPIO, pull_up=True, bounce_time=0.2)

    radio_b = Button(RADIO_B_GPIO, pull_up=True, bounce_time=0.2)

    switch_c1 = Button(SWITCH_C1_GPIO, pull_up=True, bounce_time=0.2)
    switch_c2 = Button(SWITCH_C2_GPIO, pull_up=True, bounce_time=0.2)
    switch_c3 = Button(SWITCH_C3_GPIO, pull_up=True, bounce_time=0.2)
    switch_c4 = Button(SWITCH_C4_GPIO, pull_up=True, bounce_time=0.2)
    switch_c5 = Button(SWITCH_C5_GPIO, pull_up=True, bounce_time=0.2)


def main():
    global running
    gpio_setup()

    with open("game.json", "r", encoding="utf-8") as f:
        game_state = json.load(f)

    print("Default samplerate:", sd.default.samplerate)
    print("Default blocksize:", sd.default.blocksize)
    print("Default latency:", sd.default.latency)
    print("\nDefault output device:", sd.default.device)
    print("Device info:", sd.query_devices())

    # XXX search for and pre-select headphone device

    preload_all_audio(game_state)

    print("Waiting for GPIO toggle to go LOW...")
    while not running:
        time.sleep(0.1)

    play_game(game_state)

if __name__ == "__main__":
    main()

