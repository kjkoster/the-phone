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

echo ""
echo "Stage 2: Deploy"

# With all the voice clips generated, it is time to copy everything over to the
# Raspberry Pi inside the telephone.

DEPLOYDIR=/usr/local/the-phone

ssh phonepi.local sudo mkdir -p ${DEPLOYDIR}
ssh phonepi.local sudo chown kjkoster:kjkoster ${DEPLOYDIR}
scp build/* src/requirements.txt src/the-phone.py the-phone.service phonepi.local:${DEPLOYDIR}

echo ""
echo "Stage 3: Install Virtual Environment"

# With all the files on the phone's Raspberry Pi, set up a virtual environment
# for the game to run in.

ssh phonepi.local /bin/bash << EOF
cd ${DEPLOYDIR}
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF

echo ""
echo "Stage 4: Daemonise"

# Finally, set up the service daemon to run the game continuously.

ssh phonepi.local /bin/bash << EOF
sudo cp ${DEPLOYDIR}/the-phone.service /etc/systemd/system/the-phone.service
sudo systemctl daemon-reload
sudo systemctl enable the-phone.service
sudo systemctl stop the-phone.service
sudo systemctl start the-phone.service
EOF
