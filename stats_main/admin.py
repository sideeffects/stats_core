from django.contrib import admin
from stats_main.models import *

#-------------------------------------------------------------------------------

def admin_site_register(managed_class):
    """
    Decorator for simplifying registration.
    """
    def func(admin_class):
        admin.site.register(managed_class, admin_class)
    return func

##==============================================================================

class SelectRelatedModelAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'queryset' in kwargs:
            kwargs['queryset'] = kwargs['queryset'].select_related()
        else:
            db = kwargs.pop('using', None)
            kwargs['queryset'] = db_field.rel.to._default_manager.using(
                                 db).complex_filter(
                                 db_field.rel.limit_choices_to).select_related()
        return super(SelectRelatedModelAdmin, self).formfield_for_foreignkey(
                                                    db_field, request, **kwargs)
#-------------------------------------------------------------------------------

@admin_site_register(Machine)
class MachineAdmin(SelectRelatedModelAdmin):
    """
    Control how the admin site displays hardware ids.
    """
    #list_filter = ("hardware_id",)
    list_display = ("hardware_id",) 
    list_display_links = ("hardware_id",)
    list_per_page = 20

#-------------------------------------------------------------------------------

@admin_site_register(MachineConfig)
class MachineConfigAdmin(SelectRelatedModelAdmin):
    """
    Control how the admin site displays machine configurations.
    """
    #list_filter = ("config_hash", "machine", "creation_date",
    #               "operating_system", "graphics_card")
    
    list_display = ("config_hash", "machine", "creation_date",
                   "operating_system", "graphics_card") 
    list_display_links = ("config_hash", "machine", "creation_date")
    list_per_page = 20
    ordering = ["-creation_date"]

#-------------------------------------------------------------------------------

@admin_site_register(LogId)
class LogIdAdmin(SelectRelatedModelAdmin):
    """
    Control how the admin site displays Log Ids.
    """
    #list_filter = ("log_id", "machine_config", "logging_date")
    list_display = ("log_id", "machine_config", "logging_date") 
    list_display_links = list_display
    
    list_per_page = 20
    ordering = ["-logging_date"]

#-------------------------------------------------------------------------------

@admin_site_register(ErrorLog)
class ErrorLogAdmin(SelectRelatedModelAdmin):
    """
    Control how the admin site displays Error Logs 
    """
    #list_filter = ("description", "ip_address", "date")
    list_display = ("description", "ip_address", "date")
    list_display_links = list_display
    
    list_per_page = 20
    ordering = ["-date"]

#-------------------------------------------------------------------------------

@admin_site_register(Event)
class Event(admin.ModelAdmin):
    """
    Control how the admin site displays Events 
    """
    #list_filter = ("title", "date", "show")
    list_display = ("title", "date", "show") 
    list_display_links = list_display
    
    list_per_page = 20
    ordering = ["-date"]
