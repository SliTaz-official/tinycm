#!/bin/sh
#
# TinyCM Plugin - Blog
#
. /usr/lib/slitaz/httphelper

blog="$tiny/$content/blog"

# Blog tools
blog_tools() {
	cat << EOT
<div id="tools">
	<a href="$script?blog=edit&amp;d=new">$(gettext "New post")</a>
	<a href="$script?dashboard">Dashboard</a>
	$([ "$index" == "blog" ] && echo "<a href='$script?d=index'>Index</a>")
	$([ "$HG" == "yes" ] && echo "<a href='$script?hg'>Hg Log</a>")
</div>
EOT
}

# Post tools
post_tools() {
	cat << EOT
	- <a href="$script?blogedit&amp;d=${d}">$(gettext "Edit it!")</a>
EOT
#<a href="$script?blogrm=${d}">$(gettext "Remove")</a>
}

# Display blog post: show_posts nb
show_post() {
	d=${1%.txt}
	date=$(fgrep 'DATE=' ${blog}/${d}.txt | cut -d '"' -f 2)
	# Get post author
	author=$(fgrep 'AUTHOR=' ${blog}/${d}.txt | cut -d '"' -f 2)
	if [ -f "${PEOPLE}/${author}/account.conf" ]; then
		. ${PEOPLE}/${author}/account.conf
	else
		echo "ERROR: ${PEOPLE}/${author}/account.conf"
	fi
	echo "<div class=\"blogpost\">"
	cat ${blog}/${d}.txt | sed -e '/AUTHOR=/'d -e '/DATE=/'d | wiki_parser
	cat << EOT
<div class="post-tools">
	<a href="$script?user=$USER">$(get_gravatar $MAIL 24)</a>
	<span class="date">$date</span>
EOT
	# Post tools for admin users
	if check_auth && admin_user; then
		post_tools
		echo "</div>"
	else
		echo "</div>"
	fi
	echo "</div>"
}

# Display blog post: show_posts count
show_posts() {
	for p in $(ls $blog | sort -r -n | head -n $1)
	do
		show_post ${p}
	done
}

#
# Index main page can display the lastest Blog posts
#
if fgrep -q '[BLOG]' $tiny/$wiki/index.txt && [ ! "$(GET)" ]; then
	d="Blog posts"
	index="blog"
	header
	html_header
	user_box
	# Post tools for auth users
	if admin_user; then
		blog_tools
	fi
	show_posts 5
	echo "<p><a href='$script?blog'>$(gettext "More blog posts")</a></p>"
	html_footer && exit 0
fi

#
# Handle GET requests
#

if [ "$(GET blog)" ]; then
	case " $(GET blog) " in
		*\ edit\ *)
			d="$(GET d)"
			header
			html_header
			user_box
			if ! check_auth && admin_user; then
				gettext "You must be admin to create a new Blog post"
				html_footer && exit 0
			fi
			# New post
			if [ "$d" == "new" ]; then
				date=$(date '+%Y-%m-%d')
				last=$(ls $blog | sort -r -n | head -n 1)
				nb=${last%.txt}
				d=$(($nb + 1))
				conf=$(echo -e "\n\nAUTHOR=\"$user\"\nDATE=\"$date\"\n\n====Title====")
			fi		
			cat << EOT
<h2>$(gettext "Blog post"): $d</h2>

<div id="edit">
	<form method="get" action="$script?" name="editor">
		<input type="hidden" name="blog" value="save" />
		<input type="hidden" name="d" value="$d" />
		<textarea name="content">${conf}$(cat "$blog/$d.txt")</textarea>
		<input type="submit" value="$(gettext "Post content")" />
		$(gettext "Code Helper:")
		$(cat lib/jseditor.html)
	</form>
</div>
EOT
			html_footer && exit 0 ;;
	
		*\ save\ *)
			d="$(GET d)"
			if check_auth && admin_user; then
				[ -d "$blog" ] || mkdir -p ${blog}
				# New post ?
				if [ ! -f "${blog}/${d}.txt" ]; then
					echo "New Blog post: <a href='$script?blog=$d'>Read it!</a>" \
						| log_activity
				fi
				# Write content to file
				sed "s/$(echo -en '\r') /\n/g" > ${blog}/${d}.txt << EOT
$(GET content)
EOT
			fi 
			header "Location: $script?blog" ;;
			
		*)
			d="Blog posts"
			count="20"
			header
			html_header
			user_box
			# Blog tools for admin users
			if check_auth && admin_user; then
				blog_tools
			fi
			# Exit if plugin is disabled
			if [ ! -d "$blog" ]; then
				echo "<p class='error box'>"
				gettext "Blog plugin is not yet active."; echo "</p>"
				html_footer && exit 0
			fi
			# Single post
			if [ "$(GET blog)" != "blog" ]; then
				show_post "$(GET blog)"
			else
				show_posts ${count}
			fi ;;
	esac
	html_footer && exit 0
fi
