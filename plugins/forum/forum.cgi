#!/bin/sh
#
# TinyCM/TazBug Plugin - Support/discussion forum using #hashtags
#
# Display a topic: ?forum&topic=NB
# d= is used by html_header to set page title
# t= is used to set the topic number
#

forum="$tiny/$content/forum"

# Forum tools
forum_tools() {
	cat << EOT
<div id="tools">
	<a href="$script?forum=edit&amp;t=new">$(gettext "New post")</a>
	$([ "$(GET t)" ] && echo "<a href='$script?forum'>Forum</a>")
	$([ "$index" == "forum" ] && echo "<a href='$script?d=index'>Index</a>")
	$([ "$HG" == "yes" ] && echo "<a href='$script?hg'>Hg Log</a>")
</div>
EOT
}

# Topic tools for admin and author
topic_tools() {
	cat << EOT
	- <a href="?forum=edit&amp;t=${t}">$(gettext "Edit it!")</a>
	|| <a href="$script?forum=rm&amp;t=${t}">$(gettext "Remove")</a>
EOT
}

# Create a XML feed for a new topic
gen_rss() {
	pubdate=$(date "+%a, %d %b %Y %X")
	title="Forum: $(fgrep '====' ${forum}/${t}/topic.txt | sed s'/====//'g)"
	cat > ${forum}/${t}/topic.xml << EOT
	<item>
		<title>$title</title>
		<link>http://${SERVER_NAME}?forum=topic&amp;t=$t</link>
		<guid>topic-$t</guid>
		<pubDate>$pubdate</pubDate>
		<description>$hashtags</description>
	</item>
EOT
}

new_msg() {
	if check_auth; then
		cat << EOT
<div id="edit">
	<h3>$(gettext "New message")</h3>
	<form method="get" action="$script" name="editor">
		<textarea name="message"></textarea>
		<input type="hidden" name="forum" value="msg" />
		<input type="hidden" name="t" value="$t" />
		<input type="submit" value="$(gettext 'Send message')" />
		$(gettext "Wiki syntax is supported") -
		<a href="?d=en/help">$(gettext "Help page")</a>
	</form>
</div>
EOT
	fi
}

# Display a forum topic with messages: show_topic NB
show_topic() {
	t=${1%.txt}
	. ${forum}/${t}/topic.conf
	
	if [ -f "${PEOPLE}/${AUTHOR}/account.conf" ]; then
		. ${PEOPLE}/${AUTHOR}/account.conf
	else
		echo "ERROR: ${PEOPLE}/${AUTHOR}/account.conf"
	fi
	
	echo "<div class='blogpost'>"
	cat ${forum}/${t}/topic.txt | wiki_parser
	cat << EOT
<div class="post-tools">
	<a href="$script?user=$USER">$(get_gravatar $MAIL 24)</a>
	<span class="date">$DATE</span>
EOT
	
	# Topic tools for admin users (edit, remove)
	if check_auth && admin_user; then
		topic_tools
		echo "</div>"
	else
		echo "</div>"
	fi
	echo "</div>"
	
	# Hashtags
	if [ -f "${forum}/${t}/hashtags.txt" ]; then
		echo "<h3>Hashtags</h3>"
		echo "<div id='hashtags'>"
		link_hashtags
		echo "</div>"
	fi
}

# Display blog post: show_posts count
show_topics() {
	for t in $(ls $forum | sort -r -n | head -n $1)
	do
		. ${forum}/${t}/topic.conf
		. ${PEOPLE}/${AUTHOR}/account.conf
		title="$(fgrep '====' ${forum}/${t}/topic.txt | sed s'/====//'g)"
		cat << EOT
<div class="box topic">
	<a href="?user=${AUTHOR}">$(get_gravatar $MAIL 24)</a>
	<span class="date">$DATE</span> : <a href="?forum=topic&amp;t=${t}">$title</a>
	<span>
EOT
		link_hashtags
		echo "</span></div>"
	done
}

show_messages() {
	msgs=$(ls -1 $forum/$t/msg.*.txt | wc -l)
	echo "<h3>$(gettext 'Messages'): $msgs</h3>"
	[ "$msgs" == 0 ] && echo "<p>$(gettext 'Be the first to post a message!')<p/>"
	for msg in $(ls -1tr $forum/$t/msg.*.conf)
	do
		. ${msg}
		rm=""
		# User can delete his post.
		if [ "$user" == "$AUTHOR" ]; then
			rm="- <a href=\"?forum=msgrm&amp;t=$t&amp;msg=$ID\">$(gettext 'Remove')</a>"
		fi
		# Display user gravatar, date and message
		cat << EOT
<p>
	<a href="?user=$AUTHOR">$(get_gravatar $MAIL 24)</a>
	<span class="date">$DATE</span> $rm
</p>
<div class="forum-msg">
$(cat ${msg%.conf}.txt | wiki_parser)
</div>
EOT
		unset NAME DATE
	done
}

# Create HTML link for a topic #hashtags
link_hashtags() {
	for h in $(cat ${forum}/${t}/hashtags.txt)
	do
		echo "<a href='?forum=hashtag&amp;h=${h#\#}'>${h}</a>"
	done
}

#
# Handle GET requests
#
if [ "$(GET forum)" ]; then
	case " $(GET forum) " in
		*\ edit\ *)
			t="$(GET t)"
			d="Edit: $(fgrep '====' ${forum}/${t}/topic.txt | sed s'/====//'g)"
			header
			html_header
			user_box
			if ! check_auth; then
				gettext "You must be logged in to create a new Forum post"
				html_footer && exit 0
			fi
			# New post
			if [ "$t" == "new" ]; then
				date=$(date '+%Y-%m-%d %H:%M')
				last=$(ls -r $forum | head -n 1)
				nb=${last%.txt}
				t=$(($nb + 1))
				conf=$(echo "====Title====")
			else
				hashtags="$(cat $forum/$t/hashtags.txt)"
			fi		
			cat << EOT
<h2>$(gettext "Forum topic"): $t</h2>

<div id="edit">
	<form method="get" action="$script" name="editor">
		<input type="hidden" name="forum" value="save" />
		<input type="hidden" name="t" value="$t" />
		<textarea name="content">${conf}$(cat "$forum/$t/topic.txt")</textarea>
		<div>
			<b>#HashTags : </b> 
			<input type="text" name="hashtags" value="$hashtags" />
		</div>
		<input type="submit" value="$(gettext "Post topic")" />
		$(gettext "Code Helper:")
		$(cat lib/jseditor.html)
	</form>
</div>
EOT
			html_footer && exit 0 ;;
		
		*\ save\ *)
			t="$(GET t)"
			hashtags="$(GET hashtags)"
			if check_auth; then
				[ -d "${forum}/${t}" ] || mkdir -p ${forum}/${t}
				# New topic ?
				if [ ! -f "${forum}/${t}/topic.txt" ]; then
					echo "New Forum topic: <a href='$script?forum=topic&amp;t=$t'>Read it!</a>" \
						| log_activity
					cat > ${forum}/${t}/topic.conf << EOT
# TinyCM Forum topic config file
AUTHOR="$user"
DATE="$(date '+%Y-%m-%d %H:%M')"
STATUS="open"
EOT
					gen_rss
				fi
				# Write content and #hashtags to file
				sed "s/$(echo -en '\r') /\n/g" > ${forum}/${t}/topic.txt << EOT
$(GET content)
EOT
				echo "${hashtags}" > ${forum}/${t}/hashtags.txt
			fi
			header "Location: $script?forum=topic&t=$t" ;;
	
		*\ msgrm\ *)
			# Remove a message
			t="$(GET t)"
			if check_auth; then
				rm -f ${forum}/${t}/msg."$(GET msg)".*
			fi
			header "Location: $script?forum=topic&t=$t" ;;
		
		*\ msg\ *)
			t="$(GET t)"
			if check_auth; then
				date=$(date "+%Y-%m-%d %H:%M")
				msgs=$(ls -1 $forum/$t/msg.*.txt | wc -l)
				count=$(($msgs + 1))
				# Write config file
				cat > ${forum}/${t}/msg.${count}.conf << EOT
# TinyCM Forum message config file
AUTHOR="$user"
DATE="$(date '+%Y-%m-%d %H:%M')"
ID="$count"
EOT
			# Write message to file
			sed "s/$(echo -en '\r') /\n/g" > ${forum}/${t}/msg.${count}.txt << EOT
$(GET message)
EOT
			fi
			header "Location: $script?forum=topic&t=$t" ;;
		
		*\ rm\ *)
			# Remove a forum topic
			t="$(GET t)"
			if [ -d "${forum}/${t}" ]; then
				rm -rf ${forum}/${t}
			fi
			header "Location: $script?forum" ;;
		
		*\ hashtag\ *)
			# Display a hashtag
			hashtag="$(GET h)"
			header
			html_header
			user_box
			echo "<h2>Forum Hashtag #$hashtag</h2>"
			for h in $(fgrep -l "#$hashtag" ${forum}/*/hashtags.txt)
			do
				path=$(dirname ${h})
				t=$(basename $path)
				. ${path}/topic.conf
				title="$(fgrep '====' $(dirname ${h})/topic.txt | sed s'/====//'g)"
				cat << EOT
<div class='box topic'>
	<span class='date'>$DATE</span> - <a href='?forum=topic&amp;t=$t'>$title</a>
</div>
EOT
			done
			html_footer && exit 0 ;;
		
		*\ topic\ *)
			# Single post: get title from topic content before html_header
			t="$(GET t)"
			d="Forum: $(fgrep '====' ${forum}/${t}/topic.txt | sed s'/====//'g)"
			header
			html_header
			user_box
			# Forum tools for auth users
			[ check_auth ] && forum_tools
			show_topic "$t"
			show_messages
			new_msg
			html_footer && exit 0 ;;
			
		*)
			d="$(gettext 'Forum Topics')"
			count="20"
			header
			html_header
			user_box
			# Exit if plugin is disabled
			if [ ! -d "$forum" ]; then
				echo "<pre class='error box'>"
				gettext "Forum plugin is not yet active."; echo
				echo "Command: install -m 0777 -d $forum</pre>"
				html_footer && exit 0
			fi
			echo $(GET topic)
			# Forum tools for auth users
			[ check_auth ] && forum_tools
			echo "<h2>$d</h2>"
			show_topics ${count} ;;
	esac
	html_footer && exit 0
fi
	
