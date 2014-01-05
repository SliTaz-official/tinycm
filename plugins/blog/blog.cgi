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
	<a href="$script?blogedit&amp;d=new">$(gettext "New post")</a>
	<a href="$script?dashboard">Dashboard</a>
	$([ "$index" == "blog" ] && echo "<a href='$script?d=index'>Index</a>")
	$([ "$HG" == "yes" ] && echo "<a href='$script?hg'>Hg Log</a>")
</div>
EOT
}

# Post tools
post_tools() {
	cat << EOT
<div class="post-tools">
	${d}: <a href="$script?blogedit&amp;d=${d}">$(gettext "Edit post")</a>
</div>
EOT
}

# Display blog post: show_posts nb
show_posts() {
	for p in $(find $blog -type f | head -n $1)
	do
		name=$(basename $p)
		d=${name%.txt}
		echo "<div class=\"blogpost\">"
		cat ${blog}/${d}.txt | wiki_parser
		echo "</div>"
		# Post tools for auth users
		if check_auth; then
			post_tools
		fi
	done
}

#
# Index main page can display the lastest Blog posts
#
if fgrep -q '[BLOG]' $tiny/$wiki/index.txt && [ ! "$(GET)" ]; then
	d="Blog"
	index="blog"
	header
	html_header
	user_box
	echo "<h2>$(gettext "Latest blog posts")</h2>"
	# Post tools for auth users
	if check_auth; then
		blog_tools
	fi
	show_posts 5
	echo "<p><a href='$script?blog'>$(gettext "More blog posts")</a></p>"
	html_footer && exit 0
fi

case " $(GET) " in
	*\ blogedit\ *)
		d="$(GET d)"
		header
		html_header
		user_box
		# Blog tools for auth users
		if ! check_auth; then
			gettext "You must be logged in to create a new Blog post"
			html_footer && exit 0
		fi
		# New post
		if [ "$d" == "new" ]; then
			d=$(date '+%Y%m%d')
			[ -f "$blog/$d.txt" ] && d=$(date '+%Y%m%d-%H%M')
		fi		
		cat << EOT
<h2>$(gettext "Blog post"): $d</h2>

<div id="edit">
	<form method="get" action="$script" name="editor">
		<input type="hidden" name="blogsave" value="$d" />
		<textarea name="content">$(cat "$blog/$d.txt")</textarea>
		<input type="submit" value="$(gettext "Post content")" />
		$(gettext "Code Helper:")
		$(cat lib/jseditor.html)
	</form>
</div>
EOT
		html_footer && exit 0 ;;

	*\ blogsave\ *)
		d="$(GET blogsave)"
		if check_auth; then
			[ -d "$blog" ] || mkdir -p ${blog}
			sed "s/$(echo -en '\r') /\n/g" > ${blog}/${d}.txt << EOT
$(GET content)
EOT
		fi 
		header "Location: $script?blog" ;;
		
	*\ blog\ *)
		d="Latest blog posts"
		nb="20"
		header
		html_header
		user_box
		echo "<h2>$(gettext "Latest blog posts")</h2>"
		# Blog tools for auth users
		if check_auth; then
			blog_tools
		fi
		# Exit if plugin is disabled
		if [ ! -d "$blog" ]; then
			echo "<p class='error box'>"
			gettext "Blog plugin is not yet active."; echo "</p>"
			html_footer && exit 0
		fi
		show_posts ${nb}
		html_footer
		exit 0 ;;
esac
