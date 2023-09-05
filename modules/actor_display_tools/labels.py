#Contains functionality for actor display labels

import pygame

from ..labels import label
from ..images import minister_type_image
from .. import utility
from .. import scaling
from . import images

class actor_display_label(label):
    '''
    Label that changes its text to match the information of selected mobs or tiles
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_label_type': string value - Type of actor information shown
                'actor_type': string value - Type of actor to display the information of, like 'mob', 'tile', or 'minister'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_buttons = []
        self.has_label_collection = False
        self.actor = 'none'
        self.actor_label_type = input_dict['actor_label_type'] #name, terrain, resource, etc
        self.actor_type = input_dict['actor_type'] #mob or tile, none if does not scale with shown labels, like tooltip labels
        self.image_y_displacement = 0
        input_dict['message'] = ''
        super().__init__(input_dict, global_manager)
        #all labels in a certain ordered label list will be placed in order on the side of the screen when the correct type of actor/minister is selected
        s_increment = scaling.scale_width(6, self.global_manager)
        m_increment = scaling.scale_width(11, self.global_manager)
        l_increment = scaling.scale_width(30, self.global_manager)

        s_size = self.height + s_increment
        m_size = self.height + m_increment
        l_size = self.height + l_increment
        input_dict = {
            'coordinates': (self.x, self.y),
            'width': s_size,
            'height': s_size,
            'modes': self.modes,
            'attached_label': self
        }
        if self.actor_label_type == 'name':
            self.message_start = 'Name: '
            input_dict['init_type'] = 'merge button'
            input_dict['image_id'] = 'buttons/merge_button.png'
            #input_dict['keybind_id'] = pygame.K_m
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'split button'
            input_dict['image_id'] = 'buttons/split_button.png'
            #input_dict['keybind_id'] = pygame.K_n
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'labor broker button'
            input_dict['image_id'] = 'buttons/labor_broker_button.png'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'embark vehicle button'
            input_dict['image_id'] = 'buttons/embark_ship_button.png'
            input_dict['keybind_id'] = pygame.K_b
            input_dict['vehicle_type'] = 'ship'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'embark vehicle button'
            input_dict['image_id'] = 'buttons/embark_train_button.png'
            input_dict['keybind_id'] = pygame.K_b
            input_dict['vehicle_type'] = 'train'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'worker crew vehicle button'
            input_dict['image_id'] = 'buttons/crew_ship_button.png'
            #input_dict['keybind_id'] = pygame.K_m
            input_dict['vehicle_type'] = 'ship'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'worker crew vehicle button'
            input_dict['image_id'] = 'buttons/crew_train_button.png'
            #input_dict['keybind_id'] = pygame.K_m
            input_dict['vehicle_type'] = 'train'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'work crew to building button'
            input_dict['image_id'] = 'buttons/work_crew_to_building_button.png'
            input_dict['keybind_id'] = pygame.K_g
            input_dict['building_type'] = 'resource'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'switch theatre button'
            input_dict['image_id'] = 'buttons/switch_theatre_button.png'
            input_dict['keybind_id'] = pygame.K_g
            input_dict['width'], input_dict['height'] = (m_size, m_size)
            self.add_attached_button(input_dict)

            del input_dict['image_id']
            input_dict['init_type'] = 'construction button'
            input_dict['building_type'] = 'resource'
            input_dict['keybind_id'] = pygame.K_g
            input_dict['width'], input_dict['height'] = (s_size, s_size)
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'port'
            input_dict['keybind_id'] = pygame.K_p
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'infrastructure'
            input_dict['keybind_id'] = pygame.K_r
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'train_station'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'trading_post'
            input_dict['keybind_id'] = pygame.K_y
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'mission'
            input_dict['keybind_id'] = pygame.K_y
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'fort'
            input_dict['keybind_id'] = pygame.K_v
            self.add_attached_button(input_dict)
            
            input_dict['init_type'] = 'repair button'
            input_dict['building_type'] = 'resource'
            input_dict['keybind_id'] = pygame.K_g
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'port'
            input_dict['keybind_id'] = pygame.K_p
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'train_station'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['building_type'] = 'trading_post'
            input_dict['keybind_id'] = pygame.K_y
            self.add_attached_button(input_dict)
            
            input_dict['building_type'] = 'mission'
            input_dict['keybind_id'] = pygame.K_y
            self.add_attached_button(input_dict)
            
            input_dict['building_type'] = 'fort'
            input_dict['keybind_id'] = pygame.K_v
            self.add_attached_button(input_dict)
            del input_dict['building_type']
            del input_dict['keybind_id']
            
            input_dict['init_type'] = 'upgrade button'
            input_dict['base_building_type'] = 'resource'
            input_dict['upgrade_type'] = 'scale'
            self.add_attached_button(input_dict)

            input_dict['upgrade_type'] = 'efficiency'
            self.add_attached_button(input_dict)

            input_dict['base_building_type'] = 'warehouses'
            input_dict['upgrade_type'] = 'warehouse_level'
            input_dict['keybind_id'] = pygame.K_k
            self.add_attached_button(input_dict)
            del input_dict['base_building_type']
            del input_dict['upgrade_type']
            
            input_dict['init_type'] = 'build train button'
            input_dict['image_id'] = 'mobs/train/button.png'
            input_dict['keybind_id'] = pygame.K_y
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'build steamboat button'
            input_dict['image_id'] = 'mobs/steamboat/button.png'
            input_dict['keybind_id'] = pygame.K_u
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'trade button'
            input_dict['image_id'] = 'buttons/trade_button.png'
            input_dict['keybind_id'] = pygame.K_r
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'convert button'
            input_dict['image_id'] = 'buttons/convert_button.png'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'rumor search button'
            input_dict['image_id'] = 'buttons/rumor_search_button.png'
            input_dict['keybind_id'] = pygame.K_r
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'artifact search button'
            input_dict['image_id'] = 'buttons/artifact_search_button.png'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'evangelist campaign button'
            input_dict['image_id'] = 'buttons/public_relations_campaign_button.png'
            input_dict['campaign_type'] = 'public relations campaign'
            input_dict['keybind_id'] = pygame.K_r
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'evangelist campaign button'
            input_dict['image_id'] = 'buttons/religious_campaign_button.png'
            input_dict['campaign_type'] = 'religious campaign'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'advertising campaign button'
            input_dict['image_id'] = 'ministers/icons/trade.png'
            input_dict['keybind_id'] = pygame.K_r
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'take loan button'
            input_dict['image_id'] = 'buttons/take_loan_button.png'
            input_dict['keybind_id'] = pygame.K_l
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'track beasts button'
            input_dict['image_id'] = 'buttons/track_beasts_button.png'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'capture slaves button'
            input_dict['image_id'] = 'buttons/capture_slaves_button.png'
            input_dict['keybind_id'] = pygame.K_t
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'suppress slave trade button'
            input_dict['image_id'] = 'buttons/suppress_slave_trade_button.png'
            input_dict['keybind_id'] = pygame.K_r
            self.add_attached_button(input_dict)
            
        elif self.actor_label_type == 'movement':
            self.message_start = 'Movement points: '
            
            input_dict['init_type'] = 'enable automatic replacement button'
            input_dict['target_type'] = 'unit'
            input_dict['image_id'] = 'buttons/enable_automatic_replacement_officer_button.png'
            self.add_attached_button(input_dict)
            
            input_dict['init_type'] = 'disable automatic replacement button'
            input_dict['image_id'] = 'buttons/disable_automatic_replacement_officer_button.png'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'enable automatic replacement button'
            input_dict['image_id'] = 'buttons/enable_automatic_replacement_worker_button.png'
            input_dict['target_type'] = 'worker'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'disable automatic replacement button'
            input_dict['image_id'] = 'buttons/disable_automatic_replacement_worker_button.png'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'enable automatic replacement button'
            input_dict['image_id'] = 'buttons/enable_automatic_replacement_officer_button.png'
            input_dict['target_type'] = 'officer'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'disable automatic replacement button'
            input_dict['image_id'] = 'buttons/disable_automatic_replacement_officer_button.png'
            self.add_attached_button(input_dict)
            
            del input_dict['target_type']
            
            input_dict['init_type'] = 'enable sentry mode button'
            input_dict['image_id'] = 'buttons/enable_sentry_mode_button.png'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'disable sentry mode button'
            input_dict['image_id'] = 'buttons/disable_sentry_mode_button.png'
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'end unit turn button'
            input_dict['image_id'] = 'buttons/end_unit_turn_button.png'
            input_dict['keybind_id'] = pygame.K_f
            self.add_attached_button(input_dict)
            del input_dict['keybind_id']

            input_dict['init_type'] = 'automatic route button'
            input_dict['image_id'] = 'buttons/clear_automatic_route_button.png'
            input_dict['button_type'] = 'clear automatic route'
            self.add_attached_button(input_dict)

            input_dict['image_id'] = 'buttons/draw_automatic_route_button.png'
            input_dict['button_type'] = 'draw automatic route'
            self.add_attached_button(input_dict)

            input_dict['image_id'] = 'buttons/follow_automatic_route_button.png'
            input_dict['button_type'] = 'follow automatic route'
            self.add_attached_button(input_dict)
            
        elif self.actor_label_type == 'building work crews':
            self.message_start = 'Work crews: '
            input_dict['init_type'] = 'cycle work crews button'
            input_dict['image_id'] = 'buttons/cycle_passengers_down_button.png'
            self.add_attached_button(input_dict)

        elif self.actor_label_type == 'current building work crew':
            self.message_start = ''
            self.attached_building = 'none'
            input_dict['init_type'] = 'remove work crew button'
            input_dict['image_id'] = 'buttons/remove_work_crew_button.png'
            input_dict['building_type'] = 'resource'
            self.add_attached_button(input_dict)

        elif self.actor_label_type == 'crew':
            self.message_start = 'Crew: '
            input_dict['init_type'] = 'crew vehicle button'
            input_dict['image_id'] = 'buttons/crew_ship_button.png'
            #input_dict['keybind_id'] = pygame.K_m
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'uncrew vehicle button'
            input_dict['image_id'] = 'buttons/uncrew_ship_button.png'
            #input_dict['keybind_id'] = pygame.K_n
            self.add_attached_button(input_dict)

        elif self.actor_label_type == 'passengers':
            self.message_start = 'Passengers: '
            input_dict['init_type'] = 'cycle passengers button'
            input_dict['image_id'] = 'buttons/cycle_passengers_down_button.png'
            input_dict['keybind_id'] = pygame.K_4
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'embark all passengers button'
            input_dict['image_id'] = 'buttons/embark_ship_button.png'
            input_dict['keybind_id'] = pygame.K_z
            self.add_attached_button(input_dict)

            input_dict['init_type'] = 'disembark all passengers button'
            input_dict['image_id'] = 'buttons/disembark_ship_button.png'
            input_dict['keybind_id'] = pygame.K_x
            self.add_attached_button(input_dict)

        elif self.actor_label_type == 'current passenger':
            self.message_start = ''
            input_dict['keybind_id'] = 'none'
            if self.list_index == 0:
                input_dict['keybind_id'] = pygame.K_1
            elif self.list_index == 1:
                input_dict['keybind_id'] = pygame.K_2
            elif self.list_index == 2:
                input_dict['keybind_id'] = pygame.K_3
            input_dict['init_type'] = 'disembark vehicle button'
            input_dict['image_id'] = 'buttons/disembark_ship_button.png'
            self.add_attached_button(input_dict)

        elif self.actor_label_type == 'tooltip':
            self.message_start = ''

        elif self.actor_label_type == 'native aggressiveness':
            self.message_start = 'Aggressiveness: '

        elif self.actor_label_type == 'native population':
            self.message_start = 'Total population: '

        elif self.actor_label_type == 'native available workers':
            self.message_start = 'Available workers: '
            african_workers_image_id_list = ['mobs/default/button.png']
            left_worker_dict = {
                'image_id': 'mobs/African workers/default.png',
                'size': 0.8,
                'x_offset': -0.2,
                'y_offset': 0,
                'level': 1
            }
            african_workers_image_id_list.append(left_worker_dict)

            right_worker_dict = left_worker_dict.copy()
            right_worker_dict['x_offset'] *= -1
            african_workers_image_id_list.append(right_worker_dict)
            input_dict['init_type'] = 'hire african workers button'
            input_dict['image_id'] = african_workers_image_id_list
            input_dict['hire_source_type'] = 'village'
            input_dict['width'], input_dict['height'] = (l_size, l_size)
            self.add_attached_button(input_dict)

        elif self.actor_label_type in ['mob inventory capacity', 'tile inventory capacity']:
            self.message_start = 'Inventory: '

        elif self.actor_label_type == 'terrain':
            self.message_start = 'Terrain: '
            buy_slaves_image_id_list = ['mobs/default/button.png']
            left_worker_dict = {
                'image_id': 'mobs/slave workers/default.png',
                'size': 0.8,
                'x_offset': -0.2,
                'y_offset': 0,
                'level': 1
            }
            buy_slaves_image_id_list.append(left_worker_dict)

            right_worker_dict = left_worker_dict.copy()
            right_worker_dict['x_offset'] *= -1
            buy_slaves_image_id_list.append(right_worker_dict)
            input_dict['init_type'] = 'buy slaves button'
            input_dict['image_id'] = buy_slaves_image_id_list
            input_dict['width'], input_dict['height'] = (l_size, l_size)
            self.add_attached_button(input_dict)

        elif self.actor_label_type == 'minister':
            self.message_start = 'Minister: '
            input_dict['width'], input_dict['height'] = (m_size, m_size)
            attached_minister_type_image = minister_type_image((self.x - self.height - m_increment, self.y), self.height + m_increment, self.height + m_increment, self.modes, 'none', self, global_manager)
            self.insert_collection_above().add_member(attached_minister_type_image, {'x_offset': -1 * attached_minister_type_image.height, 'y_offset': -0.5 * m_increment}) #offsets are being ignored
            self.parent_collection.can_show_override = self #parent collection is considered showing when this label can show, allowing ordered collection to work correctly
            self.image_y_displacement = 5

        elif self.actor_label_type in ['minister_name', 'country_name']:
            self.message_start = 'Name: '
            if self.actor_label_type == 'minister_name':
                input_dict['init_type'] = 'active investigation button'
                self.add_attached_button(input_dict)
        
        elif self.actor_label_type == 'country_effect':
            self.message_start = 'Effect: '

        elif self.actor_label_type == 'minister_office':
            self.message_start = 'Office: '
            input_dict['init_type'] = 'remove minister button'
            self.add_attached_button(input_dict)
            input_dict['init_type'] = 'appoint minister button'
            for current_position in global_manager.get('minister_types'):
                input_dict['appoint_type'] = current_position
                self.add_attached_button(input_dict)

        elif self.actor_label_type == 'evidence':
            self.message_start = 'Evidence: '
            if 'ministers' in self.modes:
                input_dict['init_type'] = 'to trial button'
                input_dict['width'], input_dict['height'] = (m_size, m_size)
                self.add_attached_button(input_dict)
            if 'trial' in self.modes:
                input_dict['init_type'] = 'fabricate evidence button'
                input_dict['width'], input_dict['height'] = (m_size, m_size)
                self.add_attached_button(input_dict)
                
                input_dict['init_type'] = 'bribe judge button'
                self.add_attached_button(input_dict)

        elif self.actor_label_type == 'slums':
            self.message_start = 'Slums population: '
            african_workers_image_id_list = ['mobs/default/button.png']
            left_worker_dict = {
                'image_id': 'mobs/African workers/default.png',
                'size': 0.8,
                'x_offset': -0.2,
                'y_offset': 0,
                'level': 1
            }
            african_workers_image_id_list.append(left_worker_dict)

            right_worker_dict = left_worker_dict.copy()
            right_worker_dict['x_offset'] *= -1
            african_workers_image_id_list.append(right_worker_dict)
            input_dict['init_type'] = 'hire african workers button'
            input_dict['image_id'] = african_workers_image_id_list
            input_dict['width'], input_dict['height'] = (l_size, l_size)
            input_dict['hire_source_type'] = 'slums'
            self.add_attached_button(input_dict)

        elif self.actor_label_type == 'combat_strength':
            self.message_start = 'Combat strength: '

        elif self.actor_label_type == 'preferred_terrains':
            self.message_start = 'Preferred terrain: '

        elif self.actor_label_type == 'building workers':
            self.message_start = 'Work crews: '

        else:
            self.message_start = utility.capitalize(self.actor_label_type) + ': ' #'worker' -> 'Worker: '
        self.calibrate('none')

    def add_attached_button(self, input_dict, member_config=None):
        '''
        Description:
            Adds a button created by the inputted input_dict to this label's interface collection, creating the collection if it does not already exist
        Input:
            dictionary input_dict: Input dict of button to create
            dictionary member_config=None: Optional member config of button to create
        Output:
            None
        '''
        if not self.has_label_collection:
            self.has_label_collection = True
            self.insert_collection_above(override_input_dict={
                'init_type': 'ordered collection',
                'direction': 'horizontal',
            })
            self.parent_collection.can_show_override = self #uses this label's can_show as the collection's can_show, so any members require this label to be showing
        if not member_config: #avoids issue with same default {} being used across multiple calls
            member_config = {}
        if not 'order_y_offset' in member_config:
            member_config['order_y_offset'] = abs(input_dict['height'] - self.height) / -2
        self.parent_collection.add_member(self.global_manager.get('actor_creation_manager').create_interface_element(input_dict, self.global_manager), member_config)

    def update_tooltip(self):
        '''
        Description:
            Sets this label's tooltip based on the label's type and the information of the actor it is attached to
        Input:
            None
        Output:
            None
        '''
        if self.actor_label_type in ['building work crew', 'current passenger']:
            if len(self.attached_list) > self.list_index:
                self.attached_list[self.list_index].update_tooltip()
                tooltip_text = self.attached_list[self.list_index].tooltip_text
                self.set_tooltip(tooltip_text)
            else:
                super().update_tooltip()
                
        elif self.actor_label_type == 'passengers':
            if (not self.actor == 'none'):
                if self.actor.has_crew:
                    name_list = [self.message_start]
                    for current_passenger in self.actor.contained_mobs:
                        name_list.append('    ' + utility.capitalize(current_passenger.name))
                    if len(name_list) == 1:
                        name_list[0] = self.message_start + ' none'
                    self.set_tooltip(name_list)
                else:
                    super().update_tooltip()
                    
        elif self.actor_label_type == 'crew':
            if (not self.actor == 'none') and self.actor.has_crew:
                self.actor.crew.update_tooltip()
                tooltip_text = self.actor.crew.tooltip_text
                self.set_tooltip(tooltip_text)
            else:
                super().update_tooltip()
                
        elif self.actor_label_type == 'tooltip':
            if not self.actor == 'none':
                self.actor.update_tooltip()
                tooltip_text = self.actor.tooltip_text
                if self.actor.actor_type == 'tile': #show tooltips of buildings in tile
                    for current_building in self.actor.cell.get_buildings():
                        current_building.update_tooltip()
                        tooltip_text.append('')
                        tooltip_text += current_building.tooltip_text  
                self.set_tooltip(tooltip_text)
                
        elif self.actor_label_type in ['native aggressiveness', 'native population', 'native available workers']:
            tooltip_text = [self.message]
            if self.actor_label_type == 'native aggressiveness':
                tooltip_text.append('Corresponds to the chance that the people of this village will attack nearby company units')
            elif self.actor_label_type == 'native population':
                tooltip_text.append('The total population of this village, which grows over time unless attacked or if willing villagers leave to become company workers')
            elif self.actor_label_type == 'native available workers':
                tooltip_text.append('The portion of this village\'s population that would be willing to work for your company')
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type in ['mob inventory capacity', 'tile inventory capacity']:
            tooltip_text = [self.message]
            if self.actor_label_type == 'mob inventory capacity':
                if not self.actor == 'none':
                    tooltip_text.append('This unit is currently holding ' + str(self.actor.get_inventory_used()) + ' commodities')
                    tooltip_text.append('This unit can hold a maximum of ' + str(self.actor.inventory_capacity) + ' commodities')
            elif self.actor_label_type == 'tile inventory capacity':
                if not self.actor == 'none':
                    if not self.actor.cell.visible:
                        tooltip_text.append('This tile has not been discovered')
                    elif self.actor.can_hold_infinite_commodities:
                        tooltip_text.append('This tile can hold infinite commodities.')
                    else:
                        tooltip_text.append('This tile currently contains ' + str(self.actor.get_inventory_used()) + ' commodities')
                        tooltip_text.append('This tile can retain a maximum of ' + str(self.actor.inventory_capacity) + ' commodities')
                        tooltip_text.append('If this tile is holding commodities exceeding its capacity before resource production at the end of the turn, extra commodities will be lost')
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'minister':
            tooltip_text = []
            if not self.actor == 'none':
                self.actor.update_tooltip()
                if not self.actor.controlling_minister == 'none':
                    tooltip_text = self.actor.controlling_minister.tooltip_text
                else:
                    tooltip_text = ['The ' + self.actor.controlling_minister_type + ' is responsible for controlling this unit',
                                    'As there is currently no ' + self.actor.controlling_minister_type + ', this unit will not be able to complete most actions until one is appointed']
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'evidence':
            tooltip_text = []
            if not self.actor == 'none':
                if self.global_manager.get('current_game_mode') == 'trial':
                    real_evidence = self.actor.corruption_evidence - self.actor.fabricated_evidence
                    tooltip_text.append('Your prosecutor has found ' + str(real_evidence) + ' piece' + utility.generate_plural(real_evidence) + ' of evidence of corruption against this minister.')
                    if self.actor.fabricated_evidence > 0:
                        tooltip_text.append('Additionally, your prosecutor has fabricated ' + str(self.actor.fabricated_evidence) + ' piece' + utility.generate_plural(self.actor.corruption_evidence) +
                            ' of fake evidence against this minister.')
                    tooltip_text.append('Each piece of evidence, real or fabricated, increases the chance of a trial\'s success. After a trial, all fabricated evidence and about half of the real evidence are rendered unusable')
                else:
                    tooltip_text.append('Your prosecutor has found ' + str(self.actor.corruption_evidence) + ' piece' + utility.generate_plural(self.actor.corruption_evidence) + ' of evidence of corruption against this minister')
                    tooltip_text.append('A corrupt minister may let goods go missing, steal the money given for a task and report a failure, or otherwise benefit themselves at the expense of your company')
                    tooltip_text.append('When a corrupt act is done, a skilled and loyal prosecutor may find evidence of the crime.')
                    tooltip_text.append('If you believe a minister is corrupt, evidence against them can be used in a criminal trial to justify appointing a new minister in their position')
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'background':
            tooltip_text = [self.message]
            tooltip_text.append('A minister\'s personal background determines their social status and may give them additional expertise in certain areas')
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'social status':
            tooltip_text = [self.message]
            tooltip_text.append('A minister\'s social status determines their power independent of your company.')
            tooltip_text.append('A minister of higher social status has a much greater ability to either help your company when your goals align, or fight back should they ever diverge')
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'interests':
            tooltip_text = [self.message]
            tooltip_text.append('While some interests are derived from a minister\'s legitimate talent or experience in a particular field, others are mere fancies')
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == 'ability':
            tooltip_text = [self.message]
            rank = 0
            if not self.actor == 'none':
                for skill_value in range(6, 0, -1): #iterates backwards from 6 to 1
                    for skill_type in self.actor.apparent_skills:
                        if self.actor.apparent_skills[skill_type] == skill_value:
                            rank += 1
                            skill_name = self.global_manager.get('minister_type_dict')[skill_type] #like General to military
                            tooltip_text.append('    ' + str(rank) + '. ' + skill_name.capitalize() + ': ' + self.actor.apparent_skill_descriptions[skill_type])
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == 'loyalty':
            tooltip_text = [self.message]
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'building workers':
            tooltip_text = []
            tooltip_text.append('Increase work crew capacity by upgrading the building\'s scale with a construction gang')
            if (not self.attached_building == 'none'):
                tooltip_text.append('Work crews: ' + str(len(self.attached_building.contained_work_crews)) + '/' + str(self.attached_building.scale))
                for current_work_crew in self.attached_building.contained_work_crews:
                    tooltip_text.append('    ' + utility.capitalize(current_work_crew.name))
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'building efficiency':
            tooltip_text = [self.message]
            tooltip_text.append('Each work crew attached to this building can produce up to the building efficiency in commodities each turn')
            tooltip_text.append('Increase work crew efficiency by upgrading the building\'s efficiency with a construction gang')
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'slums':
            tooltip_text = [self.message]
            tooltip_text.append('Villagers exposed to consumer goods through trade, fired workers, and freed slaves will wander and eventually move to slums in search of work')
            tooltip_text.append('Slums can form around ports, train stations, and resource production facilities')
            self.set_tooltip(tooltip_text)
            
        elif self.actor_label_type == 'combat_strength':
            tooltip_text = [self.message]
            tooltip_text.append('Combat strength is an estimation of a unit\'s likelihood to win combat based on its experience and unit type')
            tooltip_text.append('When attacked, the defending side will automatically choose its strongest unit to fight')
            if not self.actor == 'none':
                modifier = self.actor.get_combat_modifier()
                if modifier >= 0:
                    sign = '+'
                else:
                    sign = ''
                if self.actor.get_combat_strength() == 0:
                    tooltip_text.append('A unit with 0 combat strength will die automatically if forced to fight or if all other defenders are defeated')
                else:
                    if self.actor.veteran:
                        tooltip_text.append('In combat, this unit would roll 2 dice with a ' + sign + str(modifier) + ' modiifer, taking the higher of the 2 results')
                    else:
                        tooltip_text.append('In combat, this unit would roll 1 die with a ' + sign + str(modifier) + ' modiifer')
            self.set_tooltip(tooltip_text)

        elif self.actor_label_type == 'slave_traders_strength':
            tooltip_text = [self.message]
            tooltip_text.append('Any actions to combat the slave traders will be more difficult when strength is 20 or higher and easier when strength is 9 or lower')
            tooltip_text.append('The slave trade will be permanently eradicated once strength has been decreased to 0')
            tooltip_text.append('Strength will increase by 1 for each slave purchased')
            tooltip_text.append('Additionally, when decreased, strength will increase by 1 each turn until it returns to its original value of ' + str(self.global_manager.get('slave_traders_natural_max_strength')))
            self.set_tooltip(tooltip_text)

        else:
            super().update_tooltip()

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            if self.actor_label_type == 'name':
                self.set_label(self.message_start + utility.capitalize(new_actor.name))
                
            elif self.actor_label_type == 'coordinates':
                self.set_label(self.message_start + '(' + str(new_actor.x) + ', ' + str(new_actor.y) + ')')
                
            elif self.actor_label_type == 'terrain':
                if new_actor.grid.is_abstract_grid:
                    self.set_label(utility.capitalize(new_actor.grid.name))
                elif self.actor.cell.visible:
                    if new_actor.cell.terrain == 'water':
                        if new_actor.cell.y == 0:
                            self.set_label(self.message_start + 'ocean ' + str(new_actor.cell.terrain))
                        else:
                            self.set_label(self.message_start + 'river ' + str(new_actor.cell.terrain))
                    else:
                        self.set_label(self.message_start + str(new_actor.cell.terrain))
                else:
                    self.set_label(self.message_start + 'unknown')
                    
            elif self.actor_label_type == 'resource':
                if new_actor.grid.is_abstract_grid:
                    self.set_label(self.message_start + 'n/a')
                elif new_actor.cell.visible:
                    if not (new_actor.cell.has_building('resource') or new_actor.cell.has_building('village')): #if no building built, show resource: name
                        self.set_label(self.message_start + new_actor.cell.resource)
                else:
                    self.set_label(self.message_start + 'unknown')

            elif self.actor_label_type == 'resource building':
                if (not new_actor.grid.is_abstract_grid) and new_actor.cell.visible and new_actor.cell.has_building('resource'):
                    self.set_label('Resource building: ' + new_actor.cell.get_building('resource').name)

            elif self.actor_label_type == 'village':
                if new_actor.cell.visible and new_actor.cell.has_building('village') and new_actor.cell.visible:
                    self.set_label('Village name: ' + new_actor.cell.get_building('village').name)

            elif self.actor_label_type == 'movement':
                if self.actor.controllable:
                    if (new_actor.is_vehicle and new_actor.has_crew and (not new_actor.has_infinite_movement) and not new_actor.temp_movement_disabled) or not new_actor.is_vehicle: #if riverboat/train with crew or normal unit
                        self.set_label(self.message_start + str(new_actor.movement_points) + '/' + str(new_actor.max_movement_points))
                    else: #if ship or riverboat/train without crew
                        if not new_actor.has_infinite_movement:
                            if new_actor.movement_points == 0 or new_actor.temp_movement_disabled or not new_actor.has_crew:
                                self.set_label('No movement')
                        else:
                            if new_actor.movement_points == 0 or new_actor.temp_movement_disabled or not new_actor.has_crew:
                                self.set_label('No movement')
                            else:
                                self.set_label('Infinite movement')
                else:
                    self.set_label(self.message_start + '???')


            elif self.actor_label_type == 'attitude':
                if not self.actor.controllable:
                    if self.actor.hostile:
                        self.set_label(self.message_start + 'hostile')
                    else:
                        self.set_label(self.message_start + 'neutral')

            elif self.actor_label_type == 'combat_strength':
                self.set_label(self.message_start + str(self.actor.get_combat_strength()))

            elif self.actor_label_type == 'preferred_terrains':
                if self.actor.is_npmob and self.actor.npmob_type == 'beast':
                    self.set_label(self.message_start + ' ' + self.actor.preferred_terrains[0] + ', ' + self.actor.preferred_terrains[1] + ', ' + self.actor.preferred_terrains[2])

            elif self.actor_label_type == 'controllable':
                if not self.actor.controllable:
                    self.set_label('You do not control this unit')
                            
            elif self.actor_label_type == 'current building work crew': # or self.actor_label_type == 'building list item':
                if self.list_type == 'resource building':
                    if new_actor.cell.has_building('resource'):
                        self.attached_building = new_actor.cell.get_building('resource')
                        self.attached_list = self.attached_building.contained_work_crews
                        if len(self.attached_list) > self.list_index:
                            self.set_label(self.message_start + utility.capitalize(self.attached_list[self.list_index].name))
                    else:
                        self.attached_building = 'none'
                        self.attached_list = []
                        
            elif self.actor_label_type == 'crew':
                if self.actor.is_vehicle:
                    if self.actor.has_crew:
                        self.set_label(self.message_start + utility.capitalize(self.actor.crew.name))
                    else:
                        self.set_label(self.message_start + 'none')
                        
            elif self.actor_label_type == 'passengers':
                if self.actor.is_vehicle:
                    if not self.actor.has_crew:
                        if self.actor.can_swim and self.actor.can_swim_ocean:
                            self.set_label('Requires a European worker crew to function')
                        elif self.actor.vehicle_type == 'train':
                            self.set_label('Requires a non-slave worker crew to function')
                    else:
                        if len(self.actor.contained_mobs) == 0:
                            self.set_label(self.message_start + 'none')
                        else:
                            self.set_label(self.message_start)
                            
            elif self.actor_label_type == 'current passenger':
                if self.actor.is_vehicle:
                    if len(self.actor.contained_mobs) > 0:
                        self.attached_list = new_actor.contained_mobs
                        if len(self.attached_list) > self.list_index:
                            self.set_label(self.message_start + utility.capitalize(self.attached_list[self.list_index].name))

            elif self.actor_label_type in ['workers', 'officer']:
                if self.actor.is_group:
                    if self.actor_label_type == 'workers':
                        self.set_label(self.message_start + str(utility.capitalize(self.actor.worker.name)))
                    else:
                        self.set_label(self.message_start + str(utility.capitalize(self.actor.officer.name)))
            
            elif self.actor_label_type in ['native aggressiveness', 'native population', 'native available workers']:
                if self.actor.cell.has_building('village') and self.actor.cell.visible: #if village present
                    if self.actor_label_type == 'native aggressiveness':
                        self.set_label(self.message_start + str(self.actor.cell.get_building('village').aggressiveness))
                    elif self.actor_label_type == 'native population':
                        self.set_label(self.message_start + str(self.actor.cell.get_building('village').population))
                    elif self.actor_label_type == 'native available workers':
                        self.set_label(self.message_start + str(self.actor.cell.get_building('village').available_workers))

            elif self.actor_label_type in ['mob inventory capacity', 'tile inventory capacity']:
                if self.actor_label_type == 'tile inventory capacity' and not self.actor.cell.visible:
                    self.set_label(self.message_start + 'n/a')
                elif self.actor.can_hold_infinite_commodities:
                    self.set_label(self.message_start + 'unlimited')
                else:
                    self.set_label(self.message_start + str(self.actor.get_inventory_used()) + '/' + str(self.actor.inventory_capacity))
                    
            elif self.actor_label_type == 'minister':
                if self.actor.controllable:
                    if not self.actor.controlling_minister == 'none':
                        self.set_label(self.message_start + self.actor.controlling_minister.name)
                    
            elif self.actor_label_type == 'evidence':
                if new_actor.fabricated_evidence == 0:
                    self.set_label(self.message_start + str(new_actor.corruption_evidence))
                else:
                    self.set_label(self.message_start + str(new_actor.corruption_evidence) + ' (' + str(new_actor.fabricated_evidence) + ')')               

            elif self.actor_label_type == 'background':
                self.set_label(self.message_start + new_actor.background)
                
            elif self.actor_label_type == 'social status':
                self.set_label(self.message_start + new_actor.status)

            elif self.actor_label_type == 'interests':
                self.set_label(self.message_start + new_actor.interests[0] + ' and ' + new_actor.interests[1])

            elif self.actor_label_type == 'ability':
                message = ''
                if new_actor.current_position == 'none':
                    displayed_skill = new_actor.get_max_apparent_skill()
                    message += 'Highest ability: '
                else:
                    displayed_skill = new_actor.current_position
                    message += 'Current ability: '
                if displayed_skill != 'unknown':
                    displayed_skill_name = self.global_manager.get('minister_type_dict')[displayed_skill] #like General to military
                    message += new_actor.apparent_skill_descriptions[displayed_skill] + ' (' + displayed_skill_name + ')'
                else:
                    message += displayed_skill
                self.set_label(message)

            elif self.actor_label_type == 'loyalty':
                self.set_label(self.message_start + new_actor.apparent_corruption_description)
            
            elif self.actor_label_type in ['minister_name', 'country_name']:
                self.set_label(self.message_start + new_actor.name)

            elif self.actor_label_type == 'country_effect':
                self.set_label(self.message_start + new_actor.get_effect_descriptor())
                
            elif self.actor_label_type == 'minister_office':
                self.set_label(self.message_start + new_actor.current_position)
                
            elif self.actor_label_type == 'slums':
                if self.actor.cell.has_building('slums'):
                    self.set_label(self.message_start + str(self.actor.cell.get_building('slums').available_workers))
            elif self.actor_label_type == 'canoes':
                self.set_label('Equipped with canoes to move along rivers')
            
            elif self.actor_label_type == 'slave_traders_strength':
                self.set_label('Strength: ' + str(self.global_manager.get('slave_traders_strength')) + '/' + str(self.global_manager.get('slave_traders_natural_max_strength')))

        elif self.actor_label_type == 'tooltip':
            return #do not set text for tooltip label
        else:
            self.set_label(self.message_start + 'n/a')

    def can_show(self, ignore_parent_collection=False):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: False if no actor displayed or if various conditions are present depending on label type, otherwise returns same value as superclass
        '''
        result = super().can_show(ignore_parent_collection=ignore_parent_collection)
        if result ==  False:
            return(False)
        elif self.actor == 'none':
            return(False)
        elif self.actor_label_type == 'resource' and (self.actor.cell.resource == 'none' or (not self.actor.cell.visible) or self.actor.grid.is_abstract_grid or (self.actor.cell.visible and (self.actor.cell.has_building('resource') or self.actor.cell.has_building('village')))): #self.actor.actor_type == 'tile' and self.actor.grid.is_abstract_grid or (self.actor.cell.visible and (self.actor.cell.has_building('resource') or self.actor.cell.has_building('village'))): #do not show resource label on the Europe tile
            return(False)
        elif self.actor_label_type == 'resource building' and ((not self.actor.cell.visible) or (not self.actor.cell.has_building('resource'))):
            return(False)
        elif self.actor_label_type == 'village' and ((not self.actor.cell.visible) or (not self.actor.cell.has_building('village'))):
            return(False)
        elif self.actor_label_type in ['crew', 'passengers'] and not self.actor.is_vehicle: #do not show passenger or crew labels for non-vehicle mobs
            return(False)
        elif self.actor_label_type in ['workers', 'officer'] and not self.actor.is_group:
            return(False)
        elif self.actor.actor_type == 'mob' and (self.actor.in_vehicle or self.actor.in_group or self.actor.in_building): #do not show mobs that are attached to another unit/building
            return(False)
        elif self.actor_label_type == 'slums' and not self.actor.cell.has_building('slums'):
            return(False)
        elif self.actor_label_type == 'minister' and not self.actor.controllable:
            return(False)
        elif self.actor_label_type in ['attitude', 'controllable'] and self.actor.controllable:
            return(False)
        elif self.actor_label_type == 'preferred_terrains' and not (self.actor.is_npmob and self.actor.npmob_type == 'beast'):
            return(False)
        elif self.actor_label_type == 'canoes' and not self.actor.has_canoes:
            return(False)
        elif self.actor_label_type == 'slave_traders_strength' and self.actor.grid != self.global_manager.get('slave_traders_grid'):
            return(False)
        elif self.actor_label_type == 'loyalty' and self.actor.apparent_corruption_description == 'unknown':
            return(False)
        elif self.actor_label_type == 'ability':
            empty = True
            for skill_type in self.actor.apparent_skills:
                if self.actor.apparent_skill_descriptions[skill_type] != 'unknown':
                    empty = False
            if empty:
                return(False)
            else:
                return(result)
        else:
            return(result)

class list_item_label(actor_display_label):
    '''
    Label that shows the information of a certain item in a list, like a train passenger among a list of passengers
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_label_type': string value - Type of actor information shown
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'list_index': int value - Index to determine item of list reflected
                'list_type': string value - Type of list associated with, like 'resource building' along with label type of 'building work crew' to show work crews attached to a resource 
                    building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.list_index = input_dict['list_index']
        self.list_type = input_dict['list_type']
        #input_dict['actor_label_type'] = self.list_type + ' list item'
        self.attached_list = []
        super().__init__(input_dict, global_manager)

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on one of the inputted actor's lists
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors
        Output:
            None
        '''
        self.attached_list = []
        #print(self.actor_label_type)
        super().calibrate(new_actor)

    def can_show(self, ignore_parent_collection=False):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as this label's list is long enough to contain this label's index, otherwise returns False
        '''
        if len(self.attached_list) > self.list_index:
            return(super().can_show(ignore_parent_collection))
        return(False)

class building_work_crews_label(actor_display_label):
    '''
    Label at the top of the list of work crews in a building that shows how many work crews are in it
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'building_type': string value - Type of building associated with, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.remove_work_crew_button = 'none'
        self.showing = False
        self.attached_building = 'none'
        input_dict['actor_label_type'] = 'building workers'
        super().__init__(input_dict, global_manager)
        self.building_type = input_dict['building_type']

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        self.actor = new_actor
        self.showing = False
        if not new_actor == 'none':
            self.attached_building = new_actor.cell.get_building(self.building_type)
            if not self.attached_building == 'none':
                self.set_label(self.message_start + str(len(self.attached_building.contained_work_crews)) + '/' + str(self.attached_building.scale))
                self.showing = True

    def can_show(self, ignore_parent_collection=False):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the displayed tile has a building of this label's building_type, otherwise returns False
        '''
        if self.showing:
            return(super().can_show(ignore_parent_collection))
        else:
            return(False)

class building_efficiency_label(actor_display_label):
    '''
    Label that shows a production building's efficiency, which is the number of attempts work crews at the building have to produce commodities
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'building_type': string value - Type of building associated with, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.remove_work_crew_button = 'none'
        self.showing = False
        input_dict['actor_label_type'] = 'building efficiency'
        super().__init__(input_dict, global_manager)
        self.building_type = input_dict['building_type']
        self.attached_building = 'none'

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        self.actor = new_actor
        self.showing = False
        if not new_actor == 'none':
            self.attached_building = new_actor.cell.get_building(self.building_type)
            if not self.attached_building == 'none':
                self.set_label('Efficiency: ' + str(self.attached_building.efficiency))
                self.showing = True

    def can_show(self, ignore_parent_collection=False):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the displayed tile has a building of this label's building_type, otherwise returns False
        '''
        if self.showing:
            return(super().can_show(ignore_parent_collection))
        else:
            return(False)

class native_info_label(actor_display_label): #possible actor_label_types: native aggressiveness, native population, native available workers
    '''
    Label that shows the population, aggressiveness, or number of available workers in a displayed tile's village
    '''
    def can_show(self, ignore_parent_collection=False):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the displayed tile is explored and has a village, otherwise returns False
        '''
        result = super().can_show(ignore_parent_collection)
        if result:
            if self.actor.cell.has_building('village') and self.actor.cell.visible:
                return(True)
        return(False)
        

class commodity_display_label(actor_display_label):
    '''
    Label that changes its text and attached image and button to match the commodity in a certain part of a currently selected actor's inventory    
    '''
    def __init__(self, input_dict, global_manager):

        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'minimum_width': int value - Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
                'actor_type': string value - Type of actor to display the information of, like 'mob' or 'tile'
                'commodity_index': int value - Index of actor's inventory reflected
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.current_commodity = 'none'
        input_dict['actor_label_type'] = 'commodity'
        super().__init__(input_dict, global_manager)
        self.showing_commodity = False
        self.commodity_index = input_dict['commodity_index']
        self.commodity_image = images.label_image((self.x - self.height, self.y), self.height, self.height, self.modes, self, self.global_manager) #self, coordinates, width, height, modes, attached_label, global_manager
        input_dict = {
            'coordinates': (self.x, self.y + 200),
            'width': self.height,
            'height': self.height,
            'modes': self.modes,
            'attached_label': self,
            'init_type': 'label button'
        }

        self.insert_collection_above()
        self.parent_collection.add_member(self.commodity_image, {'x_offset': -1 * self.height - 5})
        input_dict['coordinates'] = (0, 0)
        if self.actor_type == 'mob':
            input_dict['button_type'] = 'drop commodity'
            input_dict['image_id'] = 'buttons/commodity_drop_button.png'
            self.add_attached_button(input_dict)
            
            input_dict['button_type'] = 'drop all commodity'
            input_dict['image_id'] = 'buttons/commodity_drop_all_button.png'
            self.add_attached_button(input_dict)
            
        elif self.actor_type == 'tile':
            input_dict['button_type'] = 'pick up commodity'
            input_dict['image_id'] = 'buttons/commodity_pick_up_button.png'
            self.add_attached_button(input_dict)

            input_dict['button_type'] = 'pick up all commodity'
            input_dict['image_id'] = 'buttons/commodity_pick_up_all_button.png'
            self.add_attached_button(input_dict)
            
            input_dict['button_type'] = 'sell commodity'
            input_dict['image_id'] = 'buttons/commodity_sell_button.png'
            self.add_attached_button(input_dict)
            
            input_dict['button_type'] = 'sell all commodity'
            input_dict['image_id'] = 'buttons/commodity_sell_all_button.png'
            self.add_attached_button(input_dict)

    def set_label(self, new_message):
        '''
        Description:
            Sets this label's text to the inputted string and changes locations of attached buttons since the length of the label may change. Also changes this label's attached image to match the commodity
        Input:
            string new_message: New text to set this label to
        Output:
            None
        '''
        super().set_label(new_message)
        if not self.actor == 'none':
            commodity_list = self.actor.get_held_commodities()
            if len(commodity_list) > self.commodity_index:
                commodity = commodity_list[self.commodity_index]
                self.commodity_image.set_image('scenery/resources/' + commodity + '.png')

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            commodity_list = new_actor.get_held_commodities()
            if len(commodity_list) - 1 >= self.commodity_index: #if index in commodity list
                self.showing_commodity = True
                commodity = commodity_list[self.commodity_index]
                self.current_commodity = commodity
                self.set_label(commodity + ': ' + str(new_actor.get_inventory(commodity))) #format - commodity_name: how_many
            else:
                self.showing_commodity = False
                self.set_label('n/a')
        else:
            self.showing_commodity = False
            self.set_label('n/a')

    def can_show(self, ignore_parent_collection=False):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns False if this label's commodity_index is not in the attached actor's inventory. Otherwise, returns same value as superclass
        '''
        if not self.showing_commodity:
            return(False)
        else:
            return(super().can_show(ignore_parent_collection))
