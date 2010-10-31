Clouseau

Authors:

    Andy McKay

Credits and Thanks:

    Lots of great work on this at the initial Vancouver sprint:
    
        Leonardo Rochael Almeida
        Richard Amerman

    Enfold Systems, space for Vancouver sprint and developer time
    Blue Fountain, for developer time
    7TechNW, developer time
    Tiberiu Ichim, developer time
    
    Testing and feedback:
    
        Wichert Akkerman
        Volodymyr Cherepanyak
        Johannes Ammonl
        Laurence Rowe
        Maik Röder

License:

    GPL, see License.GPL

What is it?

    It's a Ajax based Zope/Python prompt. Think of it is a replacement for zopectl debug.

Dependencies

    Recent browser tested on Safari, Firefox 1.5

    Zope 2.9 + 

    Plone 2.5

    May work in others, but this is what it was tested on.

    Warning not tested on:
    
        IE since 0.1 release. I don't own a Windows computer (and don't want to). Any help or debugging from users of IE appreciated. Unfortunately, just telling me it does not work on IE is not enough, I need patches.
	
	Optional:
	
	    If you have DocFinderTab installed, you will get more detailed tooltips.
	    
	    Find DocFinderTab here: http://www.zope.org/Members/shh/DocFinderTab
	
Doesn't work with

    Using Clouseau when PDBDebugMode is installed and active results in weird behaviour and lockdowns.
    
It's a what?

    A Python prompt that allows you to interact with your Zope site. It does this with an Ajax interface, so you can do this right from the ui.
    
How do I use it?

    Download product and drop the Clouseau directory into your Products directory. Just like any other product. Restart Zope.
    
    In Plone go to site setup > add/remove products. Install Clouseau.
    
    Then go to site setup > Clouseau.
    
    Click "create a new session".
    
    Play.
    
    --- or
    
    Go to a content item.
    
    Click on the little magnifying glass.
    
    Play.

Is it secure?

    Probably not. All the methods that interact with the application are protected by Zope security. So if you trust that code, you'll be happy. However chances are if you know Plone and Zope you might be screaming at this point.
    
    It does fly in the face of the traditional security model a bit, although essentially you are allowing anyone who has Manager to do anything to your site. Running this on a production site is crazy. From the page template in Clouseau...
    
    Warning: this tool allows users to interact with your Zope at its most basic level. It will allow a user to add, edit, delete any data in the site  ignoring all security. This tool should only be used on development sites. If you are at all unsure, stop, back away and uninstall this product immediately and go and read the documentation in the source.
    
First, how can I protect my installation?

    There are two variables *enabled* and *enabled_only_in_debug_mode*. Both of these are defined in config.py. If you would like to turn Clouseau off, then set enabled = False. If you'd like clouseau to work only when Zope is in debug-mode then leave *enabled_only_in_debug_mode* = True.
    
    Note: by default Clouseau is set to *enabled* = True and *enabled_only_in_debug_mode* = True. If you are running in production mode, restart your server in debug-mode.
    
Next, will this work?

    Probably. It's got quite a way to go yet. See to do.

Why browser based?

    1) Ease of end users, this has NO dependencies (compare to PloneShell or zopectl)
    
    2) Collaborative debugging, multiple people can join a session and see the same data
    
    3) Lots of features we haven't gotten too yet.
    
    4) Ease of development, no hacking down in wxPython or Zope sources.