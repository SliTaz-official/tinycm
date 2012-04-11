#!/bin/sh
#
# TinyCM Plugin - Export to static content
#
. /usr/lib/slitaz/httphelper

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
$(gettext "Export to HTML and ceate a tarball of your text content or
uploaded files.")
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
		cd $tmpdir && mkdir $TINYCM/$cache/export
		# Clean cache
		find $TINYCM/$cache/export -mtime +1 | xargs rm -rf
		tar czf $TINYCM/$cache/export/$export-$date.tar.gz $export
		cd $TINYCM/$cache/export && du -sh $export-$date.tar.gz
	}
	dl_link() {
		gettext "Download"; echo \
			": <a href='cache/export/$export-$date.tar.gz'>$export-$date.tar.gz</a>"
	}
	# Export requested content
	case " $(GET export) " in
		*\ uploads\ *)
			export="uploads"
			tmpdir="content"
			echo '<pre>'
			gettext "Exporting:"; echo " $export"
			gen_tarball
			echo '</pre>' 
			dl_link ;;
		*)
			[ "$(GET export)" == "export" ] && exit 0
			export="$(GET export)"
			format="html"
			echo '<pre>'
			gettext "Exporting:"; echo " $export"
			gettext "Creating tmp directory:"; echo " PID $$ DATE $date"
			mkdir -p $tmpdir/$export
			gettext "Copying CSS style and images..."; echo
			cp -a style.css images $tmpdir/$export
			cd $content/$export
			for d in $(find . -type f | sed s'!./!!')
			do
				d=${d%.txt}
				[ "$d" == "help" ] && continue
				gettext "Exporting: "; echo "$d.txt"
				mkdir -p $tmpdir/$export/$(dirname $d)
				f=$tmpdir/$export/$d.html
				html_header > $f
				sed -i '/functions.js/'d $f
				sed -i '/favicon.ico/'d $f
				cat $d.txt | wiki_parser | sed \
					-e '/functions.js/'d \
					-e s'/?d=//'g \
					-e s"#href='\([^']*\)*\>#\0.html#"g >> $f 
				html_footer >> $f
			done
			cd $tmpdir/$export
			[ "$format" == "html" ] && css_path
			gen_tarball
			gettext "Removing temporary files..."; echo
			rm -rf $tmp/export/$$
			echo '</pre>'
			dl_link ;;
	esac
	
	html_footer
	exit 0
fi
