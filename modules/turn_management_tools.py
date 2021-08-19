from . import text_tools
from . import actor_utility
from . import market_tools

def end_turn(global_manager):
    for current_mob in global_manager.get('mob_list'):
        current_mob.selected = False
    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), 'none')
    global_manager.set('player_turn', False)
    text_tools.print_to_screen("Ending turn", global_manager)
    for current_mob in global_manager.get('mob_list'):
        current_mob.end_turn_move()
    for current_resource_building in global_manager.get('resource_building_list'):
        current_resource_building.produce()
    manage_upkeep(global_manager)
    #do things that happen at end of turn
    start_turn(global_manager, False)

def start_turn(global_manager, first_turn):
    global_manager.set('player_turn', True)
    text_tools.print_to_screen("", global_manager)
    text_tools.print_to_screen("Starting turn", global_manager)
    global_manager.get('turn_tracker').change(1)
    for current_mob in global_manager.get('mob_list'):
        current_mob.reset_movement_points()
    if not first_turn:
        market_tools.adjust_prices(global_manager)#adjust_prices(global_manager)

def manage_upkeep(global_manager):
    num_workers = global_manager.get('num_workers')
    worker_upkeep = global_manager.get('worker_upkeep')
    total_upkeep = num_workers * worker_upkeep
    global_manager.get('money_tracker').change(-1 * total_upkeep)
    text_tools.print_to_screen("You paid " + str(worker_upkeep) + " money for each of your " + str(num_workers) + " workers, totaling to " + str(total_upkeep) + " money", global_manager)

