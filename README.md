stats_core
==========

The stats_core package implements the core infrastructure for collecting statistics data and generating reports. This package is part of the [Houdini Anonymous Usage  Statistics](http://www.sidefx.com/index.php?option=com_content&task=view&id=2686) project, but it is generic enough to make it easily adaptable for any kind of data collection. 

With this package installed you will be able to:

* Create your own server at your facility and make your desire apps point to it 

  By default the data collected from inside Houdini will be sent to our servers, but you can send the data collected to your own servers by setting the environment variable HOUDINI_STATS_API_URL to point to your server, for example: http://www.servername.com/stats/api.  

* Record usage data for any app you add as add-on

  By default we have stats_houdini installed as an add on. But you can add other apps to your project by including them as extensions in settings.py 
  
  ```python

# Extension apps to be added to stats_core 
STATS_EXTENSIONS = (
    # In the current version stats_core project ALWAYS needs
    # the stats_houdini extension                
    "../stats_houdini", 
)

```

You can follow the instructions in INSTALL.txt to get your server up and running. 

-----------------------------------------------------------------------------------------------------------------
Currently, stats_core will not work unless the stats_houdini extension is also installed. You can download it from
https://github.com/sideeffects/stats_houdini. If you wish to add other extensions, remember to edit settings.py
and change STATS_EXTENSIONS to include the extension.
