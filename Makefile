TIMESTAMP=$(shell date +"%Y-%m-%d")
SERVER=www.sidefx.com
INSTALL_DIR=/var/www/stats
TEMP_DIR=/root/stats_backup
BACKUP_DIR=/root/stats_backup/$(TIMESTAMP)
SOURCE_FILE_NAME=source.tar
DB_DUMP_FILE_NAME=db_backup.tar.gz

RELEASE_FILES=\
	Makefile \
	*.py \
	wsgi-script/django.wsgi

RELEASE_DIRS=\
	static \
	templates \
	houdini_stats

package_source:
	@# Create the package of source files to copy to the server.
	rm -f $(SOURCE_FILE_NAME)
	tar cf $(SOURCE_FILE_NAME) $(RELEASE_FILES) $(RELEASE_DIRS)

push:
	$(MAKE) package_source

	@# Copy the source and the makefile to the server.
	scp $(SOURCE_FILE_NAME) Makefile root@$(SERVER):$(TEMP_DIR)/

	@# Run the target on the server.
	ssh root@$(SERVER) "cd $(TEMP_DIR) && make -n apply_updates_on_server"

apply_updates_on_server:
	@# Back up the old source code and database.
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

	@# Apply any migrations.
	(cd $(INSTALL_DIR) && ./manage.py migrate)

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

