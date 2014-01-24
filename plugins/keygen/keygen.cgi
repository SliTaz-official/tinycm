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
<h2>$(gettext "Key generator")</h2>

<div style="text-align: center; padding: 20px 0;">
	<form method="get" action="$script">
		<input type="text" name="keygen" 
			placeholder="$(gettext "Random or personal string")" />
		<div>
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
			*) echo "--" ;;
		esac
		# Random password
		cat << EOT
</pre>

<h3>$(gettext "Random password")</h3>

<div>
	<form method="get" action="$script">
		<div>
			<input type="hidden" name="keygen" value="passwd" />
			<input type="submit" name="random" value="$(gettext "generate")" />
		</div>
	</form>
</div>
<pre>
EOT
		
		if [ "$(GET keygen)" == "passwd" ]; then
			< /dev/urandom tr -dc '/()?!@#$%+-_A-Z-a-z-0-9' | head -c 10; echo ""
			#date +%s | sha256sum | base64 | head -c 10 ; echo ""
		else
			echo "--"
		fi
		echo "</pre>"
		html_footer && exit 0 ;;
esac
