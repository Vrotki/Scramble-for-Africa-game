#Contains functionality for interface elements and collections

import pygame
from . import scaling

class interface_element():
    '''
    Abstract base interface element class
    Object that can be contained in an interface collection and has a location, rect, and image bundle with particular conditions for displaying, along with an optional tooltip when displayed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates' = (0, 0): int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear, optional for elements with parent collections
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'member_config' = {}: Dictionary of extra configuration values for how to add elements to collections
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        old_input_dict = input_dict
        self.global_manager = global_manager
        self.width = input_dict['width']
        self.height = input_dict['height']
        self.Rect = pygame.Rect(0, self.global_manager.get('display_height') - (self.height), self.width, self.height)
        if not 'parent_collection' in input_dict:
            input_dict['parent_collection'] = 'none'
        self.parent_collection = input_dict['parent_collection']
        self.has_parent_collection = self.parent_collection != 'none'
        if not 'coordinates' in input_dict:
            input_dict['coordinates'] = (0, 0)
        self.x, self.y = input_dict['coordinates']
        if self.has_parent_collection:
            if not 'member_config' in input_dict:
                input_dict['member_config'] = {}
            if not 'x_offset' in input_dict['member_config']:
                input_dict['member_config']['x_offset'] = input_dict['coordinates'][0]
            if not 'y_offset' in input_dict['member_config']:
                input_dict['member_config']['y_offset'] = input_dict['coordinates'][1]
            self.parent_collection.add_member(self, input_dict['member_config'])
        else:
            self.set_origin(input_dict['coordinates'][0], input_dict['coordinates'][1])

        if 'modes' in input_dict:
            self.set_modes(input_dict['modes'])
        elif 'parent_collection' != 'none':
            self.set_modes(self.parent_collection.modes)

    def can_show(self):
        '''
        Description:
            Returns whether this button can be shown. By default, elements can be shown during game modes in which they can appear, iff their parent collection (if any) is also showing
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        '''
        if not self.has_parent_collection:
            if self.global_manager.get('current_game_mode') in self.modes:
                return(True)
        elif self.parent_collection.allow_show(self, self.ignore_minimized):
            if self.global_manager.get('current_game_mode') in self.modes:
                return(True)
        return(False)

    def set_origin(self, new_x, new_y):
        '''
        Description:
            Sets this interface element's location at the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        '''
        self.x = new_x
        self.Rect.x = self.x
        self.y = new_y
        self.Rect.y = self.global_manager.get('display_height') - (self.y + self.height)
        if self.has_parent_collection:
            self.x_offset = self.x - self.parent_collection.x
            self.y_offset = self.y - self.parent_collection.y

    def set_modes(self, new_modes):
        '''
        Description:
            Sets this interface element's active modes to the inputted list
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        '''
        self.modes = new_modes

    def calibrate(self, new_actor):
        '''
        Description:
            Allows subclasses to attach to the inputted actor and updates information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        return
    
    def insert_collection_above(self):
        '''
        Description:
            Replaces this element's place in its parent collection with a new interface collection, allowing elements to dynamically form collections after initialization 
                without interfering with above hierarchies
        'Input':
            None, could potentially modify to allow choosing the init type of collection to insert above
        'Output':
            None
        '''
        input_dict = {
            'coordinates': (self.x, self.y),
            'width': self.width,
            'height': self.height,
            'modes': self.modes,
            'parent_collection': self.parent_collection,
            'init_type': 'interface collection',
            'member_config': {'index': self.parent_collection.members.index(self)}
        }
        if self.parent_collection != 'none':
            if hasattr(self.parent_collection, 'order_overlap_list') and self in self.parent_collection.order_overlap_list:
                input_dict['member_config']['order_overlap'] = True
                input_dict['member_config']['order_overlap_index'] = self.parent_collections.order_overlap_list.index(self)

            if hasattr(self.parent_collection, 'order_exempt_list') and self in self.parent_collection.order_exempt_list:
                input_dict['member_config']['order_exempt'] = True
                input_dict['member_config']['order_exempt_index'] = self.parent_collection.order_exempt_list.index(self)

            if hasattr(self, 'x_offset'):
                input_dict['member_config']['x_offset'] = self.x_offset

            if hasattr(self, 'y_offset'):
                input_dict['member_config']['y_offset'] = self.y_offset

            if hasattr(self, 'order_x_offset'):
                input_dict['member_config']['order_x_offset'] = self.order_x_offset

            if hasattr(self, 'order_y_offset'):
                input_dict['member_config']['order_y_offset'] = self.order_y_offset
            
        new_parent_collection = self.global_manager.get('actor_creation_manager').create_interface_element(input_dict, self.global_manager)

        self.parent_collection.remove_member(self)
        
        new_parent_collection.add_member(self)

        return(new_parent_collection)

class interface_collection(interface_element):
    '''
    Object managing an image bundle and collection of interactive interface elements, including buttons, free images, and other interface collections
    An entire collection can be displayed or hidden as a unit, along with individual components having their own conditions for being visible when the window is displayed
    A collection could have different modes that display different sub-windows under different conditions while keeping other elements constant
    A particular type of collection could have special ordered functionality, like a series of buttons that can be scrolled through, or a images displayed in horizontal rows w/ maximum widths
    Older, informal collections such as the available minister scrollbar, the movement buttons, and the mob, tile, minister, prosecution, and defense displays should be able to be 
        implemented as interface collections. Additionally, the "mode" system could possibly be changed to use overarching interface collections for each mode
    Like an image bundle, members of an interface collection should have independent types and characteristics but be controlled as a unit and created in a list with a dictionary or simple 
        string. Unlike an image bundle, a collection does not necessarily have to be saved, and 
    '''
    def __init__(self, input_dict, global_manager):    
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
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.members = []
        self.minimized = False
        if 'is_info_display' in input_dict and input_dict['is_info_display']:
            self.is_info_display = True
            self.actor_type = input_dict['actor_type']
        else:
            self.is_info_display = False
        super().__init__(input_dict, global_manager)
        self.original_coordinates = (self.x, self.y)
        if self.is_info_display:
            global_manager.set(self.actor_type + '_info_display', self)
        self.description = input_dict.get('description', 'window')
        self.move_with_mouse_config = {'moving': False}
        customize_button_x_offset = 0
        customize_button_size = 20
        if 'allow_minimize' in input_dict and input_dict['allow_minimize']:
            member_input_dict = {
                'coordinates': scaling.scale_coordinates(customize_button_x_offset, 5, global_manager),
                'width': scaling.scale_width(customize_button_size, global_manager),
                'height': scaling.scale_height(customize_button_size, global_manager),
                'parent_collection': self,
                'init_type': 'minimize interface collection button',
                'image_id': 'buttons/minimize_button.png',
                'member_config': {'order_exempt': True, 'ignore_minimized': True}
            }
            global_manager.get('actor_creation_manager').create_interface_element(member_input_dict, global_manager)
            customize_button_x_offset += customize_button_size + 5
        if 'allow_move' in input_dict and input_dict['allow_move']:
            member_input_dict = {
                'coordinates': scaling.scale_coordinates(customize_button_x_offset, 5, global_manager),
                'width': scaling.scale_width(customize_button_size, global_manager),
                'height': scaling.scale_height(customize_button_size, global_manager),
                'parent_collection': self,
                'init_type': 'move interface collection button',
                'image_id': 'buttons/reposition_button.png',
                'member_config': {'order_exempt': True, 'ignore_minimized': True}
            }
            global_manager.get('actor_creation_manager').create_interface_element(member_input_dict, global_manager)
            customize_button_x_offset += customize_button_size + 5
            
            member_input_dict = {
                'coordinates': scaling.scale_coordinates(customize_button_x_offset, 5, global_manager),
                'width': scaling.scale_width(customize_button_size, global_manager),
                'height': scaling.scale_height(customize_button_size, global_manager),
                'parent_collection': self,
                'init_type': 'reset interface collection button',
                'image_id': 'buttons/reset_button.png',
                'member_config': {'order_exempt': True, 'ignore_minimized': True}
            }
            global_manager.get('actor_creation_manager').create_interface_element(member_input_dict, global_manager)
            customize_button_x_offset += customize_button_size + 5

    def calibrate(self, new_actor):
        '''
        Description:
            Atttaches this collection and its members to inputted actor and updates their information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        super().calibrate(new_actor)
        for member in self.members:
            member.calibrate(new_actor)
        if self.is_info_display:
            self.global_manager.set('displayed_' + self.actor_type, new_actor)
    
    def add_member(self, new_member, member_config={}):
        '''
        Description:
            Adds an existing interface element as a member of this collection and sets its origin coordinates relative to this collection's origin coordinates
        Input:
            interface_element new_member: New element to add as a member
            int x_offset: Number of pixels to the right the new member's origin should be from the collection's origin
            int x_offset: Number of pixels upward the new member's origin should be from the collection's origin
        Output:
            None
        '''
        if not 'x_offset' in member_config:
            member_config['x_offset'] = 0
        if not 'y_offset' in member_config:
            member_config['y_offset'] = 0
        if not 'ignore_minimized' in member_config:
            member_config['ignore_minimized'] = False

        new_member.parent_collection = self
        new_member.has_parent_collection = True
        if not 'index' in member_config:
            self.members.append(new_member)
        else:
            self.members.insert(member_config['index'], new_member)
        new_member.ignore_minimized = member_config['ignore_minimized']
        new_member.set_origin(self.x + member_config['x_offset'], self.y + member_config['y_offset'])

    def remove_member(self, removed_member):
        '''
        Description:
            Removes a member from this collection
        Input:
            interface_element removed_member: Member to remove from this collection
        Output:
            None
        '''
        if hasattr(removed_member, 'x_offset'):
            removed_member.x_offset = None
        if hasattr(removed_member, 'y_offset'):
            removed_member.y_offset = None
        if hasattr(removed_member, 'ignore_minimized'):
            removed_member.ignore_minimized = None
        self.members.remove(removed_member)

    def set_origin(self, new_x, new_y):
        '''
        Description:
            Sets this interface element's location and those of its members to the inputted coordinates
        Input:
            int new_x: New x coordinate for this element's origin
            int new_y: New y coordinate for this element's origin
        Output:
            None
        '''
        super().set_origin(new_x, new_y)
        for member in self.members: #members will retain their relative positions with the collection while shifting to be centered around the new collection origin
            member.set_origin(new_x + member.x_offset, new_y + member.y_offset)

    def set_modes(self, new_modes):
        '''
        Description:
            Sets this interface element's active modes and those of its members to the inputted list
        Input:
            string list new_modes: List of game modes in which this element is active
        Output:
            None
        '''
        super().set_modes(new_modes)
        for member in self.members:
            member.set_modes(new_modes)

    def allow_show(self, member, ignore_minimized):
        return(self.can_show(ignore_minimized))

    def can_show(self, ignore_minimized = False):
        '''
        Description:
            Returns whether this collection can be shown. A collection can be shown if it is not minimized and could otherwise be shown
        Input:
            None
        Output:
            boolean: Returns True if this button can appear under current conditions, otherwise returns False
        '''
        result = super().can_show()
        if self.is_info_display and self.global_manager.get('displayed_' + self.actor_type) == 'none':
            return(False)
        elif ignore_minimized:
            return(result)
        else:
            return(result and not self.minimized)

class tabbed_collection(interface_collection):
    def __init__(self, input_dict, global_manager):
        self.tabbed_members = []
        self.current_tabbed_member = None
        super().__init__(input_dict, global_manager)
        tabs_collection_input_dict = {
            'coordinates': scaling.scale_coordinates(0, 5, global_manager),
            'width': scaling.scale_width(10, global_manager),
            'height': scaling.scale_height(30, global_manager),
            'init_type': 'ordered collection',
            'parent_collection': self,
            'direction': 'horizontal'
        }
        self.tabs_collection = global_manager.get('actor_creation_manager').create_interface_element(tabs_collection_input_dict, global_manager)

    def allow_show(self, member, ignore_minimized):
        if member in self.tabbed_members and member != self.current_tabbed_member:
            return(False)
        return(super().allow_show(member, ignore_minimized))

    def add_member(self, new_member, member_config={}):
        '''
        Description:
            Adds an existing interface element as a member of this collection and sets its origin coordinates relative to this collection's origin coordinates
        Input:

        Output:
            None
        '''
        if not 'tabbed' in member_config:
            member_config['tabbed'] = False
        elif member_config['tabbed']:
            if not 'button_image_id' in member_config:
                member_config['button_image_id'] = 'buttons/default_button.png'
        super().add_member(new_member, member_config)

        if member_config['tabbed']:
            tab_button_input_dict = {
                'width': scaling.scale_width(20, self.global_manager),
                'height': scaling.scale_height(20, self.global_manager),
                'init_type': 'tab button',
                'parent_collection': self.tabs_collection,
                'image_id': member_config['button_image_id'],
                'linked_element': new_member
            }
            self.global_manager.get('actor_creation_manager').create_interface_element(tab_button_input_dict, self.global_manager)
            self.tabbed_members.append(new_member)
            if len(self.tabbed_members) == 1:
                self.current_tabbed_member = new_member

class ordered_collection(interface_collection): #work on ordered collection documentation, remove info display documentation, add limited length ordered collections
    def __init__(self, input_dict, global_manager): #and change inventory display to a collection so that it orders correctly
        if not 'separation' in input_dict:
            input_dict['separation'] = scaling.scale_height(5, global_manager)
        if not 'direction' in input_dict:
            input_dict['direction'] = 'vertical'
        self.separation = input_dict['separation']
        self.direction = input_dict['direction']
        self.order_overlap_list = []
        self.order_exempt_list = []
        global_manager.get('ordered_collection_list').append(self)
        super().__init__(input_dict, global_manager)

    def add_member(self, new_member, member_config={}):
        '''
        Description:
            Adds an existing interface element as a member of this collection and sets its origin coordinates relative to this collection's origin coordinates
        Input:
            interface_element new_member: New element to add as a member
            int x_offset: Number of pixels to the right the new member's origin should be from the collection's origin
            int x_offset: Number of pixels upward the new member's origin should be from the collection's origin
        Output:
            None
        '''
        if not 'order_overlap' in member_config:
            member_config['order_overlap'] = False

        if not 'order_exempt' in member_config:
            member_config['order_exempt'] = False

        if not 'order_x_offset' in member_config:
            member_config['order_x_offset'] = 0
        new_member.order_x_offset = member_config['order_x_offset']

        if not 'order_y_offset' in member_config:
            member_config['order_y_offset'] = 0
        new_member.order_y_offset = member_config['order_y_offset']

        super().add_member(new_member, member_config)

        if member_config['order_overlap'] and hasattr(self, 'order_overlap_list'): #maybe have a list of lists to iterate through these operations
            if not 'order_overlap_index' in member_config:
                self.order_overlap_list.append(new_member)
            else:
                self.order_overlap_list.insert(member_config['order_overlap_index'], new_member)

        if member_config['order_exempt'] and hasattr(self, 'order_exempt_list'):
            if not 'order_exempt_index' in member_config:
                self.order_exempt_list.append(new_member)
            else:
                self.order_exempt_list.insert(member_config['order_exempt_index'], new_member)

    def remove_member(self, removed_member):
        '''
        Description:
            Removes a member from this collection
        Input:
            interface_element removed_member: Member to remove from this collection
        Output:
            None
        '''
        if hasattr(removed_member, 'order_x_offset'): #see if there is a way to modify these attributes with a variable instead of manually
            removed_member.order_x_offset = None
        if hasattr(removed_member, 'order_y_offset'):
            removed_member.order_y_offset = None
        if removed_member in self.order_overlap_list:
            self.order_overlap_list.remove(removed_member)
        if removed_member in self.order_exempt_list:
            self.order_exempt_list.remove(removed_member)
        super().remove_member(removed_member)

    def order_members(self):
        '''
        Description:
            Changes locations of collection members to put all visible members in order while skipping hidden ones
        Input:
            None
        Output:
            None
        '''
        current_y = self.y
        current_x = self.x
        for member in self.members:
            if member.can_show() and not member in self.order_exempt_list:
                if self.direction == 'vertical':
                    current_y -= member.height

                    new_x = self.x + member.order_x_offset
                    new_y = current_y + member.order_y_offset
                    if (member.x, member.y) != (new_x, new_y):
                        member.set_origin(self.x + member.order_x_offset, current_y + member.order_y_offset)

                    if not member in self.order_overlap_list:
                        current_y -= self.separation
                    else:
                        current_y += member.height

                elif self.direction == 'horizontal':
                    new_x = current_x + member.order_x_offset
                    new_y = self.y + member.order_y_offset
                    if (member.x, member.y) != (new_x, new_y):
                        member.set_origin(current_x + member.order_x_offset, self.y + member.order_y_offset)

                    if not member in self.order_overlap_list:
                        current_x += self.separation + member.width
