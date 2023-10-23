#Contains functionality for icons that follow the mouse pointer

import pygame
from ..constructs.images import free_image
import modules.constants.constants as constants
import modules.constants.flags as flags

class mouse_follower_template(free_image):
    '''
    Free image that follows the mouse pointer and appears in certain situations, such as when choosing on a movement destination
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['image_id'] = 'misc/targeting_mouse.png'
        input_dict['coordinates'] = pygame.mouse.get_pos()
        input_dict['width'] = 50
        input_dict['height'] = 50
        input_dict['modes'] = ['strategic', 'europe']
        super().__init__(input_dict, global_manager)
        
    def update(self):
        ''''
        Description:
            Moves this image to follow the mouse pointer
        Input:
            None
        Output:
            None
        '''
        self.x, self.y = pygame.mouse.get_pos()
        self.x -= self.width // 2
        self.y += self.height // 2

    def draw(self):
        '''
        Description:
            Draws this image if the player is currently choosing a movement destination
        Input:
            None
        Output:
            None
        '''
        if flags.choosing_destination or flags.choosing_advertised_commodity or flags.drawing_automatic_route:
            self.update()
            super().draw()
