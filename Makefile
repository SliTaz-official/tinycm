# Makefile for SliTaz Bugs.
#

PACKAGE="tinycm"
PREFIX?=/usr
DESTDIR?=
WEB?=/var/www/cgi-bin/tinycm
LOGIN?=/var/lib/slitaz
LINGUAS?=

all:

# i18n

pot:
	xgettext -o po/tinycm.pot -L Shell --package-name="TinyCM" \
		./index.cgi

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/$(PACKAGE).pot; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/$(PACKAGE).mo po/$$l.po; \
	done;

# Install

install:
	install -m 0700 -d $(DESTDIR)$(LOGIN)/people
	install -m 0700 -d $(DESTDIR)$(LOGIN)/auth
	install -m 0755 -d $(DESTDIR)$(WEB)/cache
	install -m 0777 -d $(DESTDIR)$(PREFIX)/share/applications
	#install -m 0777 -d $(DESTDIR)$(PREFIX)/share/locale
	
	cp -a config.cgi favicon.ico index.cgi style.css images lib \
		plugins content/ $(DESTDIR)$(WEB)
	#cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale
	install -m 0644 data/*.desktop $(DESTDIR)$(PREFIX)/share/applications
	
	# Set permissions
	chown -R www.www $(DESTDIR)$(LOGIN)/auth
	chown -R www.www $(DESTDIR)$(LOGIN)/people
	chown -R www.www $(DESTDIR)$(WEB)/content
	chown -R www.www $(DESTDIR)$(WEB)/cache

uninstall:
	rm -rf $(DESTDIR)$(WEB)
	rm $(DESTDIR)$(PREFIX)/share/applications/tinycm.desktop
