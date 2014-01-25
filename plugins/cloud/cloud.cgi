#!/bin/sh
#
# TinyCM Plugin - Upload files to the Cloud
#
. /usr/lib/slitaz/httphelper

cloud="$tiny/$content/cloud"
cloudlog="$tiny/$cache/log/cloud.log"

case " $(GET) " in
	*\ upcloud\ *)
		# Have a variable in config file for the content/cloud path ?
		[ ! check_auth ] && header "Location: $HTTP_REFERER"
		[ ! "$(FILE datafile name)" ] && header "Location: $HTTP_REFERER"
		user="$(GET user)"
		cloud="../../content/cloud"
		cloudlog="../../cache/log/cloud.log"
		name=$(FILE datafile name)
		tmpname=$(FILE datafile tmpname)
		# Sanity check
		[ ! -d "$cloud" ] && mkdir -p ${cloud}
		[ ! -f "$cloudlog" ] && touch ${cloudlog}
		# Move/Overwrite files to the cloud and set permissions
		if ! mv -f ${tmpname} ${cloud}/${name}; then
			echo "ERROR: ${name}" && exit 1
		fi
		chmod a+r ${cloud}/${name}
		# Log activity
		cat >> ${cloudlog} << EOT
$(date '+%Y-%m-%d %H:%M') : <a href="content/cloud/${name}">${name}</a> \
$(gettext "uploaded by:") <a href="index.cgi?user=$user">$user</a>
EOT
		# Back to the cloud
		header "Location: $HTTP_REFERER" ;;
		
	*\ rmcloud\ *)
		user="$(GET user)"
		name="$(GET name)"
		rm -f "$cloud/$name"
		# Log activity
		cat >> ${cloudlog} << EOT
$(date '+%Y-%m-%d %H:%M') : $name $(gettext "removed by:") \
<a href="index.cgi?user=$user">$user</a>
EOT
		# Back to the cloud
		header "Location: $HTTP_REFERER" ;;
		
	*\ cloudlog\ *)
		# Display Cloud activity
		d="Cloud activity"
		[ ! check_auth ] && header "Location: $script"
		# Clean-up logfile
		if [ "$(GET clean)" ]; then
			rm -f ${cloudlog} && touch ${cloudlog}
			header "Location: $HTTP_REFERER"
		fi
		header
		html_header
		user_box
		echo "<h2>$(gettext "Cloud activity")</h2>"
		echo '<pre>'
		if [ "$(GET full)" ]; then
			tac ${cloudlog}
		else
			tac ${cloudlog} | head -n 20
		fi
		echo '</pre>'
		cat << EOT
<div id="tools">
	<a href="$script?cloud">Cloud files</a>
	<a href="$script?cloudlog&amp;full">$(gettext "More activity")</a>
	<a href="$script?cloudlog&amp;clean">$(gettext "Clean logfile")</a>
</div>
EOT
		html_footer && exit 0 ;;
		
	*\ cloud\ *)
		# The dashboard
		d="Cloud files"
		files=$(ls -1 $cloud | wc -l)
		size=$(du -sh $cloud | awk '{print $1}')
		header
		html_header
		user_box
		# Security check
		if ! check_auth; then
			gettext "You must be logged in to use the Cloud."
			exit 1
		fi
		cat << EOT
<div id="tools">
	<a href="$script?cloudlog">Activity</a>
	<a href="$content/cloud">Raw files</a>
</div>

<h2>Cloud files</h2>

<p>
$(gettext "Upload files on the cloud to share them with some other people
or use them in your documents content. Tip: Drag and Drop files from your
desktop.")
</p>
<div style="text-align: center;">
	<form method="post" action="plugins/cloud/cloud.cgi?upcloud&amp;user=$user"
		enctype="multipart/form-data">
		<input type="file" name="datafile" size="50" />
		<input type="submit" value="Upload" />
	</form>
</div>
<p>
	<b>Files:</b> $files | <b>Size:</b> $size
</p>
EOT
		echo '<pre>'
		# List all Cloud files
		for f in $(ls ${cloud})
		do
			case $f in
				*.png|*.jpg|*.gif) image="images/image.png" ;;
				*) image="images/empty.png" ;;
			esac
			cat << EOT
<a href="$content/cloud/${f}" title="${WEB_URL}$content/cloud/${f}">\
<img src="$image" />${f}</a> : \
<a href="$script?rmcloud&amp;name=${f}&amp;user=$user">$(gettext "Remove")</a>
EOT
		done
		echo '</pre>'
		html_footer
		exit 0
esac
