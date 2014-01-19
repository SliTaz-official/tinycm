#!/bin/sh
#
# Update a TinyCM install with latest code from Hg.
# Usage: ./tools/update.sh [paths]
#
. /lib/libtaz.sh

[ ! "$1" ] && echo "Missing TinyCM path(s)" && exit 0

# We dont overwrite style.css and images since they may have changed
# as well as the config file!
for cm in $@
do
	echo "Updating: $cm"
	cp -a index.cgi ${cm}
	cp -a plugins ${cm}
	cp -a lib/functions.js ${cm}/lib
	cp -a lib/jseditor.html ${cm}/lib
done

exit 0
