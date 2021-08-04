import pygame
import time

import modules.scaling as scaling
import modules.main_loop as main_loop
import modules.notification_tools as notification_tools
import modules.images as images
import modules.buttons as buttons
import modules.game_transitions as game_transitions
import modules.grids as grids
import modules.data_managers as data_managers
import modules.actor_utility as actor_utility
import modules.groups as groups
import modules.europe_transactions as europe_transactions
import modules.labels as labels
import modules.actor_match_tools as actor_match_tools
import modules.instructions as instructions

pygame.init()

global_manager = data_managers.global_manager_template()#manager of a dictionary of what would be global variables passed between functions and classes
global_manager.set('europe_grid', 'none')
resolution_finder = pygame.display.Info()
global_manager.set('default_display_width', 1728)#all parts of game made to be at default and scaled to display
global_manager.set('default_display_height', 972)
global_manager.set('display_width', resolution_finder.current_w - round(global_manager.get('default_display_width')/10))
global_manager.set('display_height', resolution_finder.current_h - round(global_manager.get('default_display_height')/10))
global_manager.set('loading', True)
global_manager.set('loading_start_time', time.time())

#default
#global_manager.set('myfont', pygame.font.SysFont('Times New Roman', scaling.scale_width(15, global_manager)))

global_manager.set('myfont', pygame.font.SysFont('Times New Roman', scaling.scale_width(15, global_manager)))

global_manager.set('font_size', scaling.scale_width(15, global_manager))
global_manager.set('game_display', pygame.display.set_mode((global_manager.get('display_width'), global_manager.get('display_height'))))

pygame.display.set_caption('SFA')
global_manager.set('color_dict',
    {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'light gray': (230, 230, 230),
    'gray': (190, 190, 190),
    'dark gray': (150, 150, 150),
    'bright red': (255, 0, 0),
    'red': (200, 0, 0),
    'dark red': (150, 0, 0),
    'bright green': (0, 255, 0),
    'green': (0, 200, 0),
    'dark green': (0, 150, 0),
    'green': (0, 200, 0),
    'dark green': (0, 150, 0),
    'bright blue': (0, 0, 255),
    'blue': (0, 0, 200),
    'dark blue': (0, 0, 150),
    'yellow': (255, 255, 0),
    'brown': (132, 94, 59)
    }
)

terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
global_manager.set('terrain_list', terrain_list)

global_manager.set('terrain_colors',
    {
    'clear': (150, 200, 104),
    'hills': (50, 205, 50),
    'jungle': (0, 100, 0),
    'water': (0, 0, 200),
    'mountain': (100, 100, 100),
    'swamp': (100, 100, 50),
    'desert': (255, 248, 104),
    'none': (0, 0, 0)
    }
)

global_manager.set('commodity_types', ['coffee', 'copper', 'diamonds', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'])
global_manager.set('resource_types', global_manager.get('commodity_types') + ['natives'])

global_manager.get('game_display').fill(global_manager.get('color_dict')['white'])
global_manager.set('button_list', [])
global_manager.set('current_instructions_page', 'none')
global_manager.set('current_dice_rolling_notification', 'none')
global_manager.set('current_instructions_page_index', 0)
global_manager.set('instructions_list', [])
#page 1
instructions_message = "Placeholder instructions, use += to add"
global_manager.get('instructions_list').append(instructions_message)

global_manager.set('grid_list', [])
global_manager.set('abstract_grid_list', [])
global_manager.set('text_list', [])
global_manager.set('image_list', [])
global_manager.set('background_image_list', [])
global_manager.set('bar_list', [])
global_manager.set('actor_list', [])
global_manager.set('mob_list', [])
global_manager.set('officer_list', [])
global_manager.set('worker_list', [])
global_manager.set('group_list', [])
global_manager.set('tile_list', [])
global_manager.set('overlay_tile_list', [])
global_manager.set('notification_list', [])
global_manager.set('label_list', [])
global_manager.set('mob_info_display_list', [])
global_manager.set('displayed_mob', 'none')
global_manager.set('tile_info_display_list', [])
global_manager.set('displayed_tile', 'none')
global_manager.set('dice_list', [])
#global_manager.set('notification_queue', [])
#global_manager.set('notification_type_queue', [])
pygame.key.set_repeat(300, 200)
global_manager.set('crashed', False)
global_manager.set('lmb_down', False)
global_manager.set('rmb_down', False)
global_manager.set('mmb_down', False)
global_manager.set('typing', False)
global_manager.set('message', '')
global_manager.set('show_grid_lines', True)
global_manager.set('show_text_box', True)
global_manager.set('show_selection_outlines', True)
global_manager.set('show_minimap_outlines', True)
global_manager.set('mouse_origin_x', 0)
global_manager.set('mouse_origin_y', 0)
global_manager.set('mouse_destination_x', 0)
mouse_destination_y = 0
global_manager.set('mouse_destination_y', 0)
global_manager.set('making_mouse_box', False)
global_manager.set('making_choice', False)

global_manager.set('ongoing_exploration', False)

global_manager.set('r_shift', 'up')
global_manager.set('l_shift', 'up')
global_manager.set('capital', False)
global_manager.set('r_ctrl', 'up')
global_manager.set('l_ctrl', 'up')
global_manager.set('ctrl', 'up')
global_manager.set('start_time', time.time())
global_manager.set('current_time', time.time())
global_manager.set('last_selection_outline_switch', time.time())
#global_manager.set('last_minimap_outline_switch', time.time())
mouse_moved_time = time.time()
global_manager.set('mouse_moved_time', time.time())
old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
global_manager.set('old_mouse_x', old_mouse_x)
global_manager.set('old_mouse_y', old_mouse_y)
global_manager.set('flavor_text_manager', data_managers.flavor_text_manager_template(global_manager))
global_manager.set('notification_manager', data_managers.notification_manager_template(global_manager))
notification_tools.show_tutorial_notifications(global_manager)
global_manager.set('loading_image', images.loading_image_template('misc/loading.png', global_manager))
global_manager.set('current_game_mode', 'none')
global_manager.set('input_manager', data_managers.input_manager_template(global_manager))

strategic_background_image = images.free_image('misc/background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['strategic', 'europe'], global_manager)
#europe_background_image = images.free_image('misc/europe_background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['europe'], global_manager)
global_manager.get('background_image_list').append(strategic_background_image)
#global_manager.get('background_image_list').append(europe_background_image)
#strategic_map_grid = grids.grid(scaling.scale_coordinates(729, 150, global_manager), scaling.scale_width(870, global_manager), scaling.scale_height(810, global_manager), 64, 60, True, color_dict['dark green'], ['strategic']) #other map sizes
#strategic_map_grid = grids.grid(scaling.scale_coordinates(729, 150, global_manager), scaling.scale_width(870, global_manager), scaling.scale_height(810, global_manager), 32, 30, True, color_dict['dark green'], ['strategic'])
#strategic_map_grid = grids.grid(scaling.scale_coordinates(695, 150, global_manager), scaling.scale_width(864, global_manager), scaling.scale_height(810, global_manager), 16, 15, color_dict['dark green'], ['strategic'], global_manager) #54 by 54
#default
#strategic_map_grid = grids.grid(scaling.scale_coordinates(global_manager.get('display_width') - (grid_width + 100), global_manager.get('display_height') - (grid_height + 25), global_manager), scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 16, 15, color_dict['dark green'], ['strategic'], True, global_manager)
grid_height = 450
grid_width = 480

strategic_map_grid = grids.grid(scaling.scale_coordinates(global_manager.get('default_display_width') - (grid_width + 100), global_manager.get('default_display_height') - (grid_height + 25), global_manager),
                    scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 16, 15, 'black', 'black', ['strategic'], True, 2, global_manager)
global_manager.set('strategic_map_grid', strategic_map_grid)

minimap_grid = grids.mini_grid(scaling.scale_coordinates(global_manager.get('default_display_width') - (grid_width + 100), global_manager.get('default_display_height') - (2 * (grid_height + 25)), global_manager),
                    scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 5, 5, 'black', 'bright red', ['strategic'], global_manager.get('strategic_map_grid'), 3, global_manager) #60 by 60
global_manager.set('minimap_grid', minimap_grid)

europe_grid_x = global_manager.get('default_display_width') - (grid_width + 340)
europe_grid_y = global_manager.get('default_display_height') - (grid_height + 25)
europe_grid = grids.abstract_grid(scaling.scale_coordinates(europe_grid_x, europe_grid_y, global_manager), scaling.scale_width(round(grid_width / 4), global_manager), scaling.scale_height(round(grid_width / 4), global_manager), 'black',
                                  'black', ['strategic', 'europe'], 3, 'locations/europe.png', 'Europe', global_manager)

global_manager.set('europe_grid', europe_grid)

game_transitions.set_game_mode('strategic', global_manager)
game_transitions.create_strategic_map(global_manager)

global_manager.set('money_tracker', data_managers.value_tracker('money', 100, global_manager))
labels.value_label(scaling.scale_coordinates(275, global_manager.get('default_display_height') - 30, global_manager), scaling.scale_width(100, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe'],
                   'misc/default_label.png', 'money', global_manager)
                

europe_transactions.european_hq_button(scaling.scale_coordinates(europe_grid_x - 85, europe_grid_y, global_manager), scaling.scale_width(round(grid_width / 8), global_manager), scaling.scale_height(round(grid_width / 8),
                                       global_manager), 'blue', 'none', True, ['strategic'], 'misc/european_hq_button.png', global_manager)

europe_transactions.european_hq_button(scaling.scale_coordinates(150, global_manager.get('default_display_height') - 100, global_manager), scaling.scale_width(100, global_manager), scaling.scale_height(100, global_manager), 'blue',
                                       pygame.K_ESCAPE, False, ['europe'], 'misc/exit_european_hq_button.png', global_manager)

button_start_x = 500#600#x position of leftmost button
button_separation = 60#x separation between each button
current_button_number = 0#tracks current button to move each one farther right

left_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
                                   'move left', pygame.K_a, ['strategic'], 'misc/left_button.png', global_manager)
current_button_number += 1

down_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
                                   'move down', pygame.K_s, ['strategic'], 'misc/down_button.png', global_manager)#movement buttons should be usable in any mode with a grid


up_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 80, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
                                 'move up', pygame.K_w, ['strategic'], 'misc/up_button.png', global_manager)
current_button_number += 1

right_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
                                    'move right', pygame.K_d, ['strategic'], 'misc/right_button.png', global_manager)
current_button_number += 2#move more when switching categories

to_africa_button = buttons.switch_grid_button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager),
                                              scaling.scale_height(50, global_manager), 'blue', 'to africa', pygame.K_1, ['strategic'], 'locations/africa_button.png', global_manager.get('strategic_map_grid'), global_manager)

current_button_number += 1

to_europe_button = buttons.switch_grid_button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager),
                                              scaling.scale_height(50, global_manager), 'blue', 'to europe', pygame.K_2, ['strategic'], 'locations/europe_button.png', global_manager.get('europe_grid'), global_manager)

current_button_number += 1

expand_text_box_button = buttons.button(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'black',
                                        'expand text box', pygame.K_j, ['strategic', 'europe'], 'misc/text_box_size_button.png', global_manager) #'none' for no keybind

#toggle_grid_lines_button = button.button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 170, global_manager), scaling.scale_width(50, global_manager),
#scaling.scale_height(50, global_manager), 'blue', 'toggle grid lines', pygame.K_g, ['strategic'], 'misc/grid_line_button.png', global_manager)

instructions_button = instructions.instructions_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager),
                                     scaling.scale_height(50, global_manager), 'blue', 'instructions', pygame.K_i, ['strategic', 'europe'], 'misc/instructions.png', global_manager)

toggle_text_box_button = buttons.button(scaling.scale_coordinates(75, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
                                        'toggle text box', pygame.K_t, ['strategic', 'europe'], 'misc/toggle_text_box_button.png', global_manager)

merge_button = groups.merge_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 220, global_manager), scaling.scale_width(50, global_manager),
                                   scaling.scale_height(50, global_manager), 'blue', pygame.K_m, ['strategic', 'europe'], 'misc/merge_button.png', global_manager)

split_button = groups.split_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 220, global_manager), scaling.scale_width(50, global_manager),
                                   scaling.scale_height(50, global_manager), 'blue', pygame.K_n, ['strategic', 'europe'], 'misc/split_button.png', global_manager)

#mob background image
mob_free_image_background = images.free_image('misc/mob_background.png', scaling.scale_coordinates(0, global_manager.get('default_display_height') - 245, global_manager), scaling.scale_width(125, global_manager),
                                              scaling.scale_height(125, global_manager), ['strategic', 'europe'], global_manager)

#mob image
mob_free_image = actor_match_tools.actor_match_free_image(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 245, global_manager), scaling.scale_width(125, global_manager),
                                                          scaling.scale_height(125, global_manager), ['strategic', 'europe'], 'default', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('mob_info_display_list').append(mob_free_image)

#mob name label
mob_name_label = actor_match_tools.actor_match_label(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 285, global_manager), scaling.scale_width(100, global_manager), scaling.scale_height(30, global_manager),
                                          ['strategic', 'europe'], 'misc/default_label.png', 'name', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager

global_manager.get('mob_info_display_list').append(mob_name_label)


#tile background image
tile_free_image_background = images.free_image('misc/mob_background.png', scaling.scale_coordinates(0, global_manager.get('default_display_height') - 560, global_manager), scaling.scale_width(125, global_manager),
                                               scaling.scale_height(125, global_manager), ['strategic'], global_manager)

#tile terrain image
tile_free_image = actor_match_tools.actor_match_free_image(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 560, global_manager), scaling.scale_width(125, global_manager),
                                                           scaling.scale_height(125, global_manager), ['strategic'], 'terrain', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_image)

#tile resource image
tile_free_resource_image = actor_match_tools.actor_match_free_image(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 560, global_manager), scaling.scale_width(125, global_manager),
                                                         scaling.scale_height(125, global_manager), ['strategic'], 'resource', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_resource_image)

#tile terrain label
tile_terrain_label = actor_match_tools.actor_match_label(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 600, global_manager), scaling.scale_width(100, global_manager),
                    scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', 'terrain', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('tile_info_display_list').append(tile_terrain_label)

#tile resource label
tile_resource_label = actor_match_tools.actor_match_label(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 640, global_manager), scaling.scale_width(100, global_manager),
                                                          scaling.scale_height(30, global_manager),
                                               ['strategic'], 'misc/default_label.png', 'resource', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('tile_info_display_list').append(tile_resource_label)

for current_index in range(len(global_manager.get('commodity_types'))):
    new_commodity_match_label = actor_match_tools.commodity_match_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - (150 + (35 * current_index)), global_manager),
            scaling.scale_width(50, global_manager), scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', current_index, 'mob', global_manager)
            #coordinates, ideal_width, minimum_height, modes, image_id, commodity_index, global_manager
    
    global_manager.get('mob_info_display_list').append(new_commodity_match_label)

for current_index in range(len(global_manager.get('commodity_types'))):
    new_commodity_match_label = actor_match_tools.commodity_match_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - (490 + (35 * current_index)), global_manager),
            scaling.scale_width(50, global_manager), scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', current_index, 'tile', global_manager)
            #coordinates, ideal_width, minimum_height, modes, image_id, commodity_index, global_manager
    
    global_manager.get('tile_info_display_list').append(new_commodity_match_label)

for i in range(0, 5):
    selected_icon = buttons.selected_icon(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - (280 + 60 * i), global_manager),
                                          scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'gray', ['strategic', 'europe'], 'misc/default_button.png', i, global_manager)
    
recruitment_types = ['explorer', 'European worker']
for recruitment_index in range(len(recruitment_types)):
    new_recruitment_button = europe_transactions.recruitment_button(scaling.scale_coordinates(1500, 500 + (120 * recruitment_index), global_manager), scaling.scale_width(100, global_manager), scaling.scale_height(100, global_manager),
                                                                    'blue', recruitment_types[recruitment_index], 'none', ['europe'], global_manager)

global_manager.get('minimap_grid').calibrate(2, 2)
actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), 'none') #tile info display should start empty

main_loop.main_loop(global_manager)
pygame.quit()
