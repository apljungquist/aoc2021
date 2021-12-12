# Configuration
# =============

# Have zero effect by default to prevent accidental changes.
.DEFAULT_GOAL := none

# Delete targets that fail to prevent subsequent attempts incorrectly assuming
# the target is up to date.
.DELETE_ON_ERROR: ;

# Prevent pesky default rules from creating unexpected dependency graphs.
.SUFFIXES: ;


# Verbs
# =====

.PHONY: none

none:
	@echo No target specified


# Nouns
# =====

constraints.txt:  $(wildcard requirements/*.txt)
	pip-compile --allow-unsafe --no-header --output-file $@ $^

requirements.txt: $(wildcard requirements/*.txt)
	echo $^ | tr " " "\n" | sed -e 's/^/-r/g' > $@
