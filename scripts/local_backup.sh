#!/bin/bash

# Run this manually from local computer from time to time.

source `which virtualenvwrapper.sh`

workon contracts

### Copy server backup files to local directory ###
rsync -avzh root@vault.thelensnola.org:/backups/contracts/ $PYTHONPATH/backup/
# rsync keeps second location in sync with first.
# -a: archive mode, which means symbolic links, devices, attributes, permissions, ownerships and so forth are preserved. This also includes recursive checks.
# -v: verbose
# -z: compress file data during the transfer
# -h: human-readable output

deactivate
