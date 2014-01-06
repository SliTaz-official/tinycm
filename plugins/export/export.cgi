#!/bin/sh
#
# TinyCM Plugin - Export to static content
#
. /usr/lib/slitaz/httphelper

#
# NOTE: Exporting wiki and making all urls work is a bit tricky and
# actually doesn't work as expected. The goal is to have a SliTaz codex
# online that can be included on the ISO, so we could have an export
# including a small CGI script to simply display wiki pages via HTTPd
# knowing that with HTML we must also deal with ../../
#

if [ "$(GET export)" ]; then
	d="Export"
	date=$(date "+%Y%m%d")
	tmpdir="$tmp/export/$$/wiki-$date"
	header
	html_header
	user_box
	cat << EOT 
<h2>Export</h2>
<p>
$(gettext "EXPERIMENTAL: Export to HTML and create a tarball of your text
content or plugins files.")
</p>
<form method="get" action="$WEB_URL">
	<select name="export">
EOT
	for c in $(ls -1 content/)
	do
		echo "<option value="$c">$c</option>"
	done
	cat << EOT
	</select>
	<input type="submit" value="$(gettext "Export")" />
</form>
EOT
	# Functions
	css_path() {
		# Sed CSS style path in all documents
		sed -i s'/style.css/..\/style.css/' */*.html
		sed -i s'/style.css/..\/..\/style.css/' */*/*.html
		sed -i s'/style.css/..\/..\/..\/style.css/' */*/*/*.html
	}
	gen_tarball() {
		gettext "Creating tarball"; echo -n ": "
		cd $tmpdir && mkdir $tiny/$cache/export
		# Clean cache
		find $tiny/$cache/export -mtime +1 | xargs rm -rf
		tar czf $tiny/$cache/export/$export-$date.tar.gz $export
		cd $tiny/$cache/export && du -sh $export-$date.tar.gz
	}
	dl_link() {
		gettext "Download"; echo \
			": <a href='cache/export/$export-$date.tar.gz'>$export-$date.tar.gz</a>"
	}
	# Export requested content
	case " $(GET export) " in
		*\ cloud\ *)
			export="cloud"
			tmpdir="content"
			echo '<pre>'
			gettext "Exporting:"; echo " $export"
			gen_tarball
			echo '</pre>' 
			dl_link ;;
		*\ wiki\ *)
			export="wiki"
			echo '<pre>'
			gettext "Exporting:"; echo " $export"
			mkdir -p $tmpdir/$export
			gettext "Copying CSS style and images..."; echo
			cp -a style.css images $tmpdir/$export
			cd $content/$export
			for d in $(find . -type f | sed s'!./!!')
			do
				d=${d%.txt}
				[ "$d" == "en/help" ] && continue
				gettext "Exporting: "; echo "$d.txt"
				mkdir -p $tmpdir/$export/$(dirname $d)
				f=$tmpdir/$export/$d.html
				html_header > ${f}
				sed -i '/functions.js/'d ${f}
				sed -i '/favicon.ico/'d ${f}
				sed -i s'/index.cgi/index.html/'/ ${f}
				doc="[0-9a-zA-Z\.\#/~\_%=\?\&,\+\:@;!\(\)\*\$'\-]*"
				#
				# The sed from wiki urls to html bug if there is 2 links
				# on same line: [test|Test] tralala [en/index|English]
				#
				cat $d.txt | wiki_parser | sed \
					s"#href='\([^]]*\)?d=\($doc\)'>#href='\2.html'>#"g >> ${f} 
				html_footer >> ${f}
			done
			cd $tmpdir/$export
			css_path
			gen_tarball
			rm -rf $tmp/export/$$
			echo '</pre>'
			dl_link ;;
		*\ export\ ) html_footer && exit 0 ;;
		*)
			echo '<pre>'
			gettext "Export not yet implemented for"; echo ": $(GET export)"
			echo '</pre>' ;;
	esac
	
	html_footer && exit 0
fi
