#Contains functionality for creating new games, saving, and loading

import random
import pickle
from ...util import scaling, game_transitions, turn_management_utility, text_utility, market_utility, minister_utility, actor_utility, tutorial_utility
from ...interface_types import grids
from . import global_manager_template
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class save_load_manager_template():
    '''
    Object that controls creating new games, saving, and loading
    '''
    def __init__(self, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.copied_globals = []
        self.copied_constants = []
        self.copied_statuses = []
        self.copied_flags = []
        self.set_copied_elements()

    def set_copied_elements(self):
        '''
        Description:
            Determines which variables should be saved and loaded
        Input:
            None
        Output:
            None
        '''
        self.copied_globals = []
        self.copied_globals.append('commodity_prices')
        self.copied_globals.append('african_worker_upkeep')
        self.copied_globals.append('european_worker_upkeep')
        self.copied_globals.append('slave_worker_upkeep')
        self.copied_globals.append('recruitment_costs')
        self.copied_globals.append('minister_appointment_tutorial_completed')
        self.copied_globals.append('exit_minister_screen_tutorial_completed')
        self.copied_globals.append('transaction_history')
        self.copied_globals.append('previous_financial_report')
        self.copied_globals.append('num_wandering_workers')
        self.copied_globals.append('sold_commodities')
        self.copied_globals.append('slave_traders_strength')
        self.copied_globals.append('slave_traders_natural_max_strength')
        self.copied_globals.append('completed_lore_mission_types')

        self.copied_constants = []
        self.copied_constants.append('action_prices')
        self.copied_constants.append('turn')
        self.copied_constants.append('public_opinion')
        self.copied_constants.append('money')
        self.copied_constants.append('evil')
        self.copied_constants.append('fear')
        self.copied_constants.append('current_game_mode')

        self.copied_statuses = []
        self.copied_statuses.append('current_country_name')

        self.copied_flags = []
        self.copied_flags.append('prosecution_bribed_judge')
        
    def new_game(self, country):
        '''
        Description:
            Creates a new game and leaves the main menu
        Input:
            country country: Country being played in the new game
        Output:
            None
        '''
        flags.creating_new_game = True
        country.select()
        strategic_grid_height = 300
        strategic_grid_width = 320
        mini_grid_height = 600
        mini_grid_width = 640

        status.strategic_map_grid = grids.grid(False, {
            'coordinates': scaling.scale_coordinates(constants.default_display_width - (strategic_grid_width + 100), constants.default_display_height - (strategic_grid_height + 25)),
            'width': scaling.scale_width(strategic_grid_width),
            'height': scaling.scale_height(strategic_grid_height),
            'coordinate_width': self.global_manager.get('strategic_map_width'),
            'coordinate_height': self.global_manager.get('strategic_map_height'),
            'internal_line_color': 'black',
            'external_line_color': 'black',
            'modes': ['strategic'],
            'strategic_grid': True,
            'grid_line_width': 2
        }, self.global_manager)

        status.minimap_grid = grids.mini_grid(False, {
            'coordinates': scaling.scale_coordinates(constants.default_display_width - (mini_grid_width + 100),
                constants.default_display_height - (strategic_grid_height + mini_grid_height + 50)),
            'width': scaling.scale_width(mini_grid_width),
            'height': scaling.scale_height(mini_grid_height),
            'coordinate_width': 5,
            'coordinate_height': 5,
            'internal_line_color': 'black',
            'external_line_color': 'bright red',
            'modes': ['strategic'],
            'grid_line_width': 3,
            'attached_grid': status.strategic_map_grid
        }, self.global_manager)

        europe_grid_x = constants.europe_grid_x #constants.default_display_width - (strategic_grid_width + 340)
        europe_grid_y = constants.europe_grid_y #constants.default_display_height - (strategic_grid_height + 25)

        status.europe_grid = grids.abstract_grid(False, {
            'coordinates': scaling.scale_coordinates(europe_grid_x, europe_grid_y),
            'width': scaling.scale_width(120),
            'height': scaling.scale_height(120),
            'internal_line_color': 'black',
            'external_line_color': 'black',
            'modes': ['strategic', 'europe'],
            'tile_image_id': 'locations/europe/' + country.name + '.png',
            'grid_line_width': 3,
            'name': 'Europe'
        }, self.global_manager)


        slave_traders_grid_x = europe_grid_x #constants.default_display_width - (strategic_grid_width + 340)
        slave_traders_grid_y = constants.default_display_height - (strategic_grid_height - 120) #started at 25, -120 for europe grid y, -25 for space between

        status.slave_traders_grid = grids.abstract_grid(False, {
            'coordinates': scaling.scale_coordinates(slave_traders_grid_x, slave_traders_grid_y),
            'width': scaling.scale_width(120),
            'height': scaling.scale_height(120),
            'internal_line_color': 'black',
            'external_line_color': 'black',
            'modes': ['strategic'],
            'tile_image_id': 'locations/slave_traders/default.png', 
            'grid_line_width': 3,
            'name': 'Slave traders'
        }, self.global_manager)
        
        game_transitions.set_game_mode('strategic', self.global_manager)
        game_transitions.create_strategic_map(self.global_manager, from_save=False)
        status.minimap_grid.calibrate(2, 2)

        game_transitions.set_game_mode('ministers', self.global_manager)

        for current_commodity in self.global_manager.get('commodity_types'):
            if not current_commodity == 'consumer goods':
                #min_price = self.global_manager.get('commodity_min_starting_price')
                #max_price = self.global_manager.get('commodity_max_starting_price')
                price = round((random.randrange(1, 7) + random.randrange(1, 7))/2)
                increase = 0
                if current_commodity == 'gold':
                    increase = random.randrange(1, 7)
                elif current_commodity == 'diamond':
                    increase = random.randrange(1, 7) + random.randrange(1, 7)
                price += increase    
                market_utility.set_price(current_commodity, price, self.global_manager) #2-5
            else:
                market_utility.set_price(current_commodity, self.global_manager.get('consumer_goods_starting_price'), self.global_manager)

        constants.money_tracker.reset_transaction_history()
        constants.money_tracker.set(500)
        constants.turn_tracker.set(0)
        constants.public_opinion_tracker.set(50)
        constants.money_tracker.change(0) #updates projected income display
        constants.evil_tracker.set(0)
        constants.fear_tracker.set(1)

        self.global_manager.set('slave_traders_natural_max_strength', 10) #regenerates to natural strength, can increase indefinitely when slaves are purchased
        actor_utility.set_slave_traders_strength(self.global_manager.get('slave_traders_natural_max_strength'), self.global_manager)
        flags.player_turn = True
        self.global_manager.set('previous_financial_report', 'none')

        constants.actor_creation_manager.create_initial_ministers(self.global_manager)

        constants.available_minister_left_index = -2

        self.global_manager.set('num_african_workers', 0)
        self.global_manager.set('num_european_workers', 0)
        self.global_manager.set('num_slave_workers', 0)
        self.global_manager.set('num_wandering_workers', 0)
        self.global_manager.set('num_church_volunteers', 0)
        self.global_manager.set('african_worker_upkeep', self.global_manager.get('initial_african_worker_upkeep'))
        self.global_manager.set('european_worker_upkeep', self.global_manager.get('initial_european_worker_upkeep'))
        self.global_manager.set('slave_worker_upkeep', self.global_manager.get('initial_slave_worker_upkeep'))
        self.global_manager.get('recruitment_costs')['slave workers'] = self.global_manager.get('base_slave_recruitment_cost')
        actor_utility.reset_action_prices(self.global_manager)
        for current_commodity in self.global_manager.get('commodity_types'):
            self.global_manager.get('sold_commodities')[current_commodity] = 0
        flags.prosecution_bribed_judge = False

        for i in range(1, random.randrange(5, 8)):
            turn_management_utility.manage_villages(self.global_manager)
            turn_management_utility.manage_warriors(self.global_manager)
            actor_utility.spawn_beast(self.global_manager)
        
        minister_utility.update_available_minister_display(self.global_manager)

        turn_management_utility.start_player_turn(self.global_manager, True)
        if not constants.effect_manager.effect_active('skip_intro'):
            self.global_manager.set('minister_appointment_tutorial_completed', False)
            self.global_manager.set('exit_minister_screen_tutorial_completed', False)
            tutorial_utility.show_tutorial_notifications(self.global_manager)
        else:
            self.global_manager.set('minister_appointment_tutorial_completed', True)
            self.global_manager.set('exit_minister_screen_tutorial_completed', True)
            for current_minister_position_index in range(len(self.global_manager.get('minister_types'))):
                status.minister_list[current_minister_position_index].appoint(self.global_manager.get('minister_types')[current_minister_position_index])
            game_transitions.set_game_mode('strategic', self.global_manager)
        flags.creating_new_game = False
        
    def save_game(self, file_path):
        '''
        Description:
            Saves the game in the file corresponding to the inputted file path
        Input:
            None
        Output:
            None
        '''
        file_path = 'save_games/' + file_path
        saved_global_manager = global_manager_template.global_manager_template()
        self.global_manager.set('transaction_history', constants.money_tracker.transaction_history)
        for current_element in self.copied_globals: #save necessary data into new global manager
            saved_global_manager.set(current_element, self.global_manager.get(current_element))
        
        saved_constants = {}
        for current_element in self.copied_constants:
            saved_constants[current_element] = getattr(constants, current_element)

        saved_statuses = {}
        for current_element in self.copied_statuses:
            saved_statuses[current_element] = getattr(status, current_element)

        saved_flags = {}
        for current_element in self.copied_flags:
            saved_flags[current_element] = getattr(flags, current_element)

        saved_grid_dicts = []
        for current_grid in status.grid_list:
            if not current_grid.is_mini_grid: #minimap grid doesn't need to be saved
                saved_grid_dicts.append(current_grid.to_save_dict())

            
        saved_actor_dicts = []
        for current_pmob in status.pmob_list:
            if not (current_pmob.in_group or current_pmob.in_vehicle or current_pmob.in_building): #containers save their contents and load them in, contents don't need to be saved/loaded separately
                saved_actor_dicts.append(current_pmob.to_save_dict())
                
        for current_npmob in status.npmob_list:
            if current_npmob.saves_normally: #for units like native warriors that are saved as part a village and not as their own unit, do not attempt to save from here
                saved_actor_dicts.append(current_npmob.to_save_dict())
            
        for current_building in status.building_list:
            saved_actor_dicts.append(current_building.to_save_dict())
            
        for current_loan in status.loan_list:
            saved_actor_dicts.append(current_loan.to_save_dict())

        saved_minister_dicts = []        
        for current_minister in status.minister_list:
            saved_minister_dicts.append(current_minister.to_save_dict())
            if constants.effect_manager.effect_active('show_corruption_on_save'):
                print(current_minister.name + ', ' + current_minister.current_position + ', skill modifier: ' + str(current_minister.get_skill_modifier()) + ', corruption threshold: ' + str(current_minister.corruption_threshold) +
                    ', stolen money: ' + str(current_minister.stolen_money) + ', personal savings: ' + str(current_minister.personal_savings))

        saved_lore_mission_dicts = []
        for current_lore_mission in self.global_manager.get('lore_mission_list'):
            saved_lore_mission_dicts.append(current_lore_mission.to_save_dict())

        with open(file_path, 'wb') as handle: #write wb, read rb
            pickle.dump(saved_global_manager, handle) #saves new global manager with only necessary information to file
            pickle.dump(saved_constants, handle)
            pickle.dump(saved_statuses, handle)
            pickle.dump(saved_flags, handle)
            pickle.dump(saved_grid_dicts, handle)
            pickle.dump(saved_actor_dicts, handle)
            pickle.dump(saved_minister_dicts, handle)
            pickle.dump(saved_lore_mission_dicts, handle)
            handle.close()
        text_utility.print_to_screen('Game successfully saved to ' + file_path, self.global_manager)

    def load_game(self, file_path):
        '''
        Description:
            Loads a saved game from the file corresponding to the inputted file path
        Input:
            None
        Output:
            None
        '''
        flags.loading_save = True
        
        text_utility.print_to_screen('', self.global_manager)
        text_utility.print_to_screen('Loading ' + file_path, self.global_manager)
        game_transitions.start_loading(self.global_manager)
        #load file
        try:
            file_path = 'save_games/' + file_path
            with open(file_path, 'rb') as handle:
                new_global_manager = pickle.load(handle)
                saved_constants = pickle.load(handle)
                saved_statuses = pickle.load(handle)
                saved_flags = pickle.load(handle)
                saved_grid_dicts = pickle.load(handle)
                saved_actor_dicts = pickle.load(handle)
                saved_minister_dicts = pickle.load(handle)
                saved_lore_mission_dicts = pickle.load(handle)
                handle.close()
        except:
            text_utility.print_to_screen('The ' + file_path + ' file does not exist.', self.global_manager)
            return()

        #load variables
        for current_element in self.copied_globals:
            self.global_manager.set(current_element, new_global_manager.get(current_element))
        for current_element in self.copied_constants:
            setattr(constants, current_element, saved_constants[current_element])
        for current_element in self.copied_statuses:
            setattr(status, current_element, saved_statuses[current_element])
        for current_element in self.copied_flags:
            setattr(flags, current_element, saved_flags[current_element])
        constants.money_tracker.set(constants.money)
        constants.money_tracker.transaction_history = self.global_manager.get('transaction_history')
        constants.turn_tracker.set(constants.turn)
        constants.public_opinion_tracker.set(constants.public_opinion)
        constants.evil_tracker.set(constants.evil)
        constants.fear_tracker.set(constants.fear)

        getattr(status, status.current_country_name).select() #selects the country object with the same identifier as the saved country name

        text_utility.print_to_screen('', self.global_manager)
        text_utility.print_to_screen('Turn ' + str(constants.turn), self.global_manager)

        #load grids
        strategic_grid_height = 300
        strategic_grid_width = 320
        mini_grid_height = 600
        mini_grid_width = 640
        europe_grid_x = constants.europe_grid_x #constants.default_display_width - (strategic_grid_width + 340)
        europe_grid_y = constants.europe_grid_y #constants.default_display_height - (strategic_grid_height + 25)
        slave_traders_grid_x = europe_grid_x #constants.default_display_width - (strategic_grid_width + 340)
        slave_traders_grid_y = constants.default_display_height - (strategic_grid_height - 120)
        for current_grid_dict in saved_grid_dicts:
            input_dict = current_grid_dict
            if current_grid_dict['grid_type'] == 'strategic_map_grid':
                input_dict['coordinates'] = scaling.scale_coordinates(constants.default_display_width - (strategic_grid_width + 100), constants.default_display_height - (strategic_grid_height + 25))
                input_dict['width'] = scaling.scale_width(strategic_grid_width)
                input_dict['height'] = scaling.scale_height(strategic_grid_height)
                input_dict['coordinate_width'] = self.global_manager.get('strategic_map_width')
                input_dict['coordinate_height'] = self.global_manager.get('strategic_map_height')
                input_dict['internal_line_color'] = 'black'
                input_dict['external_line_color'] = 'black'
                input_dict['modes'] = ['strategic']
                input_dict['strategic_grid'] = True
                input_dict['grid_line_width'] = 2
                status.strategic_map_grid = grids.grid(True, input_dict, self.global_manager)
                
            elif current_grid_dict['grid_type'] in ['europe_grid', 'slave_traders_grid']:
                input_dict['width'] = scaling.scale_width(120)
                input_dict['height'] = scaling.scale_height(120)
                input_dict['internal_line_color'] = 'black'
                input_dict['external_line_color'] = 'black'
                input_dict['grid_line_width'] = 3
                if current_grid_dict['grid_type'] == 'europe_grid':
                    input_dict['modes'] = ['strategic', 'europe']
                    input_dict['coordinates'] = scaling.scale_coordinates(europe_grid_x, europe_grid_y)
                    input_dict['tile_image_id'] = 'locations/europe/' + status.current_country.name + '.png' 
                    input_dict['name'] = 'Europe'
                    status.europe_grid = grids.abstract_grid(True, input_dict, self.global_manager)
                else:
                    input_dict['modes'] = ['strategic']
                    input_dict['coordinates'] = scaling.scale_coordinates(slave_traders_grid_x, slave_traders_grid_y)
                    input_dict['tile_image_id'] = 'locations/slave_traders/default.png' 
                    input_dict['name'] = 'Slave traders'
                    status.slave_traders_grid = grids.abstract_grid(True, input_dict, self.global_manager)

        status.minimap_grid = grids.mini_grid(False, {
            'coordinates': scaling.scale_coordinates(constants.default_display_width - (mini_grid_width + 100),
                constants.default_display_height - (strategic_grid_height + mini_grid_height + 50)),
            'width': scaling.scale_width(mini_grid_width),
            'height': scaling.scale_height(mini_grid_height),
            'coordinate_width': 5,
            'coordinate_height': 5,
            'internal_line_color': 'black',
            'external_line_color': 'bright red',
            'modes': ['strategic'],
            'grid_line_width': 3,
            'attached_grid': status.strategic_map_grid
        }, self.global_manager)
        
        game_transitions.set_game_mode('strategic', self.global_manager)
        game_transitions.create_strategic_map(self.global_manager, from_save=True)
        if constants.effect_manager.effect_active('eradicate_slave_trade'):
            actor_utility.set_slave_traders_strength(0, self.global_manager)
        else:
            actor_utility.set_slave_traders_strength(self.global_manager.get('slave_traders_strength'), self.global_manager)

        #load actors
        for current_actor_dict in saved_actor_dicts:
            constants.actor_creation_manager.create(True, current_actor_dict, self.global_manager)
        for current_minister_dict in saved_minister_dicts:
            constants.actor_creation_manager.create_minister(True, current_minister_dict, self.global_manager)
        for current_lore_mission_dict in saved_lore_mission_dicts:
            constants.actor_creation_manager.create_lore_mission(True, current_lore_mission_dict, self.global_manager)
        constants.available_minister_left_index = -2
        minister_utility.update_available_minister_display(self.global_manager)
        self.global_manager.get('commodity_prices_label').update_label()
        
        status.minimap_grid.calibrate(2, 2)
        if saved_constants['current_game_mode'] != 'strategic':
            game_transitions.set_game_mode(saved_constants['current_game_mode'], self.global_manager)

        for current_completed_lore_type in self.global_manager.get('completed_lore_mission_types'):
            self.global_manager.get('lore_types_effects_dict')[current_completed_lore_type].apply()

        tutorial_utility.show_tutorial_notifications(self.global_manager)

        flags.loading_save = False
