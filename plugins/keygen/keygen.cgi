#!/bin/sh
#
# TinyCM Plugin - Key generator
#
. /usr/lib/slitaz/httphelper

case " $(GET) " in
	*\ keygen\ *)
		d="Keygen"
		keygen="$(GET keygen)"
		header
		html_header
		user_box
		cat << EOT
<h2>$(gettext "Password &amp; key generator")</h2>

<div style="text-align: center; padding: 20px 0;">
	<form method="get" action="$script">
		<input type="text" name="keygen" 
			placeholder="$(gettext "Random or personal string")" />
		<div>
			<input type="submit" name="encryption" value="password" />
			<input type="submit" name="encryption" value="base64" />
			<input type="submit" name="encryption" value="md5sum" />
			<input type="submit" name="encryption" value="sha256sum" />
			<input type="submit" name="encryption" value="sha512sum" />
		</div>
	</form>
</div>

<pre>
EOT
		# Random key if empty string
		if [ ! "$keygen" ];then
			keygen="$(date +%s | md5sum | base64 | head -c 10)"
		fi
		case " $(GET encryption) " in
			*\ base64\ *) echo "$keygen" | base64 ;;
			*\ md5sum\ *) echo "$keygen" | md5sum | awk '{print $1}' ;;
			*\ sha256sum\ *) echo "$keygen" | sha256sum | awk '{print $1}' ;;
			*\ sha512sum\ *) echo "$keygen" | sha512sum | awk '{print $1}' ;;
			*\ password\ *) 
				< /dev/urandom tr -dc '/()?!@#$%+-_A-Z-a-z-0-9' | head -c 10; echo "" ;;
			*) echo "--" ;;
		esac
		echo "</pre>"
		html_footer && exit 0 ;;
esac
