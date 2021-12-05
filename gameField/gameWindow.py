#class for game display
from gameField.gameAssets import *
from multiprocessing.dummy import Pool as ThreadPool
#from multiprocessing import Pool 

#----------------------------------------------------------------------

class spaceWindow:

    def __init__(self, ops_hex_map, game_screen, size_hex_IMG):
        self.hex_map_length = ops_hex_map.map_length
        self.hex_map_width = ops_hex_map.map_width
        self.ops_hex_map = ops_hex_map
        self.size_hex_IMG = size_hex_IMG
        self.game_screen = game_screen
        #movement variables
        self.move_window_X = 0
        self.move_window_Y = 0
        self.center_hex = -1
        self.window_border_Y = ((WIDTH - (self.size_hex_IMG * self.hex_map_width)) // 2) - self.move_window_Y
        self.window_border_X = ((LENGTH - (self.size_hex_IMG * self.hex_map_length)) // 2) + self.move_window_X
        #images
        self.EMPTY_HEX_IMG = EMPTY_HEX_IMG
        self.ASCS_SHIP_HEX_IMG = ASCS_SHIP_HEX_IMG
        self.ROT_ASCS_SHIP_HEX_IMG = ASCS_SHIP_HEX_IMG
        self.XNFF_SHIP_HEX_IMG = XNFF_SHIP_HEX_IMG
        self.ROT_XNFF_SHIP_HEX_IMG = XNFF_SHIP_HEX_IMG
        #selections
        self.selected_hex_index_coordinate = -1
        self.selected_hex = []
        self.ship_selected = False 
        self.targets_hexes = []
        self.active_fleet_command = 'NNNN'

        #animations
        self.base_hex_IMG = GRID_HEX_ANI_BASE
        self.base_hex_IMG.convert()
        self.template_hexes_IMG = {'aniHexB': GRID_HEX_ANI_EMPTY, 'aniHexEnemy': GRID_HEX_ANI_ENEMY, 'aniHexClick': GRID_HEX_ANI_CLICK, 
                            'aniHexMove': GRID_HEX_ANI_MOVE, 'aniHexTarget': GRID_HEX_ANI_TARGET, 'aniHexAlly': GRID_HEX_ANI_ALLY}
        for v in self.template_hexes_IMG.values():
            v.convert()
        self.animated_hexes_IMG = {'gridHex': self.template_hexes_IMG['aniHexB'], 'enemyHex': self.template_hexes_IMG['aniHexEnemy'], 
                            'clickHex': self.template_hexes_IMG['aniHexClick'], 'moveHex': self.template_hexes_IMG['aniHexMove'], 
                            'targetHex': self.template_hexes_IMG['aniHexTarget'], 'allyHex': self.template_hexes_IMG['aniHexAlly']}
        self.counter_animation_1 = 0
        self.counter_animation_2 = 0
        #scale
        self._scale_hexes(self.size_hex_IMG)

    #draw hexes on board
    def draw_hexes(self, active_fleet_command, some_ship_hex=[]):
        self.selected_hex = some_ship_hex
        self.active_fleet_command = active_fleet_command
        self.game_screen.blit(FIT_SPACE, (0, 0))

        if self.center_hex > -1:
            c = 0
            if (self.center_hex // self.hex_map_length) % 2 != 0:
                c = self.size_hex_IMG / 2
            self.move_window_X = int((self.hex_map_length / 2) - ((self.center_hex % self.hex_map_length) + 1)) * self.size_hex_IMG + c
            self.move_window_Y = int(((self.center_hex // self.hex_map_length)) - (self.hex_map_width / 2) + 0.5) * self.size_hex_IMG
            self.center_hex = -1
            
        #check of ship_selected
        self.ship_selected = False
        if some_ship_hex and not some_ship_hex.empty:
            self.targets_hexes = []
            some_ship = some_ship_hex.entity
            if some_ship.guns_primed():
                self.targets_hexes = some_ship.track_targets()
            self.ship_selected = True

        draw_pool = ThreadPool(2)
        draw_pool.map(self._draw_a_hex, self.ops_hex_map.space_hexes)
        draw_pool.close()


    def _draw_a_hex(self, some_hex):
        row_height = self.hex_map_width - (some_hex.hex_coordinate_index // self.hex_map_length) - 1
        indent = 0
        if row_height % 2 == self.hex_map_width % 2:
            indent = self.size_hex_IMG // 2

        y = (self.window_border_Y) + (row_height * self.size_hex_IMG) + self.move_window_Y
        x = (self.window_border_X) + ((some_hex.hex_coordinate_index % self.hex_map_length) * self.size_hex_IMG) + indent - (self.size_hex_IMG // 2) + self.move_window_X
        #check if hex in render space
        if x < LENGTH + self.size_hex_IMG and y < WIDTH + self.size_hex_IMG and x > -self.size_hex_IMG and y > -self.size_hex_IMG:
            self.game_screen.blit(self.animated_hexes_IMG['gridHex'], (x, y))
            #check if empty for move
            if some_hex.empty:
                if self.ship_selected:
                    some_ship = self.selected_hex.entity
                    if some_hex in self.selected_hex.neighbors and some_ship.ship_moves != 0 and (
                        some_hex.directions[some_ship.orientation] != self.selected_hex.hex_coordinate_index or some_ship.ship_type == 'DD' or some_ship.ship_type == 'CS'):
                        if not (some_ship.ship_type == 'BB' and self.ops_hex_map.space_hexes[some_hex.directions[some_ship.orientation]] in self.selected_hex.neighbors):
                            self.game_screen.blit(self.animated_hexes_IMG['moveHex'], (x, y))

            #check if ship
            elif some_hex.entity.entity_type == 'ship_entity':
                if self.active_fleet_command[0:3] != some_hex.entity.command[0:3] and some_hex.entity.detected:
                    self.game_screen.blit(self.animated_hexes_IMG['enemyHex'], (x, y))
                elif self.active_fleet_command[0:3] == some_hex.entity.command[0:3]:
                    self.game_screen.blit(self.animated_hexes_IMG['allyHex'], (x, y))

                if some_hex.entity.command == 'ASCS' and some_hex.entity.detected:
                    self.rotation_orientation(some_hex.entity)
                    self.game_screen.blit(self.ROT_ASCS_SHIP_HEX_IMG, (x, y))
                elif some_hex.entity.command == 'XNFFS' and some_hex.entity.detected:
                    self.rotation_orientation(some_hex.entity)
                    self.game_screen.blit(self.ROT_XNFF_SHIP_HEX_IMG, (x, y))

                #check if target in range
                if self.ship_selected:
                    if some_hex in self.targets_hexes:
                        self.game_screen.blit(self.animated_hexes_IMG['targetHex'], (x, y))
        
                #clicked
                if self.ship_selected:
                    if some_hex.hex_coordinate_index == self.selected_hex.hex_coordinate_index:
                        self.game_screen.blit(self.animated_hexes_IMG['clickHex'], (x, y))
        

    #get hexNums from coord mouse
    def get_mouse_hex(self, mouse_position):
        i = 0
        a, b = mouse_position
        a_position_active = False
        b_position_active = False 
        column, row = 0, 0

        if b in range(self.window_border_Y + self.move_window_Y, (self.size_hex_IMG * self.hex_map_width) + (self.window_border_Y) + self.move_window_Y):
            b_position_active = True
            #reverse y coords
            row = abs(((b - (self.window_border_Y + self.move_window_Y)) // self.size_hex_IMG) - self.hex_map_width) - 1
            #check even/odd rows
            if ((b - (self.window_border_Y + self.move_window_Y)) // self.size_hex_IMG) % 2 == (self.hex_map_width + 1) % 2:
                i = self.size_hex_IMG // 2  

        if a in range((self.window_border_X) - i + self.move_window_X, ((self.size_hex_IMG * self.hex_map_length) + (self.window_border_X) - i) + self.move_window_X):
            a_position_active = True
            column = ((a - (self.window_border_X + self.move_window_X)) + i) // self.size_hex_IMG

        if a_position_active and b_position_active:
            mouse_hex_coordinate_index = (row * self.hex_map_length) + column
            return mouse_hex_coordinate_index
        else:
            print("No Hexes In this space")
            return -1

    #WIP zoom in
    def zoom_in_window(self):
        self.size_hex_IMG += 16
        self._scale_hexes(self.size_hex_IMG)

    #WIP zoom out
    def zoom_out_window(self):
        self.size_hex_IMG -= 16
        self._scale_hexes(self.size_hex_IMG)

    #rotate an image based on ship orientation
    def rotation_orientation(self, some_ship):
        orients = {'R': -90.0, 'L': -270.0, 'UR': -30.0, 'UL': -330.0, 'DR': -150.0, 'DL': -210.0}
        self._scale_hexes(self.size_hex_IMG)
        if some_ship.command == 'ASCS':
            self.ROT_ASCS_SHIP_HEX_IMG = self._rotate_center(self.ASCS_SHIP_HEX_IMG, orients[some_ship.orientation]) 
        elif some_ship.command == 'XNFFS':
            self.ROT_XNFF_SHIP_HEX_IMG = self._rotate_center(self.XNFF_SHIP_HEX_IMG, orients[some_ship.orientation])

    #rotate an image with pivot center
    def _rotate_center(self, some_image, some_angle):
        original_rectangle = some_image.get_rect()
        rotated_image = pygame.transform.rotate(some_image, some_angle)
        rotated_rectangle = original_rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image

    def animate_hexes(self):
        animation_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11, 10, 9 ,8, 7, 6, 5, 4, 3, 2, 1, 0]
        w = self.counter_animation_1 
        
        for temporary_hexes, animated_hex_keys in zip(self.template_hexes_IMG.values(), self.animated_hexes_IMG.keys()):
            base_hex_image = self.base_hex_IMG.copy()
            new_animated_hex = temporary_hexes.copy()
            base_hex_image.blit(new_animated_hex, (0, animation_order[w]))
            new_animated_image = pygame.transform.scale(base_hex_image, (self.size_hex_IMG, self.size_hex_IMG))
            self.animated_hexes_IMG[animated_hex_keys] = new_animated_image
        
        if self.counter_animation_1 == 23:
            self.counter_animation_1 = 0
        else:
            self.counter_animation_1 += 1
       
    #scale the hexes
    def _scale_hexes(self, size_hex_IMG):
        self.ASCS_SHIP_HEX_IMG.convert()
        self.EMPTY_HEX_IMG.convert()
        self.XNFF_SHIP_HEX_IMG.convert()
        self.EMPTY_HEX_IMG = pygame.transform.smoothscale(EMPTY_HEX_IMG, (size_hex_IMG, size_hex_IMG))
        self.ASCS_SHIP_HEX_IMG = pygame.transform.smoothscale(ASCS_SHIP_HEX_IMG, (size_hex_IMG, size_hex_IMG))
        self.XNFF_SHIP_HEX_IMG = pygame.transform.smoothscale(XNFF_SHIP_HEX_IMG, (size_hex_IMG, size_hex_IMG))
