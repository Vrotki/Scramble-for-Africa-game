#Contains functionality for buttons relating to the European headquarters screen

import random
from .buttons import button
from ..util import main_loop_utility, text_utility, market_utility, utility, actor_utility, minister_utility
import modules.constants.constants as constants
import modules.constants.status as status

class recruitment_button(button):
    '''
    Button that creates a new unit with a type depending on recruitment_type and places it in Europe
    '''
    def __init__(self, input_dict):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'recruitment_type': string value - Type of unit recruited by this button, like 'explorer'
        Output:
            None
        '''
        self.recruitment_type = input_dict['recruitment_type']
        if self.recruitment_type in constants.country_specific_units:
            if status.current_country:
                self.mob_image_id = 'mobs/' + self.recruitment_type + '/' + status.current_country.adjective + '/default.png'
            else:
                self.mob_image_id = 'mobs/default/default.png'
        elif self.recruitment_type in constants.recruitment_types:
            self.mob_image_id = 'mobs/' + self.recruitment_type + '/default.png'
        else:
            self.mob_image_id = 'mobs/default/default.png'
        self.recruitment_name = ''
        for character in self.recruitment_type:
            if not character == '_':
                self.recruitment_name += character
            else:
                self.recruitment_name += ' '
        status.recruitment_button_list.append(self)
        if self.recruitment_name.endswith(' workers'):
            image_id_list = ['buttons/default_button_alt.png']
            left_worker_dict = {
                'image_id': self.mob_image_id,
                'size': 0.8,
                'x_offset': -0.2,
                'y_offset': 0,
                'level': 1
            }
            image_id_list.append(left_worker_dict)

            right_worker_dict = left_worker_dict.copy()
            right_worker_dict['x_offset'] *= -1
            image_id_list.append(right_worker_dict)
        else:
            image_id_list = ['buttons/default_button_alt.png', {'image_id': self.mob_image_id, 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
        input_dict['image_id'] = image_id_list
        input_dict['button_type'] = 'recruitment'
        super().__init__(input_dict)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button creates a new unit with a type depending on recruitment_type and places it in Europe
        Input:
            None
        Output:
            None
        '''
        cost = constants.recruitment_costs[self.recruitment_type]
        if main_loop_utility.action_possible():
            if constants.money_tracker.get() >= cost:
                choice_info_dict = {'recruitment_type': self.recruitment_type, 'cost': cost, 'mob_image_id': self.mob_image_id, 'type': 'recruitment'}
                constants.actor_creation_manager.display_recruitment_choice_notification(choice_info_dict, self.recruitment_name)
            else:
                text_utility.print_to_screen('You do not have enough money to recruit this unit')
        else:
            text_utility.print_to_screen('You are busy and cannot recruit a unit')

    def calibrate(self, country):
        '''
        Description:
            Sets this button's image to the country-specific version for its unit, like a British or French major. Should make sure self.recruitment_type is in the country_specific_units 
                list
        Input:
            country country: Country that this button's unit should match
        Output:
            None
        '''
        self.mob_image_id = {'image_id': 'mobs/' + self.recruitment_type + '/' + country.adjective + '/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}
        image_id_list = ['buttons/default_button_alt.png', self.mob_image_id]
        self.image.set_image(image_id_list)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the type of unit it recruits
        Input:
            None
        Output:
            None
        '''
        actor_utility.update_descriptions(self.recruitment_type)
        cost = constants.recruitment_costs[self.recruitment_type]
        if self.recruitment_type.endswith(' workers'):
            self.set_tooltip(['Recruits a unit of ' + self.recruitment_name + ' for ' + str(cost) + ' money.'] + constants.list_descriptions[self.recruitment_type])
        else:
            self.set_tooltip(['Recruits ' + utility.generate_article(self.recruitment_type) + ' ' + self.recruitment_name + ' for ' + str(cost) + ' money.'] + constants.list_descriptions[self.recruitment_type])

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        status.recruitment_button_list = utility.remove_from_list(status.recruitment_button_list, self)

class buy_commodity_button(button):
    '''
    Button that buys a unit of commodity_type when clicked and has an image matching that of its commodity
    '''
    def __init__(self, input_dict):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'commodity_type': string value - Type of commodity that this button buys, like 'consumer goods'
        Output:
            None
        '''
        possible_commodity_types = constants.commodity_types
        self.commodity_type = input_dict['commodity_type']
        if self.commodity_type in possible_commodity_types:
            input_dict['image_id'] = ['buttons/default_button_alt.png', 'scenery/resources/' + self.commodity_type + '.png']
        else:
            input_dict['image_id'] = 'buttons/default_button.png'
        input_dict['button_type'] = 'buy commodity'
        super().__init__(input_dict)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button buys a unit of the commodity_type commodity
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible():
            cost = constants.commodity_prices[self.commodity_type]
            if constants.money_tracker.get() >= cost:
                if minister_utility.positions_filled():
                    actor_utility.calibrate_actor_info_display(status.tile_info_display, status.europe_grid.cell_list[0][0].tile)
                    status.europe_grid.cell_list[0][0].tile.change_inventory(self.commodity_type, 1) #adds 1 of commodity type to
                    constants.money_tracker.change(-1 * cost, 'items')
                    if self.commodity_type.endswith('s'):
                        text_utility.print_to_screen('You spent ' + str(cost) + ' money to buy 1 unit of ' + self.commodity_type + '.')
                    else:
                        text_utility.print_to_screen('You spent ' + str(cost) + ' money to buy 1 ' + self.commodity_type + '.')
                    if random.randrange(1, 7) == 1 and self.commodity_type in constants.commodity_types: #1/6 chance
                        market_utility.change_price(self.commodity_type, 1)
                        text_utility.print_to_screen('The price of ' + self.commodity_type + ' has increased from ' + str(cost) + ' to ' + str(cost + 1) + '.')
                    actor_utility.calibrate_actor_info_display(status.tile_inventory_info_display, status.displayed_tile_inventory)
            else:
                text_utility.print_to_screen('You do not have enough money to purchase this commodity')
        else:
            text_utility.print_to_screen('You are busy and cannot purchase ' + self.commodity_type + '.')

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the commodity that it buys and its price
        Input:
            None
        Output:
            None
        '''
        if self.commodity_type.endswith('s'):
            self.set_tooltip(['Purchases 1 unit of ' + self.commodity_type + ' for ' + str(constants.commodity_prices[self.commodity_type]) + ' money.'])
        else:
            self.set_tooltip(['Purchases 1 ' + self.commodity_type + ' for ' + str(constants.commodity_prices[self.commodity_type]) + ' money.'])
        