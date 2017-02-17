#!/bin/sh
#
# TinyCM/TazBug Plugin - Community Tools
#

case " $(GET) " in
	*\ wall\ *)
		d="Community Wall"
		wall="$tiny/$content/wall"
		date=$(date '+%Y-%m-%d %H:%M')
		header
		html_header
		user_box
		
		# Wall is only for logged users
		if [ "$WALL_MODE" == "private" ] && ! check_auth; then
			gettext "Private Wall - You must be logged in to read the wall" 
			html_footer && exit 0
		fi
		
		# Save any new message first
		if [ "$(GET message)" ] && check_auth; then
			# Prevent more than one message by minute peer user
			file="$(date '+%Y-%m-%d_%H:%M')_$user.txt"
			[ -d "$wall" ] || mkdir -p ${wall}
			# Write content to file
			sed "s/$(echo -en '\r') /\n/g" > ${wall}/${file} << EOT
$(GET message)
EOT
		fi
		
		# Delete message if requested
		if [ "$(GET delmsg)" ] && check_auth; then
			m=$(GET delmsg)
			author=$(echo ${m} | cut -d "_" -f 3)
			if [ "$user" == "${author%.txt}" ] || admin_user; then
				rm -f ${wall}/${m}
			fi
		fi
		
		# Message form
		echo "<h2>$d</h2>"
		if check_auth; then
			cat << EOT

<form method="get" action="$script" id="wall-form" name ="wall" onsubmit="return checkWall();">
	<input type="hidden" name="wall" />
	<textarea name="message" maxlength="${WALL_MESSAGES_LENGTH}"></textarea>
	<div>
		<input type="submit" value="$(gettext 'Send message')" />
		$(eval_gettext "Date: $date - Max char:") ${WALL_MESSAGES_LENGTH} -
		$(gettext "Wiki syntax is supported:")
		<a href="?d=en/help">$(gettext "Help page")</a>
	</div>
</form>

<h2>$(gettext "Latest Messages")</h2>
EOT
		fi
		# Display messages &nb=40
		msg_nb=40
		if [ "$(GET nb)" ]; then
			msg_nb=$(GET nb)
		fi
		for m in $(ls -r $wall | head -n ${msg_nb})
		do
			author=$(echo ${m} | cut -d "_" -f 3)
			pubdate=$(echo ${m} | cut -d "_" -f 1-2 | sed s"/_/ /")
			cat << EOT
<div class="wall-message">
	<div>By <a href='?user=${author%.txt}'>${author%.txt}</a>
	- <span class="date">${pubdate}</span>
EOT
			if [ "$user" == "${author%.txt}" ] || admin_user; then
				echo " - <span class='del'><a href='?wall&amp;delmsg=$m'>Delete</a></span>"
			fi
			echo "</div><p>"
			cat ${wall}/${m} | wiki_parser
			echo "</p></div>"
		done
		if check_auth; then
			cat << EOT
<div id="tools">
	<a href="$script?community">$(gettext "Community Tools")</a>
</div>
EOT
		fi
		html_footer && exit 0 ;;
	
	*\ community\ *)
		d="Community Tools"
		header
		html_header
		user_box
		echo '<div id="tools">'
		if check_auth; then
			echo "<a href='$script?dashboard'>Dashboard</a>"
		fi
		cat << EOT
<a href="$script?wall">Community Wall</a>
</div>
<h2>$d</h2>
<p>$SHORT_DESC</p>
EOT
		if admin_user; then
			cat << EOT
<h3>Plugin config</h3>
<pre>
Wall mode        : $WALL_MODE
Messages length  : $WALL_MESSAGES_LENGTH
</pre>
EOT
		fi
		html_footer && exit 0 ;;
esac
