#!/bin/bash

# Installs parsedatetime and google api python modules.  Copies gtasks.py to executable path.


die() { echo "$@" 1>&2 ; exit 1; }


TOY_LOC="/usr/local/bin"
TMP_DIR="/tmp/gtasksinstall"
echo "==> If prompted, enter your user password or computer login password here."
echo "===> Why? Some of the libraries required have to be installed at the system level."
sudo rm -rf ${TMP_DIR}

sudo cp -f gtasks.py ${TOY_LOC}
sudo chmod +x ${TOY_LOC}/gtasks.py

[ -e /usr/bin/git ] || die "You need to install git first." 
mkdir ${TMP_DIR} 2>/dev/null
[ -d ${TMP_DIR} ] || die "Error creating ${TMP_DIR}" 

cd ${TMP_DIR}
git clone https://github.com/bear/parsedatetime.git

cd ${TMP_DIR}/parsedatetime
sudo python setup.py install
python -c "import parsedatetime" || die "Unable to install parsedatetime module"

cd ${TMP_DIR}
git clone https://github.com/google/google-api-python-client.git
cd ${TMP_DIR}/google-api-python-client
sudo python setup.py install
python -c "import oauth2client" || die "Unable to install google-api-python-client module"

echo "---"
echo "DONE! gtasks is now installed in ${TOY_LOC}"
echo "Next, open the gtasks-alfred.workflow file in the alfred/ subdirectory if you want to use Alfred."

