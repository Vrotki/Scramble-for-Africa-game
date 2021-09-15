import pygame
import time
from . import scaling
from . import text_tools
from . import actor_utility

def update_display(global_manager): #to do: transfer if current game mode in modes to draw functions, do not manage it here
    '''
    Input:
        global_manager_template object
    Output:
        Draws all images and shapes and calls the drawing of the text box and tooltips
    '''
    actor_utility.order_actor_info_display(global_manager, global_manager.get('mob_ordered_label_list'), global_manager.get('mob_ordered_list_start_y')) #global manager, list to order, top y of list
    actor_utility.order_actor_info_display(global_manager, global_manager.get('tile_ordered_label_list'), global_manager.get('tile_ordered_list_start_y'))
    if global_manager.get('loading'):
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 1) #makes it faster if the program starts repeating this part
        draw_loading_screen(global_manager)
    else:
        global_manager.get('game_display').fill((125, 125, 125))
        possible_tooltip_drawers = []

        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                current_grid.draw()

        for current_image in global_manager.get('image_list'):
            current_image.has_drawn = False

        for current_background_image in global_manager.get('background_image_list'):
            current_background_image.draw()
            current_background_image.has_drawn = True
            
        for current_tile in global_manager.get('tile_list'):
            if global_manager.get('current_game_mode') in current_tile.image.modes and not current_tile in global_manager.get('overlay_tile_list'):
                current_tile.image.draw()
                current_tile.image.has_drawn = True

        for current_infrastructure_connection in global_manager.get('infrastructure_connection_list'): #draw roads above terrain and below building icons, which are drawn below mobs
            current_infrastructure_connection.draw()
            current_infrastructure_connection.has_drawn = True

        mob_image_list = []
        for current_image in global_manager.get('image_list'):
            if not current_image.has_drawn:
                if global_manager.get('current_game_mode') in current_image.modes:
                    if not current_image.image_type == 'mob':
                        current_image.draw()
                        current_image.has_drawn = True
                    else:
                        mob_image_list.append(current_image)

        for current_image in mob_image_list:
            current_image.draw()
            current_image.has_drawn = True
                    
        for current_bar in global_manager.get('bar_list'):
            if global_manager.get('current_game_mode') in current_bar.modes:
                current_bar.draw()
                
        for current_overlay_tile in global_manager.get('overlay_tile_list'):
            if global_manager.get('current_game_mode') in current_overlay_tile.image.modes:
                current_overlay_tile.image.draw()
                current_overlay_tile.image.has_drawn = True
                
        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                current_grid.draw_grid_lines()

        displayed_tile = global_manager.get('displayed_tile')
        if not displayed_tile == 'none':
            displayed_tile.draw_actor_match_outline(False)

        for current_mob in global_manager.get('mob_list'):
            for current_image in current_mob.images:
                if current_mob.selected and global_manager.get('current_game_mode') in current_image.modes:
                    current_mob.draw_outline()
            if current_mob.can_show_tooltip():
                #print(current_mob.images[0].current_cell)
                for same_tile_mob in current_mob.images[0].current_cell.contained_mobs:
                    if same_tile_mob.can_show_tooltip() and not same_tile_mob in possible_tooltip_drawers: #if multiple mobs are in the same tile, draw their tooltips in order
                        possible_tooltip_drawers.append(same_tile_mob)

        for current_building in global_manager.get('building_list'):
            if current_building.can_show_tooltip():
                possible_tooltip_drawers.append(current_building)
            
        for current_actor in global_manager.get('actor_list'):
            if current_actor.can_show_tooltip() and not current_actor in possible_tooltip_drawers:
                possible_tooltip_drawers.append(current_actor) #only one of these will be drawn to prevent overlapping tooltips

        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                for current_cell in current_grid.cell_list:
                    current_cell.show_num_mobs()

        for current_button in global_manager.get('button_list'):
            if not (current_button in global_manager.get('button_list') and current_button.in_notification): #notifications are drawn later
                current_button.draw()
                if current_button.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                    possible_tooltip_drawers = [current_button]
                
        for current_label in global_manager.get('label_list'):
            if not (current_label in global_manager.get('button_list') and current_label.in_notification):
                current_label.draw()
                
        for current_button in global_manager.get('button_list'): #draws notifications and buttons attached to notifications
            if current_button.in_notification and not current_button == global_manager.get('current_instructions_page'):
                current_button.draw()
                if current_button.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                    possible_tooltip_drawers = [current_button]#notifications have priority over buttons and will be shown first

        for current_free_image in global_manager.get('free_image_list'):
            if current_free_image.to_front: #draw on top if free image should be in front
                current_free_image.draw()
                current_free_image.has_drawn = True
                
        if global_manager.get('show_text_box'):
            draw_text_box(global_manager)

        global_manager.get('mouse_follower').draw()

        #if global_manager.get('making_mouse_box'):
        #    mouse_destination_x, mouse_destination_y = pygame.mouse.get_pos()
        #    global_manager.set('mouse_destination_x', mouse_destination_x + 4)
        #    global_manager.set('mouse_destination_y', mouse_destination_y + 4)
        #    if abs(mouse_destination_x - global_manager.get('mouse_origin_x')) > 3 or (mouse_destination_y - global_manager.get('mouse_origin_y')) > 3:
        #        mouse_box_color = 'white'
        #        pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')[mouse_box_color], (min(global_manager.get('mouse_destination_x'), global_manager.get('mouse_origin_x')), min(global_manager.get('mouse_destination_y'), global_manager.get('mouse_origin_y')), abs(global_manager.get('mouse_destination_x') - global_manager.get('mouse_origin_x')), abs(global_manager.get('mouse_destination_y') - global_manager.get('mouse_origin_y'))), 3)
            
        if not global_manager.get('current_instructions_page') == 'none':
            instructions_page = global_manager.get('current_instructions_page')
            instructions_page.draw()
            if instructions_page.can_show_tooltip(): #while multiple actor tooltips can be shown at once, if a button tooltip is showing no other tooltips should be showing
                possible_tooltip_drawers = [instructions_page]#instructions have priority over everything
        if not (global_manager.get('old_mouse_x'), global_manager.get('old_mouse_y')) == pygame.mouse.get_pos():
            global_manager.set('mouse_moved_time', time.time())
            old_mouse_x, old_mouse_y = pygame.mouse.get_pos()
            global_manager.set('old_mouse_x', old_mouse_x)
            global_manager.set('old_mouse_y', old_mouse_y)
        if time.time() > global_manager.get('mouse_moved_time') + 0.15:#show tooltip when mouse is still
            manage_tooltip_drawing(possible_tooltip_drawers, global_manager)
        pygame.display.update()
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 3)

def action_possible(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Returns whether the player is allowed to do anything, preventing actions from being done before other actions are done
    '''
    if global_manager.get('ongoing_exploration'):
        return(False)
    elif global_manager.get('making_choice'):
        return(False)
    elif not global_manager.get('player_turn'):
        return(False)
    elif global_manager.get('choosing_destination'):
        return(False)
    return(True)


#def can_make_mouse_box(global_manager):
    #if action_possible(global_manager):
    #    return(True)
    #else:
    #    return(False)
#    return(True)

def draw_loading_screen(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Draws loading screen while the game is still loading
    '''
    global_manager.get('game_display').fill((125, 125, 125))
    global_manager.get('loading_image').draw()
    pygame.display.update()    
    if global_manager.get('loading_start_time') + 2 < time.time():#max of 1 second, subtracts 1 in update_display to lower loading screen showing time
        global_manager.set('loading', False)

def manage_tooltip_drawing(possible_tooltip_drawers, global_manager): #to do: if near bottom of screen, make first tooltip appear higher and have last tooltip on bottom of screen
    '''
    Input:
        list of objects that can draw tooltips based on the mouse position and their status, global_manager_template object
    Output:
        Draws tooltips of objecst that can draw tooltips, with tooltips beyond the first appearing at progressively lower locations
    '''
    possible_tooltip_drawers_length = len(possible_tooltip_drawers)
    font_size = scaling.scale_width(global_manager.get('font_size'), global_manager)
    y_displacement = scaling.scale_width(30, global_manager) #estimated mouse size
    if possible_tooltip_drawers_length == 0:
        return()
    elif possible_tooltip_drawers_length == 1:
        height = y_displacement
        height += font_size
        for current_text_line in possible_tooltip_drawers[0].tooltip_text:
            height += font_size
        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False
        if (global_manager.get('display_height') + 10 - mouse_y) - height < 0:
            below_screen = True
        possible_tooltip_drawers[0].draw_tooltip(below_screen, height, y_displacement)
    else:
        stopping = False
        height = y_displacement
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == global_manager.get('current_instructions_page'):
                height += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    height += font_size
                stopping = True
            if (possible_tooltip_drawer in global_manager.get('button_list') and possible_tooltip_drawer.in_notification) and not stopping:
                height += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    height += font_size
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                height += font_size
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    height += font_size

        mouse_x, mouse_y = pygame.mouse.get_pos()
        below_screen = False
        if (global_manager.get('display_height') + 10 - mouse_y) - height < 0:
            below_screen = True
        
        stopping = False
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == global_manager.get('current_instructions_page'):
                possible_tooltip_drawer.draw_tooltip(below_screen, height, y_displacement)
                y_displacement += scaling.unscale_width(font_size, global_manager)
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += scaling.unscale_width(font_size, global_manager)
                stopping = True
            if (possible_tooltip_drawer in global_manager.get('button_list') and possible_tooltip_drawer.in_notification) and not stopping:
                possible_tooltip_drawer.draw_tooltip(below_screen, height, y_displacement)
                y_displacement += scaling.unscale_width(font_size, global_manager)
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += scaling.unscale_width(font_size, global_manager)
                stopping = True
                
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                possible_tooltip_drawer.draw_tooltip(below_screen, height, y_displacement)
                y_displacement += scaling.unscale_width(font_size, global_manager)
                for current_text_line in possible_tooltip_drawer.tooltip_text:
                    y_displacement += scaling.unscale_width(font_size, global_manager)

def draw_text_box(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Draws the text box and any text it contains
    ''' 
    greatest_width = scaling.scale_width(300, global_manager)
    max_screen_lines = (scaling.scale_height(global_manager.get('default_display_height') // global_manager.get('font_size'), global_manager)) - 1
    max_text_box_lines = (scaling.scale_height(global_manager.get('text_box_height') // global_manager.get('font_size'), global_manager)) - 1
    font_name = global_manager.get('font_name')
    font_size = global_manager.get('font_size')
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            if text_tools.message_width(global_manager.get('text_list')[-text_index - 1], font_size, font_name) > greatest_width:
                greatest_width = text_tools.message_width(global_manager.get('text_list')[-text_index - 1], font_size, font_name) #manages the width of already printed text lines
    if global_manager.get('input_manager').taking_input:
        if text_tools.message_width("Response: " + global_manager.get('message'), font_size, font_name) > greatest_width: #manages width of user input
            greatest_width = text_tools.message_width("Response: " + global_manager.get('message'), font_size, font_name)
    else:
        if text_tools.message_width(global_manager.get('message'), font_size, font_name) > greatest_width: #manages width of user input
            greatest_width = text_tools.message_width(global_manager.get('message'), font_size, font_name)
    text_box_width = greatest_width + scaling.scale_width(10, global_manager)
    x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
    pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['white'], (x, y, text_box_width, global_manager.get('text_box_height'))) #draws white rect to prevent overlapping
    if global_manager.get('typing'):
        color = 'red'
    else:
        color = 'black'
    x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
    pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')[color], (x, y, text_box_width, global_manager.get('text_box_height')), scaling.scale_height(3, global_manager))
    pygame.draw.line(global_manager.get('game_display'), global_manager.get('color_dict')[color], (0, global_manager.get('display_height') - (font_size + scaling.scale_height(5, global_manager))),
        (text_box_width, global_manager.get('display_height') - (font_size + scaling.scale_height(5, global_manager))))
   # else:
   #     x, y = scaling.scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
   #     pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['black'], (x, y, text_box_width, global_manager.get('text_box_height')), 3)
   #     pygame.draw.line(global_manager.get('game_display'), global_manager.get('color_dict')['black'], (0, global_manager.get('display_height') - (font_size + 5)),
   #         (text_box_width, global_manager.get('display_height') - (font_size + 5)))

    global_manager.set('text_list', text_tools.manage_text_list(global_manager.get('text_list'), max_screen_lines)) #number of lines
    
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            textsurface = global_manager.get('myfont').render(global_manager.get('text_list')[(-1 * text_index) - 1], False, (0, 0, 0))
            global_manager.get('game_display').blit(textsurface,(scaling.scale_width(10, global_manager), (-1 * font_size * text_index) + global_manager.get('display_height') - ((2 * font_size) + scaling.scale_height(5, global_manager))))
    if global_manager.get('input_manager').taking_input:
        textsurface = global_manager.get('myfont').render('Response: ' + global_manager.get('message'), False, (0, 0, 0))
    else:
        textsurface = global_manager.get('myfont').render(global_manager.get('message'), False, (0, 0, 0))
    global_manager.get('game_display').blit(textsurface,(scaling.scale_width(10, global_manager), global_manager.get('display_height') - (font_size + scaling.scale_height(5, global_manager))))

def manage_rmb_down(clicked_button, global_manager):
    '''
    Input:
        boolean representing whether a button was just clicked (not pressed), global_manager_template object
    Output:
        Does nothing if the user was clicking a button, cycles through the mobs in a clicked location if user was not clicking a button, changing which mob is shown
    '''
    stopping = False
    if (not clicked_button) and action_possible(global_manager):
        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                for current_cell in current_grid.cell_list:
                    if current_cell.touching_mouse():
                        stopping = True #if doesn't reach this point, do same as lmb
                        if len(current_cell.contained_mobs) > 1:
                            moved_mob = current_cell.contained_mobs[1]
                            for current_image in moved_mob.images:
                                if not current_image.current_cell == 'none':
                                    while not moved_mob == current_image.current_cell.contained_mobs[0]:
                                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
                            global_manager.set('show_selection_outlines', True)
                            global_manager.set('last_selection_outline_switch', time.time())
                            if global_manager.get('minimap_grid') in moved_mob.grids:
                                global_manager.get('minimap_grid').calibrate(moved_mob.x, moved_mob.y)
                            moved_mob.select()
                            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), moved_mob.images[0].current_cell.tile)
    if not stopping:
        manage_lmb_down(clicked_button, global_manager)
    
def manage_lmb_down(clicked_button, global_manager): #to do: seems to be called when lmb/rmb is released rather than pressed, clarify name
    '''
    Input:
        boolean representing whether a button was just clicked (not pressed), global_manager_template object
    Output:
        Will do nothing if the user was clicking a button.
        If the user was not clicking a button and a mouse box was being drawn, the mouse box will stop being drawn and all mobs within it will be selected.
        If the user was not clicking a button, was not drawing a mouse box, and clicked on a cell, the top mob (the displayed one) in that cell will be selected.
        If the user was not clicking a button, any mobs not just selected will be unselected. However, if shift is being held down, no mobs will be unselected.
    '''
    if (not clicked_button) and action_possible(global_manager):#do not do selecting operations if user was trying to click a button
        mouse_x, mouse_y = pygame.mouse.get_pos()
        selected_new_mob = False
        if (not global_manager.get('capital')):
            actor_utility.deselect_all(global_manager)
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
        #actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), 'none')
                    
        #if abs(global_manager.get('mouse_origin_x') - mouse_x) < 5 and abs(global_manager.get('mouse_origin_y') - mouse_y) < 5: #if clicked rather than mouse box drawn, only select top mob of cell
        for current_grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in current_grid.modes:
                for current_cell in current_grid.cell_list:
                    if current_cell.touching_mouse():
                        if len(current_cell.contained_mobs) > 0:
                            selected_new_mob = True
                            current_cell.contained_mobs[0].select()
                            if current_grid == global_manager.get('minimap_grid'):
                                main_x, main_y = global_manager.get('minimap_grid').get_main_grid_coordinates(current_cell.x, current_cell.y) #main_x, main_y = global_manager.get('strategic_map_grid').get_main_grid_coordinates(current_cell.x, current_cell.y)
                                main_cell = global_manager.get('strategic_map_grid').find_cell(main_x, main_y)
                                if not main_cell == 'none':
                                    main_tile = main_cell.tile
                                    if not main_tile == 'none':
                                        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), main_tile)
                            else: #elif current_grid == global_manager.get('strategic_map_grid'):
                                actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_cell.tile)
        if selected_new_mob:
            selected_list = actor_utility.get_selected_list(global_manager)
            if len(selected_list) == 1 and selected_list[0].grids[0] == global_manager.get('minimap_grid').attached_grid: #do not calibrate minimap if selecting someone outside of attached grid
                global_manager.get('minimap_grid').calibrate(selected_list[0].x, selected_list[0].y)
                
        else:
            click_move_minimap(global_manager)
    elif (not clicked_button) and global_manager.get('choosing_destination'): #if clicking to move somewhere
        chooser = global_manager.get('choosing_destination_info_dict')['chooser']
        #destination_grids = global_manager.get('choosing_destination_info_dict')['destination_grids']
        chose_destination = False
        for current_grid in global_manager.get('grid_list'): #destination_grids:
            for current_cell in current_grid.cell_list:
                if current_cell.touching_mouse():
                    click_move_minimap(global_manager)
                    target_cell = 'none'
                    if current_cell.grid.is_abstract_grid:
                        target_cell = current_cell
                    else:
                        target_cell = global_manager.get('strategic_map_grid').find_cell(global_manager.get('minimap_grid').center_x, global_manager.get('minimap_grid').center_y) #center
                    if not current_grid in chooser.grids:
                        stopping = False
                        if not current_grid.is_abstract_grid: #if grid has more than 1 cell, check if correct part of grid
                            destination_x, destination_y = target_cell.tile.get_main_grid_coordinates()
                            if (not (destination_y == 0 or (destination_y == 1 and target_cell.has_port()))) and destination_x >= 0 and destination_x < global_manager.get('strategic_map_grid').coordinate_width: #or is harbor
                                text_tools.print_to_screen("You can only send ships to coastal waters and coastal ports.", global_manager)
                                stopping = True
                        chose_destination = True
                        if not stopping:
                            chooser.end_turn_destination = target_cell.tile
                            global_manager.set('show_selection_outlines', True)
                            global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when destination chosen
                    else: #can not move to same continent
                        text_tools.print_to_screen("You can only send ships to other theatres.", global_manager)
        global_manager.set('choosing_destination', False)
        global_manager.set('choosing_destination_info_dict', {})
    elif not clicked_button:
        click_move_minimap(global_manager)

def click_move_minimap(global_manager): #move minimap to clicked tile
    mouse_x, mouse_y = pygame.mouse.get_pos()
    breaking = False
    for current_grid in global_manager.get('grid_list'): #if grid clicked, move minimap to location clicked
        if current_grid.can_show():
            for current_cell in current_grid.cell_list:
                if current_cell.touching_mouse():
                    if current_grid == global_manager.get('minimap_grid'): #if minimap clicked, calibrate to corresponding place on main map
                        if not current_cell.terrain == 'none': #if off map, do not move minimap there
                            main_x, main_y = current_grid.get_main_grid_coordinates(current_cell.x, current_cell.y)
                            global_manager.get('minimap_grid').calibrate(main_x, main_y)
                    elif current_grid == global_manager.get('strategic_map_grid'):
                        global_manager.get('minimap_grid').calibrate(current_cell.x, current_cell.y)
                    else: #if abstract grid, show the inventory of the tile clicked without calibrating minimap
                        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), current_grid.cell_list[0].tile)
                    breaking = True
                    break
                if breaking:
                    break
            if breaking:
                 break
