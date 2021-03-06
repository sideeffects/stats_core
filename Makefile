LOGGING_SERVER=$(shell hostname)
LOGGING_SERVER_USER=root
QUERY_SERVER=$(shell hostname)
QUERY_SERVER_USER=root
INSTALL_DIR=/var/www/stats

TEMP_DIR=~/stats_backup
TIMESTAMP=$(shell date +"%Y-%m-%d")
BACKUP_DIR=$(TEMP_DIR)/$(TIMESTAMP)
SOURCE_FILE_NAME=source.tar
DB_DUMP_FILE_NAME=db_backup.tar.gz
HOU_LOGS_FILE=houdini_logs.txt

package_source:
	@# Create the package of source files to copy to the server.
	rm -f $(SOURCE_FILE_NAME)
	python package_source.py

push:
	$(MAKE) package_source

	@# In case this is the first time updating the servers, make sure the
	@# temporary directories exist.
	if [ $(QUERY_SERVER) != $(LOGGING_SERVER) ]; then \
	    ssh $(QUERY_SERVER_USER)@$(QUERY_SERVER) "mkdir -p $(TEMP_DIR)"; \
	fi
	ssh $(LOGGING_SERVER_USER)@$(LOGGING_SERVER) "mkdir -p $(TEMP_DIR)"

	@# Copy the source and the Makefile to the servers.
	if [ $(QUERY_SERVER) != $(LOGGING_SERVER) ]; then \
	    scp $(SOURCE_FILE_NAME) Makefile $(QUERY_SERVER_USER)@$(QUERY_SERVER):$(TEMP_DIR)/; \
	fi
	scp $(SOURCE_FILE_NAME) Makefile $(LOGGING_SERVER_USER)@$(LOGGING_SERVER):$(TEMP_DIR)/

	@# Run the target on the server.
	if [ $(QUERY_SERVER) != $(LOGGING_SERVER) ]; then \
	    ssh $(QUERY_SERVER_USER)@$(QUERY_SERVER) "cd $(TEMP_DIR) && sudo make apply_updates_on_server NO_MIGRATIONS=1 TEMP_DIR=$(TEMP_DIR)"; \
	fi
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
	    if [ ! -e $(INSTALL_DIR)/$(HOU_LOGS_FILE) ]; then \
                touch $(INSTALL_DIR)/$(HOU_LOGS_FILE); \
	    fi; \
	    (cd $(INSTALL_DIR) && tar cf $(BACKUP_DIR)/$(SOURCE_FILE_NAME) . --exclude='$(HOU_LOGS_FILE)') && \
	    (cd $(INSTALL_DIR)/stats_core && $(MAKE) dump) && \
	    mv $(INSTALL_DIR)/stats_core/$(DB_DUMP_FILE_NAME) $(BACKUP_DIR)/; \
	else \
	    mkdir -p $(INSTALL_DIR)/stats_core; \
	    touch $(INSTALL_DIR)/$(HOU_LOGS_FILE); \
	fi)

	@# Copy the new source code.  Leave the houdini_logs.txt file in
	@# the toplevel folder.
	if [ "$(INSTALL_DIR)" != "" ]; then rm -rf $(INSTALL_DIR)/stats_core $(INSTALL_DIR)/stats_houdini $(INSTALL_DIR)/stats_sesi_internal; fi
	(cd $(INSTALL_DIR) && tar xf $(TEMP_DIR)/$(SOURCE_FILE_NAME))
	
	@# Apply any migrations, unless we've been told not too.
	(if [ "$(NO_MIGRATIONS)" = "" ]; then \
	    (cd $(INSTALL_DIR)/stats_core && (echo "no" | ./manage.py syncdb)) && \
            (cd $(INSTALL_DIR)/stats_core && ./manage.py migrate); \
	fi)

	@# Change file ownerships away from root.
	(cd $(INSTALL_DIR) && chown -R www-data:www-data *)

	@# Restart the server.
	/etc/init.d/apache2 restart

# We need to avoid tar errors about "file changed as we read it" when backing
# up the houdini log file.
dump:
	./manage.py backupdb -d stats > db_backup_stats.sql
	./manage.py backupdb -d default > db_backup_stats_django_skeleton.sql
	cp ../$(HOU_LOGS_FILE) $(HOU_LOGS_FILE).backup
	tar cfz $(DB_DUMP_FILE_NAME) --transform='s|$(HOU_LOGS_FILE).backup|$(HOU_LOGS_FILE)|' db_backup_stats.sql db_backup_stats_django_skeleton.sql $(HOU_LOGS_FILE).backup
	rm $(HOU_LOGS_FILE).backup db_backup_stats.sql db_backup_stats_django_skeleton.sql

load:
	tar xfz $(DB_DUMP_FILE_NAME)
	./manage.py cleardatabase -d stats
	./manage.py cleardatabase -d default
	./manage.py backupdb -d stats -l db_backup_stats.sql
	./manage.py backupdb -d default -l db_backup_stats_django_skeleton.sql
	./manage.py migrate
	mv $(HOU_LOGS_FILE) ..
	rm db_backup_stats.sql db_backup_stats_django_skeleton.sql

run:
	./manage.py runserver
	
# Allow a Makefile.local to override things.
-include Makefile.local
