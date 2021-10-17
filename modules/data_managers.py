import random
from . import csv_tools
from . import notifications
from . import choice_notifications
from . import action_notifications
from . import scaling

class global_manager_template():
    '''
    Object designed to manage a dictionary of shared variables and be passed between functions and objects as a simpler alternative to passing each variable or object separately
    '''
    def __init__(self):
        '''
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        '''
        self.global_dict = {}
        
    def get(self, name):
        '''
        Description:
            Returns the value in this object's dictionary corresponding to the inputted key
        Input:
            string name: Name of a key in this object's dictionary
        Output:
            any type: The value corresponding to the inputted key's entry in this object's dictionary
        '''
        return(self.global_dict[name])
    
    def set(self, name, value):
        '''
        Description:
            Sets or initializes the inputted value for the inputted key in this object's dictionary
        Input:
            string name: Name of the key in this object's dictionary to initialize/modify
            any type value: Value corresponding to the new/modified key
        Output:
            None
        '''
        self.global_dict[name] = value

class input_manager_template():
    '''
    Object designed to manage the passing of typed input from the text box to different parts of the program
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
        self.previous_input = ''
        self.taking_input = False
        self.old_taking_input = self.taking_input
        self.stored_input = ''
        self.send_input_to = ''
        
    def check_for_input(self):
        '''
        Description:
            Returns true if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        Input:
            None
        Output:
            boolean: True if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        '''
        if self.old_taking_input == True and self.taking_input == False: 
            return(True)
        else:
            return(False)
        
    def start_receiving_input(self, solicitant, message):
        '''
        Description:
            Displays the prompt for the user to enter input and prepares to receive input and send it to the part of the program requesting input
        Input:
            string solicitant: Represents the part of the program to send input to
            string message: Prompt given to the player to enter input
        Output:
            None
        '''
        text_tools.print_to_screen(message, self.global_manager)
        self.send_input_to = solicitant
        self.taking_input = True
        
    def update_input(self):
        '''
        Description:
            Updates whether this object is currently taking input
        Input:
            None
        Output:
            None
        '''
        self.old_taking_input = self.taking_input
        
    def receive_input(self, received_input):
        '''
        Description:
            Sends the inputted string to the part of the program that initially requested input
        Input:
            String received_input: Input entered by the user into the text box
        Output:
            None
        '''
        if self.send_input_to == 'do something':
            if received_input == 'done':
                self.global_manager.set('crashed', True)
            else:
                text_tools.print_to_screen("I didn't understand that.")

class flavor_text_manager_template():
    '''
    Object that reads flavor text from .csv files and distributes it to other parts of the program when requested
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
        self.explorer_flavor_text_list = []
        current_flavor_text = csv_tools.read_csv('text/flavor_explorer.csv')
        for line in current_flavor_text: #each line is a list
            self.explorer_flavor_text_list.append(line[0])
        self.subject_dict = {}
        self.subject_dict['explorer'] = self.explorer_flavor_text_list
                
    def generate_flavor_text(self, subject):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        '''
        return(random.choice(self.subject_dict['explorer']))

class value_tracker():
    '''
    Object that controls the value of a certain variable
    '''
    def __init__(self, value_key, initial_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string value_key: Key used to access this tracker's variable in the global manager
            any type initial_value: Value that this tracker's variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.set(value_key, initial_value)
        self.value_label = 'none'
        self.value_key = value_key

    def get(self):
        '''
        Description:
            Returns the value of this tracker's variable
        Input:
            None
        Output:
            any type: Value of this tracker's variable
        '''
        return(self.global_manager.get(self.value_key))

    def change(self, value_change):
        '''
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        '''
        self.global_manager.set(self.value_key, self.get() + value_change)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())
    
    def set(self, new_value):
        '''
        Description:
            Sets the value of this tracker's variable to the inputted amount
        Input:
            any type value_change: Value that this tracker's variable is set to
        Output:
            None
        '''
        self.global_manager.set(self.value_key, initial_value)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())

class money_tracker(value_tracker):
    '''
    Value tracker that tracks money and causes the game to be lost when money runs out
    '''
    def __init__(self, initial_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            any type initial_value: Value that the money variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__('money', initial_value, global_manager)

    def change(self, value_change):
        '''
        Description:
            Changes the money variable by the inputted amount
        Input:
            int value_change: Amount that the money variable is changed
        Output:
            None
        '''
        super().change(value_change)
        if self.get() < 0:
            self.global_manager.set('crashed', True) #end game when money less than 0

    def set(self, new_value):
        '''
        Description:
            Sets the money variable to the inputted amount
        Input:
            int value_change: Value that the money variable is set to
        Output:
            None
        '''
        super().set(new_value)
        if self.get() < 0:
            self.global_manager.set('crashed', True) #end game when money less than 0

class notification_manager_template():
    '''
    Object that controls the displaying of notifications
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
        self.notification_queue = []
        self.notification_type_queue = []
        self.choice_notification_choices_queue = []
        self.choice_notification_info_dict_queue = []
        self.global_manager = global_manager
        self.update_notification_layout()

    def update_notification_layout(self):
        '''
        Description:
            Changes where notifications are displayed depending on the current game mode to avoid blocking relevant information
        Input:
            None
        Output:
            None
        '''
        self.notification_width = 500
        self.notification_height = 500
        self.notification_y = 236
        if self.global_manager.get('current_game_mode') in ['strategic', 'none']: #move notifications out of way of minimap on strategic mode or during setup
            self.notification_x = (scaling.unscale_width(self.global_manager.get('minimap_grid').origin_x, self.global_manager) - (self.notification_width + 40))
        else: #show notifications in center on europe mode
            self.notification_x = 610
            
    def notification_to_front(self, message):
        '''
        Description:
            Displays a new notification with text matching the inputted string and a type based on what is in the front of this object's notification type queue
        Input:
            string message: The text to put in the displayed notification
        Output:
            None
        '''
        self.update_notification_layout()
        notification_type = self.notification_type_queue.pop(0)
        if notification_type == 'roll':
            new_notification = action_notifications.dice_rolling_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, self.global_manager)
            
            for current_die in self.global_manager.get('dice_list'):
                current_die.start_rolling()

        elif notification_type in ['stop_trade', 'trade', 'trade_promotion', 'final_trade', 'successful_commodity_trade', 'failed_commodity_trade']:
            is_last = False
            commodity_trade = False
            commodity_trade_type = notification_type #for successful/failed_commodity_trade
            stops_trade = False
            if notification_type == 'stop_trade':
                stops_trade = True
            elif notification_type == 'final_trade':
                is_last = True
            elif notification_type in ['successful_commodity_trade', 'failed_commodity_trade']:
                commodity_trade = True
            elif notification_type == 'trade_promotion':
                self.global_manager.get('trade_result')[0].promote() #promotes caravan
            trade_info_dict = {'is_last': is_last, 'commodity_trade': commodity_trade, 'commodity_trade_type': notification_type, 'stops_trade': stops_trade}
            new_notification = action_notifications.trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, trade_info_dict, self.global_manager)
                
        elif notification_type == 'exploration':
            new_notification = action_notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, False, self.global_manager)
            
        elif notification_type == 'final_exploration':
            new_notification = action_notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, True, self.global_manager)

        elif notification_type == 'religious_campaign':
            new_notification = action_notifications.religious_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, False, self.global_manager)
            
        elif notification_type == 'final_religious_campaign':
            new_notification = action_notifications.religious_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, True, self.global_manager)
            
        elif notification_type == 'choice':
            choice_notification_choices = self.choice_notification_choices_queue.pop(0)
            choice_notification_info_dict = self.choice_notification_info_dict_queue.pop(0)
            new_notification = choice_notifications.choice_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, choice_notification_choices, choice_notification_info_dict, self.global_manager)

        else:
            new_notification = notifications.notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, self.global_manager)
                #coordinates, ideal_width, minimum_height, showing, modes, image, message
    
