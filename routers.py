import settings

class DBRouter(object):
    """A router to control database operations"""
    
    def db_for_read(self, model, **hints):
        """
        If model has db_name in the meta always read from that db_name.
        """
        if hasattr(model._meta, "db_name"):
            return model._meta.db_name
        return None

    def db_for_write(self, model, **hints):
        """
        If model has db_name in the meta always write from that db_name.
        """
        if hasattr(model._meta, "db_name"):
            return model._meta.db_name
        return None

    def allow_migrate(self, db, model):
        actual_db = db
        if hasattr(model._meta, "db_name"):
            actual_db = model._meta.db_name

        if actual_db == "default":
            return True
        if actual_db != "stats":
            return False
        assert actual_db == "stats"
        return settings.IS_LOGGING_SERVER

