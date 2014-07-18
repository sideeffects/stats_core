from django.db import models
import django.db.models.options as options

# Keep django from complaining about the db_name meta attribute.
if "db_name" not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("db_name",)
    

class Machine(models.Model):
    """
    Represent a unique machine.
    """    
    
    hardware_id = models.CharField(
        help_text='''Mac address hash.''',
        max_length=80,
        default=''
    )
        
    def __unicode__(self):
        return "Machine(%s)" % (self.hardware_id)

    class Meta:
        # How to order results when doing queries:
        db_name = 'stats'

#-------------------------------------------------------------------------------

class MachineConfig(models.Model):
    """
    Represent a particular configuration for a machine.
    """

    machine = models.ForeignKey(
        'Machine',
        help_text='''The machine associated with this machine config.''',
    )

    creation_date = models.DateTimeField(
        help_text='''When this machine config was created.''',
        auto_now_add=True,
    )

    config_hash = models.CharField(
        help_text='''Hash of the information from the user machine.''',
        max_length=80
    )    
    
    ip_address = models.CharField(
        help_text='''IP address.''',
        max_length=25,
        blank=True,
    )

    graphics_card = models.CharField(
        help_text='''Graphic card used in the current machine.''',
        max_length=40,
        blank=True,                               
    )
    
    graphics_card_version = models.CharField(
        help_text='''Graphic card version.''',
        max_length=40,
        blank=True,                               
    )
    
    operating_system = models.CharField(
        help_text='''Operating System installed in the machine.''',
        max_length=40,
        blank=True,                              
    )

    system_memory = models.FloatField(
        help_text='''System memory.''',
        default=0,
        blank=True,
    )
    
    system_resolution = models.CharField(
        help_text='''System resolution.''',
        max_length=40,
        blank=True,
    )
    
    number_of_processors = models.PositiveIntegerField(
        help_text='''Number of processors the machine has.''',
        default=0,
        blank=True,
        
    )
                        
    cpu_info = models.CharField(
        help_text='''CPU information.''',
        max_length=60,
        blank=True,
                                       
    )
    
    raw_user_info = models.TextField(
        help_text='''All the machine info data that was sent from Houdini.''',
        blank=True,
        default=''
    )
    
    def __unicode__(self):
        return "MachineConfig(%s, %s)" % (
            self.machine.hardware_id, self.config_hash)

    class Meta:
        # How to order results when doing queries:
        ordering = ('creation_date', )
        db_name = 'stats'
            
#-------------------------------------------------------------------------------

class LogId(models.Model):
    """
    LogId to identify which stats have been already saved in the db and not
    save the same info more than once.
    """
    
    log_id = models.CharField(
        help_text='''Lod id.''',
        max_length=80
    )  

    machine_config = models.ForeignKey(
        'MachineConfig',
        help_text='''The machine config associated with this log.''',
    )

    logging_date = models.DateTimeField(
        help_text='''When this particular log was saved.''',
        auto_now_add=True,
    )
    
    def __unicode__(self):
        return "LogId(%s, %s)" % (
            self.log_id, self.machine_config.config_hash)

    class Meta:
        # How to order results when doing queries:
        ordering = ('logging_date',)
        db_name = 'stats'
            
#-------------------------------------------------------------------------------

class Event(models.Model):
    """
    Represent an Event that will be used to annotate specific dates in the
    reports.
    """
    
    title = models.CharField(
        help_text='''The title of the event.''',
        max_length=40
    )   
    
    date = models.DateTimeField(
        help_text='''Date when the event took place.'''
    )
    
    description = models.TextField(
        help_text='''Brief Description of the event.''',
        blank=True,
        default=''
    ) 
    
    show = models.BooleanField(
        help_text='''To hide or show an event from the graphs''',
        default=False
    )
        
    def __unicode__(self):
        return "Event(%s, %s)" % \
            (self.title, self.date)
        
    class Meta:
        # How to order results when doing queries:
        ordering = ('date',)    
        db_name = 'stats'

#-------------------------------------------------------------------------------

class ErrorLog(models.Model):
    """
    Model to store possible errors like empty json files.
    """
    
    description = models.TextField(
        help_text='''Brief Description of the nature of the error.''',
        blank=True,
        default=''
    )
    
    stack_trace = models.TextField(
        help_text='''Stack Trace for the error.''',
        blank=True,
        default=''
    )   
    
    date = models.DateTimeField(
        help_text='''Date when the event took place.'''
    )
    
    def __unicode__(self):
        return "ErrorLog(%s, %s)" % \
            (self.description, self.date)
        
    class Meta:
        # How to order results when doing queries:
        ordering = ('date',)    
        db_name = 'stats'