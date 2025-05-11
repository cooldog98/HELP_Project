import pygame
from os import walk
from os.path import isfile, join
from bullet import Bullet
# from game import Game


class Player(pygame.sprite.Sprite):
    color = (255, 0, 0)
    gravity = 0.38
    # SPRITES = load_sprite_sheets('graphic', 'animation', 210, 266, True)
    '''dir1 , dir2 is dir that picture stay with width and height is size of picture thant
    use to cut if fix incorrect size the picture will have another picture than beside wit, then ture is
    make right and left direction'''
    animation_delay = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        """The top-left corner of the screen is (0, 0)."""
        """The x-axis increases from left to right."""
        """The y-axis increases from top to bottom."""
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.make = None
        self.direction = 'left'
        # self.ani_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.count = 0
        # self.animation_timer = 0

        self.load_image()
        self.state, self.frames_index = 'player_use', 0
        self.image = self.frames[self.state][0]

        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0

        self.hp = 100

        self.shooting = False
        self.shoot_frame = 7

        self.is_landed = False
        self.time_start = 0
        self.time_elapsed = 0
        self.timer_running = False
        # self.game = Game()
        self.font = pygame.font.SysFont('Arial', 30)
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        # self.y_vel = -self.gravity * 8
        self.ani_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.y_vel = -self.gravity * 8
            self.fall_count = 0
        elif self.jump_count == 2:
            self.y_vel = -self.gravity * 10
            self.fall_count = 0

    def move(self, dx, dy):
        """move dx(left right) dy(up down)"""
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        """because The top-left corner of the screen is (0, 0).
        if, want to go left vel need to be negative."""
        self.x_vel = -vel
        """check def work or not"""
        if self.direction != 'left':
            self.direction = 'left'
            current_index = self.frames_index
            self.frames = self.reload_frames(flipped=True)
            self.frames_index = current_index
            self.ani_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            current_index = self.frames_index
            self.frames = self.reload_frames(flipped=False)
            self.frames_index = current_index
            self.ani_count = 0

    def loop(self, fps, dt):
        self.y_vel += min(2, (self.fall_count / fps) * self.gravity)
        self.fall_count += 1

    def draw_player(self, screen, offset_x):
        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))

    def stop(self):
        self.x_vel = 0

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

    def load_image(self):
        self.frames = {'dying': [], 'hurt_use': [], 'jump_use': [], 'jump_2': [], 'player_use': [], 'run_use': [],
                       'shoot_use': []}
        self.frame_paths = {state: [] for state in self.frames.keys()}
        # new_size = (self.rect.width * 2, self.rect.height * 2)
        new_size = (self.rect.width, self.rect.height)
        for state in self.frames.keys():
            for folder_path, sub_folder, file_names in walk(join('graphic', 'animation', state)):
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

    def get_bullet_spawn_pos(self):
        """Calculate consistent bullet spawn position for both shooting methods"""
        if self.direction == 'right':
            # Spawn at right side + small offset
            bullet_x = self.rect.right + 10
            bullet_y = self.rect.centery - 15  # Adjust to match gun height
        else:
            # Spawn at left side - small offset
            bullet_x = self.rect.left - 10
            bullet_y = self.rect.centery - 15  # Same vertical adjustment

        return bullet_x, bullet_y

    def animate(self, dt):
        # Get state
        if self.shooting:
            self.state = 'shoot_use'
        elif self.x_vel != 0:
            self.state = 'run_use'
        elif self.y_vel != 0:
            if self.jump_count >= 1:
                self.state = 'jump_use'
        elif self.x_vel == 0:
            self.state = 'player_use'

        # Track animation frame
        prev_frame = int(self.frames_index)
        self.frames_index += 7 * dt
        current_frame = int(self.frames_index)

        # Handle shooting animation
        if self.shooting:
            # Spawn bullet at specific frame (frame 7)
            if (prev_frame < self.shoot_frame <= current_frame and
                    not self.shot_this_animation and
                    self.shoot_cooldown == 0):
                bullet_x, bullet_y = self.get_bullet_spawn_pos()
                bullet = Bullet(bullet_x, bullet_y - 50, self.direction)
                self.bullets.add(bullet)
                self.shoot_cooldown = 15
                self.shot_this_animation = True

            # Reset shooting state when animation completes
            if current_frame >= len(self.frames[self.state]) - 1:
                self.shooting = False
                self.shot_this_animation = False

        self.image = self.frames[self.state][int(self.frames_index) % len(self.frames[self.state])]

    def landed(self):
        self.fall_count = 0
        # self.y_vel = 0
        self.jump_count = 0
        """Player lands on the ground."""
        self.y_vel = 0
        self.is_landed = True
        if not self.timer_running:
            # Start the timer when the player lands
            self.time_start = pygame.time.get_ticks()
            self.timer_running = True

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def shoot(self):
        # Only allow shooting when not jumping and not already shooting
        if self.shoot_cooldown == 0 and self.jump_count == 0 and not self.shooting:
            self.shooting = True
            self.frames_index = 0  # Reset animation
            self.shot_this_animation = False

            # Use the same position calculation as in animate()
            bullet_x, bullet_y = self.get_bullet_spawn_pos()
            bullet = Bullet(bullet_x, bullet_y, self.direction)
            self.bullets.add(bullet)
            self.shoot_cooldown = 15

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def health_player(self, damage):
        self.hp -= damage
        self.state = 'hurt_use'

    def render(self, screen):
        screen.blit(self.image, self.rect)
