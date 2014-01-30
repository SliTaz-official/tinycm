#!/bin/sh
#
# TinyCM Plugin - Users and admin Dashboard.
#
. /usr/lib/slitaz/httphelper

if [ "$(GET dashboard)" ]; then
		d="Dashboard"
		header
		html_header
		user_box
		users=$(ls -1 $PEOPLE | wc -l)
		docs=$(find $wiki -type f | wc -l)
		wikisize="$(du -sh $wiki | awk '{print $1}')"
		cachesize="$(du -sh $cache | awk '{print $1}')"
		[ "$HG" != "yes" ] && hg=$(gettext "disabled")
		[ "$HG" == "yes" ] && hg=$(gettext "enabled")
		# Source all plugins.conf to get DASHBOARD_TOOLS and ADMIN_TOOLS
		ADMIN_TOOLS=""
		DASHBOARD_TOOLS=""
		for p in $(ls $plugins)
		do
			. $plugins/$p/$p.conf
		done
		if check_auth && ! admin_user; then
			ADMIN_TOOLS=""
		fi
		if check_auth; then
			cat << EOT
<div id="tools">
	<a href='$script?log'>Activity log</a>
	<a href='$script?ls'>Pages list</a>
	$DASHBOARD_TOOLS
	$ADMIN_TOOLS
</div>

<h2>$d</h2>

<pre>
Users     : $users
Wiki      : $docs ($wikisize)
Cache     : $cachesize
Mercurial : $hg
</pre>

<h3>Admin users</h3>
EOT
			# Get the list of administrators
			for u in $(ls $PEOPLE)
			do
				user=${u}
				if admin_user; then
					echo "<a href='?user=$u'>$u</a>"
				fi
			done
			cat << EOT
<h3>$(gettext "Plugins")</h3>
<pre>
EOT
			for p in $(ls -1 $plugins)
			do
				. $plugins/$p/$p.conf
				echo "<a href='?$p'>$PLUGIN</a> - $SHORT_DESC"
			done
			echo '</pre>'
		else
			gettext "You must be logged in to view the dashboard."
		fi
		html_footer
		exit 0
fi
