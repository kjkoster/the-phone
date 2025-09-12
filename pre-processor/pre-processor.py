#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import subprocess
from TTS.api import TTS


SAMPLE_RATE = 8000  # Hz

# hangs on phonemes
# tts = TTS(model_name="tts_models/en/ek1/tacotron2")

# too American
# tts = TTS(model_name="tts_models/en/ljspeech/vits")

tts = TTS("tts_models/en/vctk/vits")
print("Available speakers:", tts.speakers)
# see https://huggingface.co/NeuML/vctk-vits-onnx
SPEAKER = 'p263'

def generate_audio(text, build_dir):
    hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    filename = f"{hash}.wav"
    tempfile = f"{build_dir}/{hash}_22050.wav"
    outputfile = f"{build_dir}/{filename}"

    if os.path.exists(outputfile):
        print(f"skipping {outputfile}, since it was already generated...")
    else:
        print(f"generating {outputfile}...")
        if os.path.exists(tempfile):
            os.remove(tempfile)
        tts.tts_to_file(text=text, speaker=SPEAKER, file_path=tempfile)
        subprocess.run(
            f'sox "{tempfile}" -r {SAMPLE_RATE} -c 1 -b 16 "{outputfile}"',
            shell=True,
            check=True,
        )
        os.remove(tempfile)

    return filename


def process_game(game_state, build_dir):
    processed = {}

    for loc, node in game_state.items():
        new_node = {}
        new_node["description"] = generate_audio(node["description"], build_dir)

        new_node["options"] = {}
        for key, option in node["options"].items():
            new_node["options"][key] = {
                "option_phrase": generate_audio(option["option_phrase"], build_dir),
                "response_phrase": generate_audio(option["response_phrase"], build_dir),
                "next_location": option["next_location"],
            }

        processed[loc] = new_node

    return processed


def main():
    if len(sys.argv) != 3:
        print("Usage: pre-processor.py <input_game.json> <build_dir>")
        sys.exit(1)

    build_dir = sys.argv[2]
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as f:
        game_state = json.load(f)

    processed = process_game(game_state, build_dir)

    game_file = f"{build_dir}/game.json"
    print(f"Writing processed game definition to {game_file}...")
    with open(game_file, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()

