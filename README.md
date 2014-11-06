stats_core
==========

The stats_core package implements the core infrastructure for collecting statistics data and generating reports. This package is part of the [Houdini Anonymous Usage  Statistics](http://www.sidefx.com/index.php?option=com_content&task=view&id=2686) project, but it is genericity make it easily adaptable for any data collection system. With this package installed you will be able to:

* Create your own server at your facility and make your desire apps point to it 

  For the case of Houdini, by default the data collected from inside Houdini will be sent to our servers, but you can send the data collected to your own servers by setting the environment variable HOUDINI_STATS_API_URL to point to your server; somenthing like http://www.servername.com/stats/api.  

* Record usage data and more for any app you add as add-on

  By default we have stats_houdini installed as an add on. But you can add other ones by adding new apps to your project and adding them as extension in settings.py 
  
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
https://github.com/sideeffects/stats_houdini. If you wish to add other extensions, edit settings.py
and change STATS_EXTENSIONS to include the extension.
