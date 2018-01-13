PROJECT_DIR=`pwd`

# Keep intermediate files
.SECONDARY:

.PHONY: help test

.DEFAULT_GOAL := help

help:  ## Prints help list for targets.
	@# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

test:  ## Run tests.
	@coverage run --source=contracts -m unittest
