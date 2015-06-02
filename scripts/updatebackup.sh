#!/bin/bash

# To be run from one level up

# rsync keeps second location in sync with first.
# -a: archive mode, which means symbolic links, devices, attributes, permissions, ownerships and so forth are preserved. This also includes recursive checks.
# -v: verbose
# -z: compress file data during the transfer
# -h: human-readable output
rsync -avz root@vault.thelensnola.org:/backups/contracts backup
