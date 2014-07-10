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

@admin_site_register(Machine)
class MachineAdmin(admin.ModelAdmin):
    """
    Control how the admin site displays hardware ids.
    """
    list_filter = ("hardware_id",)
    list_display = list_filter 
    list_display_links =("hardware_id",)
    list_per_page = 20

#-------------------------------------------------------------------------------

@admin_site_register(MachineConfig)
class MachineConfigAdmin(admin.ModelAdmin):
    """
    Control how the admin site displays machine configurations.
    """
    list_filter = ("config_hash", "machine", "creation_date",
                   "operating_system", "graphics_card", 
                   #"houdini_major_version", "houdini_minor_version", 
                   #"product", "is_apprentice"
                   ) 
    list_display = list_filter 
    list_display_links =("config_hash", "machine", "creation_date")
    list_per_page = 20
    ordering = ["-creation_date"]

#-------------------------------------------------------------------------------

@admin_site_register(LogId)
class LogIdAdmin(admin.ModelAdmin):
    """
    Control how the admin site displays Log Ids.
    """
    list_filter = ("log_id", "machine_config", "logging_date")
    list_display = list_filter 
    list_display_links =list_filter
    
    list_per_page = 20
    ordering = ["-logging_date"]


