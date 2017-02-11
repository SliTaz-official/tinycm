#!/bin/sh
#
# TinyCM/TazBug Plugin - Skeleton
#

if [ "$(GET skel)" ]; then
	d="Skel"
	header
	html_header
	user_box
	echo "<h2>Plugin Skel</h2>"
	echo $(date)
	
	# Let's code!
	
	html_footer
	exit 0
fi
