TIMESTAMP=$(shell date +"%Y-%m-%d")
SERVER=www.sidefx.com
INSTALL_DIR=/var/www/stats
TEMP_DIR=/root/stats_backup
BACKUP_DIR=/root/stats_backup/$(TIMESTAMP)
SOURCE_FILE_NAME=source.tar.gz
DB_DUMP_FILE_NAME=db_backup.tar.gz

RELEASE_FILES=\
	*.py \

RELEASE_DIRS=\
	static \
	templates \
	houdini_stats

push:
	# Create the package of source files to copy to the server.
	tar cfz $(SOURCE_FILE_NAME) --file $(RELEASE_FILES)
	for dir in $(RELEASE_DIRS); do \
	    tar Afz $(SOURCE_FILE_NAME) `find $$dir --exclude='.svn'`
	done

	# Copy the source and the makefile to the server.
	scp $(SOURCE_FILE_NAME) Makefile root@$(SERVER):$(TEMP_DIR)/

	# Run the target on the server.
	ssh root@$(SERVER) "cd $(TEMP_DIR) && make apply_updates_on_server"

apply_updates_on_server:
	# Back up the old source code.
	mkdir -p $(BACKUP_DIR)
	(cd $(INSTALL_DIR) && tar cfz $(BACKUP_DIR)/source_backup.tar.gz .)

	# Back up the old database
	$(MAKE) dump
	cp $(DB_DUMP_FILE_NAME) $(BACKUP_DIR)/

	# Copy the new source code
	if [ "$(INSTALL_DIR)" != "" ]; then rm -rf $(INSTALL_DIR)/*; fi
	(cd $(INSTALL_DIR) && tar xfz $(TEMP_DIR)/$(SOURCE_FILE_NAME))

	# Apply any migrations.
	(cd $(INSTALL_DIR) && ./manage.py migrate)

	# Restart the server.
	/etc/init.d/apache2 restart

dump:
	./manage.py backupdb > $(DB_DUMP_FILE_NAME)

load:
	./manage.py cleardatabase
	./manage.py backupdb -l $(DB_DUMP_FILE_NAME)
	./manage.py migrate

