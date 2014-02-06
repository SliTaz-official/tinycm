#!/bin/sh
#
# TinyCM Plugin - Blog
#
. /usr/lib/slitaz/httphelper

blog="$tiny/$content/blog"

# # Blog tools for admin users only
blog_tools() {
	if check_auth && admin_user; then
		cat << EOT
<div id="tools">
	<a href="$script?blog">$(gettext "Blog")</a>
	<a href="$script?blog=edit&amp;p=new">$(gettext "New post")</a>
	<a href="$script?dashboard">Dashboard</a>
	$([ "$index" == "blog" ] && echo "<a href='$script?d=index'>Index</a>")
	$([ "$HG" == "yes" ] && echo "<a href='$script?hg'>Hg Log</a>")
</div>
EOT
	fi
}

# Post tools
post_tools() {
	cat << EOT
	- <a href="$script?blog=edit&amp;p=${p}">$(gettext "Edit it!")</a>
	|| <a href="$script?blog=rm&amp;p=${p}">$(gettext "Remove")</a>
EOT
}

# Create a XML feed for a new post
gen_rss() {
	pubdate=$(date "+%a, %d %b %Y %X")
	desc="$(cat ${blog}/${p}/post.txt | grep ^[A-Za-z] | head -n 4)"
	. ${blog}/${p}/post.conf
	cat > ${blog}/${p}/post.xml << EOT
	<item>
		<title>$TITLE</title>
		<link>http://${SERVER_NAME}?blog&amp;p=$p</link>
		<guid>blog-$p</guid>
		<pubDate>$pubdate</pubDate>
		<description>$desc</description>
	</item>
EOT
}

# RSS Feed
rss() {
pubdate=$(date "+%a, %d %b %Y %X")
	cat << EOT
Content-Type: text/xml

<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0">
<channel>
	<title>TinyCM RSS</title>
	<description>The Blog feed</description>
	<link>http://${SERVER_NAME}</link>
	<lastBuildDate>$pubdate GMT</lastBuildDate>
	<pubDate>$pubdate GMT</pubDate>
EOT
	for p in $(ls $blog | sort -r -n | head -n 8)
	do
		cat $blog/$p/post.xml
	done
	cat << EOT
</channel>
</rss>
EOT
}

# Display blog post: show_posts nb
show_post() {
	[ -f "$blog/$1/post.conf" ] || return 1
	p="$1"
	. ${blog}/${p}/post.conf
	d="$TITLE"
	
	# Author info
	if [ -f "${PEOPLE}/${AUTHOR}/account.conf" ]; then
		. ${PEOPLE}/${AUTHOR}/account.conf
	else
		echo "ERROR: ${PEOPLE}/${AUTHOR}/account.conf"
	fi
	
	echo "<h2>$TITLE</h2>"
	echo "<div class='blogpost'>"
	cat ${blog}/${p}/post.txt | wiki_parser
	cat << EOT
<div class="post-tools">
	<a href="$script?user=$USER">$(get_gravatar $MAIL 24)</a>
	<span class="date">$DATE</span>
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
# Index main page can display the latest Blog posts
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
			d="Editing: $(GET p)"
			p="$(GET p)"
			header
			html_header
			user_box
			if ! check_auth && admin_user; then
				gettext "You must be admin to create a new Blog post"
				html_footer && exit 0
			fi
			blog_tools
			# New post
			if [ "$p" == "new" ]; then
				last=$(ls $blog | sort -r -n | head -n 1)
				p=$(($last + 1))
				AUTHOR="$user"
				DATE=$(date '+%Y-%m-%d')
			else
				. ${blog}/${p}/post.conf
			fi		
			cat << EOT
<h2>$(gettext "Blog post"): $p</h2>

<div id="edit">
	<form method="get" action="$script?" name="editor">
		<input type="text" name="title" value="$TITLE" placeholder="Title" />
		<input type="hidden" name="blog" value="save" />
		<input type="hidden" name="p" value="$p" />
		<textarea name="content">$(cat "$blog/$p/post.txt")</textarea>
		<div>
			<input type="submit" value="$(gettext "Post content")" />
			<input style="width: 20%;" type="text" 
				name="author" value="$AUTHOR" />
			<input style="width: 20%; display: inline;" type="text"
				name="date" value="$DATE" />
		</div>
		
		<p>
		$(gettext "Code Helper:")
		$(cat lib/jseditor.html)
		</p>
	</form>
</div>
EOT
			html_footer && exit 0 ;;
	
		*\ save\ *)
			p="$(GET p)"
			if check_auth && admin_user; then
				[ -d "$blog/$p" ] || mkdir -p ${blog}/${p}
				# New post ?
				if [ ! -f "${blog}/${p}/post.txt" ]; then
					cat > ${blog}/${p}/post.conf << EOT
# TinyCM Blog post configuration
AUTHOR="$(GET author)"
DATE="$(GET date)"
TITLE="$(GET title)"
EOT
					echo "New Blog post: <a href='$script?blog=$p'>Read it!</a>" \
						| log_activity
				fi
				# Write content to file
				sed "s/$(echo -en '\r') /\n/g" > ${blog}/${p}/post.txt << EOT
$(GET content)
EOT
			fi
			[ -f "${blog}/${p}/post.xml" ] || gen_rss
			header "Location: $script?blog&p=$p" ;;
		
		*\ rm\ *)
			if check_auth && admin_user; then
				rm -rf ${blog}/"$(GET p)"
			fi
			header "Location: $script?blog" ;;
		
		*\ archives\ *)
			# List all posts with title only
			d="Blog archives"
			header
			html_header
			user_box
			blog_tools
			echo "<h2>Blog archives</h2>"
			echo "<pre>"
			for p in $(ls $blog)
			do
				. ${blog}/${p}/post.conf
				echo "\
<span class='date'>$DATE :</span> <a href='$script?blog&amp;p=$p'>$TITLE</a>"
			done 
			echo "</pre>" ;;
			
		*)
			if [ "$(GET blog)" == "rss" ]; then
				rss && exit 0
			fi
			d="Blog posts"
			count="20"
			header
			html_header
			user_box
			blog_tools
			# Exit if plugin is disabled
			if [ ! -d "$blog" ]; then
				echo "<p class='error box'>"
				gettext "Blog plugin is not yet active."; echo "</p>"
				html_footer && exit 0
			fi
			# Single post
			if [ "$(GET p)" ]; then
				show_post "$(GET p)"
			else
				show_posts ${count}
				echo "<p><a href='$script?blog=archives'>$(gettext "Blog archives")</a></p>"
			fi ;;
	esac
	html_footer && exit 0
fi
