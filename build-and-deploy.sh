#!/bin/sh
#
# This script builds the game artifacts from the sources, copies them over to
# the Raspberry Pi inside the phone and sets up and restarts the relevant
# service on the device.
#

echo "Stage 1: Build"

# We take the game definition file and generate the WAV files from all of the
# sentences. We also generate a processed version of the game file that replaces
# the game text with file names. These artifacts end up in the build directory.

(
	cd pre-processor
	source venv/bin/activate
	nice python pre-processor.py ../games/first-game.json ../build
)

