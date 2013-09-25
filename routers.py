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

