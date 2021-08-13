import random

def create_image_dict(stem):
    '''
    Input:
        string representing the path to a folder of an actor's images
    Output:
        Returns a dictionary of key strings of descriptions of images and corresponding values of the images' file paths
    '''
    '''if stem is a certain value, add extra ones, such as special combat animations: only works for images in graphics/mobs'''
    stem = 'mobs/' + stem
    stem += '/'#goes to that folder
    image_dict = {}
    image_dict['default'] = stem + 'default.png'
    image_dict['right'] = stem + 'right.png'  
    image_dict['left'] = stem + 'left.png'
    return(image_dict)

def can_merge(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Returns whether the player is able to merge a worker and an officer. A single worker and a single officer must be the only mobs selected to merge them into a group.
        If the correct mobs are selected but they are in different locations, this will return True and the merge button will show, but pressing it will prompt the user to move them to the same location.
    '''
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 1:
        officer_present = False
        worker_present = False
        for current_selected in selected_list:
            if current_selected in global_manager.get('officer_list'):
                officer_present = True
                for current_mob in current_selected.images[0].current_cell.contained_mobs:
                    if current_mob in global_manager.get('worker_list'):
                        worker_present = True
        if officer_present and worker_present:
            return(True)
        else:
            return(False)
    return(False)

def can_split(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Returns whether the player is able to split a group. A single group and no other mobs must be selected to split the group.
    '''
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 1 and selected_list[0] in global_manager.get('group_list'):
        return(True)
    return(False)

def can_embark_vehicle(global_manager): #if 1 vehicle and 1 non-vehicle selected
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 2:
        if (selected_list[0].is_vehicle and selected_list[0].has_crew and not selected_list[1].is_vehicle) or ((not selected_list[0].is_vehicle) and selected_list[1].is_vehicle and selected_list[1].has_crew):
            #1 of each, vehicle must have crew
            if(selected_list[0].x == selected_list[1].x and selected_list[0].y == selected_list[1].y and selected_list[0].grids[0] in selected_list[1].grids): #if on same coordinates on same grid
                return(True) #later check to see if vehicle has room
    return(False)

def can_disembark_vehicle(global_manager): #if 1 vehicle with any contents is selected
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 1:
        if selected_list[0].is_vehicle:
            if len(selected_list[0].contained_mobs) > 0: #or if any commodities carried
                return(True)
    return(False)

def can_crew_vehicle(global_manager):
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 2:
        if (selected_list[0].is_vehicle and not selected_list[0].has_crew and selected_list[1].is_worker) or (selected_list[0].is_worker and selected_list[1].is_vehicle and not selected_list[1].has_crew):
            #1 of each, vehicle must not have crew
            if(selected_list[0].x == selected_list[1].x and selected_list[0].y == selected_list[1].y and selected_list[0].grids[0] in selected_list[1].grids): #if on same coordinates on same grid
                return(True) #later check to see if vehicle has room
    return(False)

def can_uncrew_vehicle(global_manager):
    selected_list = get_selected_list(global_manager)
    if len(selected_list) == 1:
        if selected_list[0].is_vehicle:
            if selected_list[0].has_crew and len(selected_list[0].contained_mobs) == 0: #crew can only leave if has crew and no passengers
                return(True)
    return(False) 
    
def get_selected_list(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Returns a list of all selected mobs
    '''
    selected_list = []
    for current_mob in global_manager.get('mob_list'):
        if current_mob.selected:
            selected_list.append(current_mob)
    return(selected_list)

def get_random_ocean_coordinates(global_manager):
    mob_list = global_manager.get('mob_list')
    mob_coordinate_list = []
    #start_x, start_y = (0, 0)
    #while True: #to do: prevent 2nd row from the bottom of the map grid from ever being completely covered with water due to unusual river RNG, causing infinite loop here, or start increasing y until land is found
    start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
    start_y = 0
    #if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
    #    break
    return(start_x, start_y)

def calibrate_actor_info_display(global_manager, info_display_list, new_actor):
    '''
    Input:
        global_manager_template object, list of buttons and actors representing the objects that should be calibrated to the inputted actor, actor representing what the inputted buttons and actors should be calibrated to
    Output:
        Uses the calibrate function of each of the buttons and actors in the inputted info_display_list, causing them to reflect the appearance or information relating to the inputted actor 
    '''
    if info_display_list == global_manager.get('tile_info_display_list'):
        global_manager.set('displayed_tile', new_actor)
    elif info_display_list == global_manager.get('mob_info_display_list'):
        global_manager.set('displayed_mob', new_actor)
    for current_object in info_display_list:
        current_object.calibrate(new_actor)
    
