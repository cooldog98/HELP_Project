import pygame
from object import Object
from os import walk
from os.path import join


class enemy(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(self, x, y, width, height, 'enemy')
        self.enemy = self.load_image()

    def load_image(self):
        self.frames = {'bullet_2': [], 'enemy': [], 'enemy_2': [], 'enemy_h': [], 'enemy_hit': [],
                       'enemy_run': [], 'enemy_shoot_2': []}
        self.frame_paths = {state: [] for state in self.frames.keys()}
        # new_size = (self.rect.width * 2, self.rect.height * 2)
        new_size = (self.rect.width, self.rect.height)
        for state in self.frames.keys():
            for folder_path, sub_folder, file_names in walk(join('enemy', 'enemy_1', state)):
                if file_names:
                    """skip .DS_Store or another file that nor be .png"""
                    file_names = [f for f in file_names if f.endswith('.png')]
                    """sort file"""
                    file_names.sort(key=lambda x: int(x.split('.')[0]))
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        self.frame_paths[state].append(full_path)
                        original_surf = pygame.image.load(full_path).convert_alpha()
                        surf = pygame.transform.scale(original_surf, new_size)
                        self.frames[state].append(surf)
        print(self.frames)

    def reload_frames(self, flipped=False):
        frames = {state: [] for state in self.frame_paths.keys()}
        # new_size = (self.rect.width * 2, self.rect.height* 2)
        new_size = (self.rect.width, self.rect.height)

        for state, paths in self.frame_paths.items():
            for path in paths:
                surf = pygame.image.load(path).convert_alpha()
                surf = pygame.transform.scale(surf, new_size)
                if flipped:
                    surf = pygame.transform.flip(surf, True, False)
                    """pygame.transform.flip(surf, True, False) mean flip picture from left to right"""
                frames[state].append(surf)

        return frames

    def animate(self, dt):
        """get_state"""
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_a] or keys[pygame.K_d]:
        if self.x_vel != 0:
            self.state = 'run'
        elif self.y_vel != 0:
            if self.jump_count == 1 or self.jump_count == 2:
                self.state = 'jump'
        # elif self.y_vel > self.gravity * 2:
        #     self.state = 'player'
            # elif self.jump_count == 2:
            #     self.state = 'jump_2'
        else:
            self.state = 'player'
        """animate"""
        speed_factor = max(abs(self.x_vel) / 10, 1)
        self.frames_index += 7 * dt
        self.image = self.frames[self.state][int(self.frames_index) % len(self.frames[self.state])]
