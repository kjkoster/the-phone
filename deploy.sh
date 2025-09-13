#!/bin/sh
#
# This script builds the game artifacts from the sources, copies them over to
# the Raspberry Pi inside the phone and sets up and restarts the relevant
# service on the device.
#

if [ ${#} -ne 1 ]; then
	echo "usage: deploy.sh <hostname>"
	exit 1
fi
HOST=${1}
DEPLOYDIR=/home/the-phone

echo "Stage 1: Build"

# We take the game definition file and generate the WAV files from all of the
# sentences. We also generate a processed version of the game file that replaces
# the game text with file names. These artifacts end up in the build directory.

(
	cd pre-processor
	source venv/bin/activate
	nice python pre-processor.py ../games/first-game.json ../build
)

echo ""
echo "Stage 2: Deploying to ${HOST}:${DEPLOYDIR}"

# With all the voice clips generated, it is time to copy everything over to the
# Raspberry Pi inside the telephone.

scp build/* src/requirements.txt src/the-phone.py the-phone.service ${HOST}:${DEPLOYDIR}

echo ""
echo "Stage 3: Install Virtual Environment"

# With all the files on the phone's Raspberry Pi, set up a virtual environment
# for the game to run in.

ssh ${HOST} /bin/bash << EOF
cd ${DEPLOYDIR}
sudo apt-get install -y portaudio19-dev python3-gpiozero
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF

echo ""
echo "Stage 4: Daemonise"

# Finally, set up the service daemon to run the game continuously.

ssh ${HOST} /bin/bash << EOF
sudo cp ${DEPLOYDIR}/the-phone.service /etc/systemd/system/the-phone.service
sudo systemctl daemon-reload
sudo systemctl enable the-phone.service
sudo systemctl stop the-phone.service
sudo systemctl start the-phone.service
EOF
