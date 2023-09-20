#Runs setup and main loop on program start

import modules.main_loop as main_loop
import modules.tools.data_managers as data_managers
from modules.setup import *

try:
    global_manager = data_managers.global_manager_template() #manages a dictionary of what would be global variables passed between functions and classes
    setup(global_manager, debug_tools, fundamental, misc, terrains, commodities, def_ministers, def_countries, transactions, lore, value_trackers, buttons, europe_screen,
            ministers_screen, trial_screen, new_game_setup_screen, mob_interface, tile_interface, unit_organization_interface, inventory_interface, minister_interface,
            country_interface
    )
    main_loop.main_loop(global_manager)

except Exception: #displays error message and records error message in crash log file   
    manage_crash(Exception)

# tasks:
# look into adding text on map, such as village names - should be a generalizable procedure that works similarly to tile images or cell icons, with some way to easily
#   create a rendered text object with a string message and offset parameters
# look into a procedure that prompts for text input and prevents any other actions to get things like port names, with some level of input validation
# action notifications rework - current design of each action having a different notification class and type with its own choice button types to do very similar
#   functionality is very inefficient and impedes future development - there should be a single action notification class that can accept an input dictionary with values
#   that any individualized behaviors rely on
# fix double minister image on capture slaves notifications
# fix notification scaling issues - possibly an issue with font size scaling in notification_manager.notification_to_front
# continue replacing instances of notification_utility.display_notification(, also need to replace choice and zoom notifications (and maybe minister message)
# restrict notification queue manipulation to the notification manager - removing notification should just tell notification manager to check for queued notifications,
#   rather than directly handling the notification queue all over the program - a notification_dict should be popped the moment it is used to make a notification
# ^until this is correctly implemented, essentially all action notifications will be broken
#   clicking on a notification/choice button shouldn't "remove" notification - should have a new recursive remove function to remove above collection
