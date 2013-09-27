LOGGING_SERVER=www.sidefx.com
LOGGING_SERVER_USER=root
QUERY_SERVER=internal.sidefx.com
QUERY_SERVER_USER=prisms

INSTALL_DIR=/var/www/stats
TEMP_DIR=~/stats_backup
TIMESTAMP=$(shell date +"%Y-%m-%d")
BACKUP_DIR=$(TEMP_DIR)/$(TIMESTAMP)
SOURCE_FILE_NAME=source.tar
DB_DUMP_FILE_NAME=db_backup.tar.gz

RELEASE_FILES=\
	Makefile \
	*.py \
	wsgi-script/django.wsgi

RELEASE_DIRS=\
	static \
	templates \
	houdini_stats \
	houdini_licenses

package_source:
	@# Create the package of source files to copy to the server.
	rm -f $(SOURCE_FILE_NAME)
	tar cf $(SOURCE_FILE_NAME) $(RELEASE_FILES) $(RELEASE_DIRS)

push:
	$(MAKE) package_source

	@# In case this is the first time updating the servers, make sure the
	@# temporary directories exist.
	ssh $(QUERY_SERVER_USER)@$(QUERY_SERVER) "mkdir -p $(TEMP_DIR)"
	ssh $(LOGGING_SERVER_USER)@$(LOGGING_SERVER) "mkdir -p $(TEMP_DIR)"

	@# Copy the source and the Makefile to the servers.
	scp $(SOURCE_FILE_NAME) Makefile $(QUERY_SERVER_USER)@$(QUERY_SERVER):$(TEMP_DIR)/
	scp $(SOURCE_FILE_NAME) Makefile $(LOGGING_SERVER_USER)@$(LOGGING_SERVER):$(TEMP_DIR)/

	@# Run the target on the server.
	ssh $(QUERY_SERVER_USER)@$(QUERY_SERVER) "cd $(TEMP_DIR) && sudo make apply_updates_on_server NO_MIGRATIONS=1 TEMP_DIR=$(TEMP_DIR)"
	ssh $(LOGGING_SERVER_USER)@$(LOGGING_SERVER) "cd $(TEMP_DIR) && sudo make apply_updates_on_server"

local_push:
	$(MAKE) package_source
	mkdir -p $(TEMP_DIR)
	cp $(SOURCE_FILE_NAME) Makefile $(TEMP_DIR)/
	(cd $(TEMP_DIR) && sudo make apply_updates_on_server)

apply_updates_on_server:
	@# Back up the old source code and database.  If this is the query
	@# server the database will just contain django and south tables, but
	@# that's ok.
	@# TODO: If it's the first time, we also need to do a syncdb.
	(if [ -e $(INSTALL_DIR) ]; then \
	    mkdir -p $(BACKUP_DIR); \
	    (cd $(INSTALL_DIR) && tar cf $(BACKUP_DIR)/$(SOURCE_FILE_NAME) .); \
	    (cd $(INSTALL_DIR) && $(MAKE) dump); \
	    mv $(INSTALL_DIR)/$(DB_DUMP_FILE_NAME) $(BACKUP_DIR)/; \
	else \
	    mkdir -p $(INSTALL_DIR); \
	fi)

	@# Copy the new source code
	if [ "$(INSTALL_DIR)" != "" ]; then rm -rf $(INSTALL_DIR)/*; fi
	(cd $(INSTALL_DIR) && tar xf $(TEMP_DIR)/$(SOURCE_FILE_NAME))

	@# Apply any migrations, unless we've been told not too.
	(if [ "$(NO_MIGRATIONS)" = "" ]; then \
	    (cd $(INSTALL_DIR) && ./manage.py migrate) \
	fi)

	@# Change file ownerships away from root.
	(cd $(INSTALL_DIR) && chown -R www-data:www-data *)

	@# Restart the server.
	/etc/init.d/apache2 restart

dump:
	./manage.py backupdb > db_backup.sql
	tar cfz $(DB_DUMP_FILE_NAME) db_backup.sql
	rm db_backup.sql

load:
	tar xfz $(DB_DUMP_FILE_NAME)
	./manage.py cleardatabase
	./manage.py backupdb -l db_backup.sql
	./manage.py migrate
	rm db_backup.sql

