#!/bin/sh
#
# TinyCM - Small, fast and elegant CGI/SHell Content Manager
#
# Copyright (C) 2012-2017 SliTaz GNU/Linux - BSD License
#
. /usr/lib/slitaz/httphelper.sh

# Let's have a peer site config file with a .cgi extension so content
# is secure even if left in a web server directory.
. ./config.cgi

tiny="$PWD"
content="content"
wiki="$content/wiki"
index="index"
cache="cache"
plugins="plugins"
tmp="/tmp/tinycm"
sessions="$tmp/sessions"
script="$SCRIPT_NAME"
activity="$cache/log/activity.log"

# Content negotiation for Gettext
IFS=","
for lang in $HTTP_ACCEPT_LANGUAGE
do
	lang=${lang%;*} lang=${lang# } lang=${lang%-*}
	case "$lang" in
		en) lang="C" && break ;;
		fr) lang="fr_FR" && break ;;
		pt) lang="pt_BR" && break ;;
		ru) lang="ru_RU" && break ;;
	esac
done
unset IFS
export LANG=$lang LC_ALL=$lang

# Internationalization
. /usr/bin/gettext.sh
TEXTDOMAIN='tinycm'
export TEXTDOMAIN

#
# Functions
#

# Used by edit to display language name and the language box. This is
# for CM content not gettext support.
get_lang() {
	dlang=$(echo $d | cut -d "/" -f 1)
	doc=${d#$dlang/}
	echo '<div id="lang">'
	for l in $LANGUAGES
	do
		case $dlang in
			en) i18n="English" ;;
			fr) i18n="Français" ;;
			pt) i18n="Português" ;;
			ru) i18n="Русский" ;;
			*) i18n="*" ;; 
		esac
		echo "<a href='?d=$l/$doc'>$l</a>"
	done
	echo '</div>'
}

# HTML 5 header.
html_header() {
	if [ -f "$tiny/lib/header.html" ]; then
		cat $tiny/lib/header.html | sed -e s!'%TITLE%'!"$TITLE - $d"!g
	else
		cat << EOT
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>$TITLE</title>
	<meta charset="utf-8" />
	<style type="text/css">body { margin: 40px 120px; }</style>
</head>
<body>
<!-- Content -->
<div id="content">
EOT
	fi
}

# HTML 5 footer.
html_footer() {
	if [ -f "$tiny/lib/footer.html" ]; then
		cat $tiny/lib/footer.html
	else
		cat << EOT

<!-- End content -->
</div>

<div id="footer">
	I &hearts; <a href="http://tinycm.slitaz.org/">TinyCM</a>
</div>

</body>
</html>
EOT
	fi
}

# Default index if missing
default_index() {
	mkdir -p "$wiki"
	cat > $wiki/$index.txt << EOT
==== Welcome ====

<p>
This is the default index page of your TinyCM, you can login then start to
edit and add some content. You can read the help about text formating
and functions: [Help page|en/help]
</p>

EOT
}

# Log main activity.
log_activity() {
	[ -d "$cache/log" ] || mkdir -p ${cache}/log
	#gravatar="$(get_gravatar $MAIL 24)"
	grep ^[A-Z] | \
		sed s"#^[A-Z]\([^']*\)#$user|$(date '+%Y-%m-%d')|\0#" \
		>> $cache/log/activity.log
}

# Log documents activity.
log() {
	grep ^[A-Z] | \
		sed s"#^[A-Z]\([^']*\)#$(date '+%Y-%m-%d %H:%M') : \0#" \
		>> $cache/$d/activity.log
}

# Check if user is auth
check_auth() {
	auth="$(COOKIE auth)"
	user="$(echo $auth | cut -d ":" -f 1)"
	md5cookie="$(echo $auth | cut -d ":" -f 2)"
	[ -f "$sessions/$user" ] && md5session="$(cat $sessions/$user)"
	if [ "$md5cookie" == "$md5session" ] && [ "$auth" ]; then
		. $PEOPLE/$user/account.conf
		return 0
	else
		return 1
	fi
}

# Check if user is admin
admin_user() {
	grep -w -q "$user" ${ADMIN_USERS}
}

# Authenticated or not
user_box() {
	if check_auth; then
		cat << EOT

<div id="user">
	<a href="$script?user=$user">$(get_gravatar $MAIL 20)</a>
	<a href="$script?logout">Logout</a>
</div>

EOT
	else
	cat << EOT

<div id="user">
	<a href="$script?login"><img src="images/avatar.png" alt="[ User ]" /></a>
	<a href="$script?login">Login</a>
</div>

EOT
	fi
	cat << EOT
<!--
<div id="search">
	<form method="get" action="$script">
		<input type="text" name="search" placeholder="$(gettext "Search")" />
	</form>
</div>
-->
EOT
}

# Link for online signup if enabled.
online_signup() {
	if [ "$ONLINE_SIGNUP" == "yes" ]; then
		echo -n "<p><a href='$script?signup'>"
		gettext "Create a new account"
		echo '</a></p>'
	fi
}

# Login page
login_page() {
	cat << EOT
<h2>$(gettext "Login")</h2>

<div id="account-info">
$(gettext "No account yet or trouble with your account? Please send
a request to $ADMIN_MAIL with your real name, user name, mail and password.")
$(online_signup)
</div>

<div id="login">
	<form method="post" action="$script">
		<input type="text" name="auth" placeholder="$(gettext "User name")" />
		<input type="password" name="pass" placeholder="$(gettext "Password")" />
		<div>
			<input type="submit" value="Login" /> $error
		</div>
	</form>
</div>

<div style="clear: both;"></div>
EOT
}

# Signup page
signup_page() {
	cat << EOT

<div id="signup">
	<form method="post" name="signup" action="$script" onsubmit="return checkSignup();">
		<input type="hidden" name="signup" value="new" />
		<input type="text" name="name" placeholder="$(gettext "Real name")" />
		<input type="text" name="user" placeholder="$(gettext "User name")" />
		<input type="text" name="mail" placeholder="$(gettext "Email")" />
		<input type="password" name="pass" placeholder="$(gettext "Password")" />
		<div>
			<input type="submit" value="$(gettext "Create new account")" />
		</div>
	</form>
</div>

EOT
}

# Create a new user in AUTH_FILE and PEOPLE
new_user_config() {
	if [ ! -f "$AUTH_FILE" ]; then
		touch $AUTH_FILE && chmod 0600 $AUTH_FILE
	fi
	echo "$user:$pass" >> $AUTH_FILE
	mkdir -pm0700 $PEOPLE/${user}
	cat > $PEOPLE/$user/account.conf << EOT
# User configuration
NAME="$name"
USER="$user"
MAIL="$mail"
EOT
	chmod 0600 $PEOPLE/$user/account.conf
	# First created user is admin
	if [ $(ls ${PEOPLE} | wc -l) == "1" ]; then
		echo "$user" > ${ADMIN_USERS}
	fi
}

# The CM style parser. Just a title, simple text formatting and internal
# links, as well as images and use HTML for other stuff. Keep it fast!
# To make TinyCM as easy as possible we have a small HTML editor/helper
# written in Javascript
wiki_parser() {
	doc="[0-9a-zA-Z\.\#/~\_%=\?\&,\+\:@;!\(\)\*\$'\-]*"
	sed \
		-e s"#====\([^']*\)====#<h2>\1</h2>#"g \
		-e s"#===\([^']*\)===#<h3>\1</h3>#"g \
		-e s"#==\([^']*\)==#<h4>\1</h4>#"g \
		-e s"#\*\*\([^']*\)\*\*#<b>\1</b>#"g \
		-e s"#''\([^']*\)''#<em>\1</em>#"g \
		-e s"#__\([^']*\)__#<u>\1</u>#"g \
		-e s"#\[\([^]]*\)|\($doc\)\]#<a href='$script?d=\2'>\1</a>#"g \
		-e s"#\[\([^]]*\)!\($doc\)\]#<a href='\2'>\1</a>#"g \
		-e s"#\[\(http://*[^]]*.png\)\]#<img src='\1' />#"g \
		-e s"#\[\([^]]*.png\)\]#<img src='content/cloud/\1' />#"g \
		-e s"#@\([^']*\)@#<a href='$script?user=\1'>\1</a>#"g
}

link_user() {
	echo "<a href='$(basename $script)?user=$user'>$user</a>"
}

# Save a document. Do we need more than 1 backup and diff ?
save_document() {
	mkdir -p $cache/$d $(dirname $wiki/$d)
	# May be a new page.
	if [ ! -f "$wiki/$d.txt" ]; then
		new=0
		touch $wiki/$d.txt
	fi
	cp $wiki/$d.txt $cache/$d/last.bak
	sed "s/$(echo -en '\r') /\n/g" > $wiki/$d.txt << EOT
$(GET content)
EOT
	diff $cache/$d/last.bak $wiki/$d.txt > $cache/$d/last.diff
	# Log
	if [ "$new" ]; then
		echo "Page created by: $(link_user)" | log
		echo "New document: <a href='$script?d=$d'>$d</a>" | log_activity
		if [ "$HG" == "yes" ]; then
			cd $content && hg -q add
			hg commit -q -u "$NAME <$MAIL>" -m "Created new document: $d"
			cd $tiny
		fi
	else
		# Here we may clean log: cat && tail -n 40
		echo "Page edited by: $(link_user)" | log
		if [ "$HG" == "yes" ]; then
			cd $content && hg commit -q -u "$NAME <$MAIL>" \
				-m "Edited document: $d"
			cd $tiny
		fi
	fi
}

# CM tools (edit, diff, etc) for auth users
wiki_tools() {
	if check_auth; then
		cat << EOT
<div id="tools">
	<a href="$script?edit=$d">$(gettext "Edit document")</a>
	<a href="$script?log=$d">$(gettext "File log")</a>
	<a href="$script?diff=$d">$(gettext "Last diff")</a>
	$PLUGINS_TOOLS
EOT
		[ "$HG" == "yes" ] && echo "<a href='$script?hg'>Hg Log</a>"
		echo "</div>"
	fi
}

# Built-in tools such as log/ls and PLUGINS_TOOLS
tiny_tools() {
	if check_auth; then
				cat << EOT
<div id='tools'>
	<a href='$script?log'>Activity log</a>
	<a href='$script?ls'>Pages list</a>
	$PLUGINS_TOOLS
</div>
EOT
	fi 
}

# Get and display Gravatar image: get_gravatar email size
# Link to profile: <a href="http://www.gravatar.com/$md5">...</a>
get_gravatar() {
	email=$1
	size=$2
	[ "$size" ] || size=48
	url="http://www.gravatar.com/avatar"
	md5=$(md5crypt $email)
	echo "<img src='$url/$md5?d=identicon&s=$size' alt='&lowast;' />"
}

# List hg logs
hg_log() {
	cd $content
	cat << EOT
<table>
	<thead>
		<td>$(gettext "User")</td>
		<td>$(gettext "Description")</td>
		<td>$(gettext "Revision")</td>
	</thead>
EOT
	hg log --template "<tr><td>{author}</td><td>{desc}</td><td>{rev}</td></tr>\n"
	echo '</table>'
}

#
# POST actions
#

case " $(POST) " in
	*\ auth\ *)
		# Authenticate user. Create a session file in $sessions to be used
		# by check_auth. We have the user login name and a peer session
		# md5 string in the COOKIE.
		user="$(POST auth)"
		pass="$(md5crypt "$(POST pass)")"
		valid=$(fgrep "${user}:" $AUTH_FILE | cut -d ":" -f 2)
		if [ "$pass" == "$valid" ] && [ "$pass" != "" ]; then
			md5session=$(echo -n "$$:$user:$pass:$$" | md5sum | awk '{print $1}')
			[ -d $sessions ] || mkdir -p $sessions
			date '+%Y-%m-%d' > ${PEOPLE}/${user}/last
			echo "$md5session" > $sessions/$user
			header "Location: $script" \
				"Set-Cookie: auth=$user:$md5session; HttpOnly"
		else
			header "Location: $script?login&error"
		fi ;;
	*\ signup\ *)
		# POST action for signup
		name="$(POST name)"
		user="$(POST user)"
		mail="$(POST mail)"
		pass="$(md5crypt "$(POST pass)")"
		if ! grep "^${user}:" $AUTH_FILE; then
			new_user_config
			header "Location: $script?login"
		else
			header
			html_header
			user_box
			echo "<h2>$(gettext 'User already exists:') $user</h2>"
			html_footer
		fi ;;
esac

#
# Plugins
#
for p in $(ls -1 $plugins)
do
	[ -f "$plugins/$p/$p.conf" ] && . $plugins/$p/$p.conf
	[ -x "$plugins/$p/$p.cgi" ] && . $plugins/$p/$p.cgi
done

#
# GET actions
#

case " $(GET) " in
	*\ edit\ *)
		d="$(GET edit)" 
		header
		html_header
		user_box
		get_lang
		wiki_tools
		if check_auth; then
			cat << EOT
<h2>$(gettext "Edit $doc [ $i18n ]")</h2>

<div id="edit">

<form method="get" action="$script" name="editor">
	<input type="hidden" name="save" value="$d" />
	<textarea name="content">$(cat "$wiki/$d.txt")</textarea>
	<input type="submit" value="$(gettext "Save document")" />
	$(gettext "Code Helper:")
	$(cat lib/jseditor.html)
</form>

</div>
EOT
		else
			gettext "You must be logged in to edit pages"
		fi
		html_footer ;;
		
	*\ save\ *)
		d="$(GET save)"
		if check_auth; then
			save_document
		fi 
		header "Location: $script?d=$d" ;;
		
	*\ log\ *)
		d="$(GET log)"
		header
		html_header
		user_box
		# Main activity
		if [ "$d" == "log" ]; then
			tiny_tools
			echo "<h2>$(gettext "Activity log")</h2>"
			echo '<pre>'
			if [ -f "$cache/log/activity.log" ]; then
				IFS="|"
				tac $cache/log/activity.log | while read USER DATE LOG
				do
					. ${PEOPLE}/${USER}/account.conf
					cat << EOT
<a href='$script?user=$USER'>$(get_gravatar $MAIL 24)</a>\
<span class='date'>$DATE -</span> $LOG
EOT
				done
				unset IFS
			else
				gettext "No activity log yet"; echo
			fi
			echo '</pre>'
			html_footer && exit 0
		fi
		# Document activity
		get_lang
		wiki_tools
		echo "<h2>$(gettext "Activity for:") <a href='$script?d=$d'>$d</a></h2>"
		echo '<pre>'
		if [ -f "$cache/$d/activity.log" ]; then
			tac $cache/$d/activity.log
		else
			gettext "No log for: $d"; echo
		fi
		echo '</pre>'
		html_footer ;;
	
	*\ ls\ *)
		d="Document list"
		header
		html_header
		user_box
		tiny_tools
		[ ! check_auth ] && auth=0
		echo "<h2>$(gettext "Pages list")</h2>"
		echo '<pre>'
		cd ${wiki}
		for d in $(find . -type f | sed s'/.\///')
		do
			echo -n "<a href='$script?d=${d%.txt}'>${d%.txt}</a>"
			if [ "$auth" ]; then 
				cat << EOT
 : <a href="$script?edit=$d">$(gettext "Edit")</a> || \
<a href="$script?rm=$d">$(gettext "Remove")</a> 
EOT
			else
				echo ""
			fi
		done && unset auth
		echo '</pre>'
		html_footer ;;
	
	*\ rm\ *)
		[ ! check_auth ] && exit 1
		d="$(GET rm)"
		rm ${wiki}/"${d}"
		rm -rf ${cache}/"${d%.txt}"
		header "Location: $script?ls" ;;
		
	*\ diff\ *)
		d="$(GET diff)"
		date="last"
		header
		html_header
		user_box
		get_lang
		wiki_tools
		echo "<h2>$(gettext "Diff for:") <a href='$script?d=$d'>$d</a></h2>"
		echo '<pre>'
		if [ -f "$cache/$d/$date.diff" ]; then
			cat $cache/$d/$date.diff | sed \
			-e 's|&|\&amp;|g' -e 's|<|\&lt;|g' -e 's|>|\&gt;|g' \
			-e s"#^-\([^']*\).#<span style='color: red;'>\0</span>#"g \
			-e s"#^+\([^']*\).#<span style='color: green;'>\0</span>#"g \
			-e s"#@@\([^']*\)@@#<span style='color: blue;'>@@\1@@</span>#"g
		else
			gettext "No diff for:"; echo " $d"
		fi
		echo '</pre>'
		html_footer ;;
		
	*\ login\ *)
		# The login page
		d="Login"
		[ "$(GET error)" ] && \
			error="<p class="error">$(gettext "Bad login or pass")</p>"
		header
		html_header
		user_box
		login_page 
		html_footer ;;
		
	*\ signup\ *)
		# The login page
		d="$(gettext "Sign Up")"
		header
		html_header
		user_box
		echo "<h2>$d</h2>"
		if [ "$ONLINE_SIGNUP" == "yes" ]; then
			signup_page
		else
			gettext "Online registration is disabled"
		fi
		html_footer ;;
		
	*\ logout\ *)
		# Set a Cookie in the past to logout.
		expires="Expires=Wed, 01-Jan-1980 00:00:00 GMT"
		if check_auth; then
			rm -f "$sessions/$user"
			header "Location: $script" "Set-Cookie: auth=none; $expires; HttpOnly"
		fi ;;
		
	*\ user\ *)
		# Basic user profile. Use the users plugin for more functions
		d="$(GET user)"
		last="$(cat $PEOPLE/"$(GET user)"/last)"
		header
		html_header
		user_box
		. $PEOPLE/"$(GET user)"/account.conf
cat << EOT
<h2>$(get_gravatar $MAIL) $NAME</h2>

<pre>
$(gettext "User name  :") $USER
$(gettext "Last login :") $last
</pre>
EOT
		html_footer ;;
		
	*\ hg\ *)
		d="Hg Log"
		header
		html_header
		user_box
		[ "$HG" != "yes" ] && gettext "Hg is disabled" && exit 0
		[ ! -x /usr/bin/hg ] && gettext "Hg is not installed" && exit 0
		echo "<h2>$d</h2>"
		case " $(GET hg) " in
			*\ init\ *)
				if check_auth; then
					[ -d "$content/.hg" ] && exit 0
					echo '<pre>'
					gettext "Executing: hg init"; echo
					cd $content/ && hg init
					echo '[hooks]' > .hg/hgrc
					echo 'incoming = hg update' >> .hg/hgrc
					gettext "Adding current content and committing"; echo
					[ ! -f "$wiki/index.txt" ] && default_index
					hg add && hg commit -u "$NAME <$MAIL>" \
						-m "Initial commit with current content"
					echo '</pre>' && cd .. 
				fi ;;
		esac
		hg_log
		html_footer ;;
		
	*)
		# Display requested page
		d="$(GET d)"
		[ "$d" ] || d=$index
		header
		html_header
		user_box
		get_lang
		
		# Generate a default index on first run
		if [ ! -f "$wiki/$index.txt" ]; then
			if ! default_index; then
				echo "<pre class='error'>Directory : content/ is not writeable</pre>"
				html_footer && exit 0
			fi
		fi
		
		# Check cache dir
		if [ ! -w "$cache" ]; then
			echo "<pre class='error'>Directory : cache/ is not writeable"
			echo "Command   : install -m 0777 -d $tiny/cache</pre>"
			html_footer && exit 0
		fi
		
		# Hg warning if enabled but not initiated
		if [ "$HG" == "yes" ] && [ ! -d "$content/.hg" ]; then
			echo '<p class="error box">'
			gettext "Mercurial is enabled but no repository found"
			echo ": <a href='$script?hg=init'>Hg init</a>"
			echo '</p>'
		fi
		
		# Wiki tools
		wiki_tools
		
		# Wiki document
		if [ ! -f "$wiki/$d.txt" ]; then
			echo "<h2>$d</h2>"
			gettext "The document does not exist. You can create it or read the"
			echo " <a href='$script?d=en/help'>help</a>"
		else
			if fgrep -q [NOWIKI] $wiki/$d.txt; then
				cat $wiki/$d.txt | sed '/\[NOWIKI\]/'d
			else
				cat $wiki/$d.txt | wiki_parser
			fi
		fi
		html_footer ;;
esac

exit 0
