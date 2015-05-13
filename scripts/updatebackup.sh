#!/bin/bash

# rsync keeps second location in sync with first.
# -a: archive mode, which means symbolic links, devices, attributes, permissions, ownerships and so forth are preserved. This also includes recursive checks.
# -v: verbose
# -z: compress file data during the transfer
# -h: help?
rsync -avzh abe@projects.thelensnola.org:/backups/contracts /Volumes/bigone/lensdata
