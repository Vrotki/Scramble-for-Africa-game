#Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(debug_tools, misc, terrains, commodities, def_ministers, def_countries, transactions, actions, lore, value_trackers, buttons, europe_screen,
            ministers_screen, trial_screen, new_game_setup_screen, mob_interface, tile_interface, unit_organization_interface, inventory_interface, minister_interface,
            country_interface
    )
    main_loop.main_loop()

except Exception: #displays error message and records error message in crash log file
    manage_crash(Exception)

# tasks:
#   general:
# make sure version of game on GitHub works when cloned - missing things like Belgian music folder, save game folder
# replace usages of 'none' with None
# Add type hints on sight - gradual process
#
#   new features:
# make generic contested action type
# add minister speech bubbles
# look into default tab modes, maybe with units with commodiy capacity going to inventory mode
# add Asian workers, maybe with starting upkeep bonus for Britain and (less so) France - 4.0 upkeep, from abstract grid, no penalty for firing, European attrition,
#   no slums, otherwise like African
# look into a procedure that prompts for text input and prevents any other actions to get things like port names, with some level of input validation
#      would need to modify text box to capture the output for a particular purpose, with a standard listen/receive function
#       when an object uses listen, it starts the typing process and captures the output when typing is cancelled or entered
#       the text box should call the receive function of the current listener
# incorrect behavior when attacked while in vehicle/resource building - includes graphical error with unit not showing afterward
# add settlement name label with indented building labels
#Allow ship moving through series of ports adjacent to the river
#   would allow moving past it. Units with canoes can move through with 4 movement points (maybe same as without canoes) - implement as generic terrain
#   feature that could be ported over approximately 0.1 chance per river tile, 1-2 desired per river
# add f. lname labels under cabinet portraits in minister (and trial?) screen
# add confirmation for free all slaves button
# Add boarding pending state - unit can enter pending state if attempting to board with 0 or 2+ crewed vehicles present, then a vehicle can pick up any
#   pending units - pending is a state like sentry mode
# Change slums to be based around settlements rather than buildings, and use settlement name in migration description
# Maybe have special corruption event involving Minister of Geography attempting to steal an artifact
# Add ambient resource production facility, settlement, and village sounds
# Allow some inventory attrition to occur in Europe
#
#   bugfixes
# continue looking for steamship crew disembarking error, possibly from enemies spawning on square (like failed missionaries) - occurs after combat
# Find some solution to overlapping 3rd work crew and text box
