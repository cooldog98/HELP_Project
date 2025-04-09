import sys
import os
import pygame
from os import walk
from os import listdir
from os.path import isfile, join
import copy

# from player import Player
# from game_platform import Platform
# from object import Object
# from block import Block
# from gun import Bullet


# img = pygame.image.load("graphic/animation/player_use.png")


"""start pygame"""
pygame.init()

"""change name in windows pygame"""
pygame.display.set_caption('PLATFORMER GAME: HELP')

"""set the screen size (w, h)"""
screen = pygame.display.set_mode((1000, 800))


class Player(pygame.sprite.Sprite):
    color = (255, 0, 0)
    gravity = 0.4
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
        self.state, self.frames_index = 'run', 0
        self.image = self.frames[self.state][0]

        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0

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

    # def _gravity(self, fps):
    #     self.y_vel += min(2, (self.fall_count / fps) * self.gravity)
    #     self.fall_count += 1

    def loop(self, fps):
        self.y_vel += min(2, (self.fall_count / fps) * self.gravity)
        self.fall_count += 1
        # self._gravity(fps)
        self.move(self.x_vel, self.y_vel)

        # self.fall_count += 1
        # self.update_sprite()
        # if self.animation_timer >= self.animation_delay:
        #     self.update_sprite()
        #     self.animation_timer = 0
        # self.animation_timer += 1

    def draw_player(self, screen, offset_x):
        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        # self.sprite = self.SPRITES['run_use_' + self.direction][0]
        # if self.sprite:
        #     screen.blit(self.sprite, (self.rect.x, self.rect.y))
        # pygame.draw.rect(screen, self.color, self.rect)

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
        self.frames = {'dying': [], 'hit': [], 'jump': [], 'jump_2': [], 'player': [], 'run': [], 'shoot': []}
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

    def animate(self, dt):
        """get_state"""
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

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def die(self):
        self.rect.y = 100
        self.y_vel = 0
        self.x_vel = 0

    def shoot(self):
        if self.shoot_cooldown == 0:
            # Better bullet spawn position (from player's gun)
            if self.direction == 'right':
                bullet_x = self.rect.right + 10
            else:
                bullet_x = self.rect.left - 10
            bullet_y = self.rect.centery  # Adjust to gun position

            bullet = Bullet(bullet_x, bullet_y, self.direction)
            self.bullets.add(bullet)
            self.shoot_cooldown = 15  # Cooldown frames

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


class Platform:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_background(self, name):
        path = os.path.join('graphic', name)  # Join the file path correctly
        """os.path.join('assets', 'Background', 'back_G_help.jpg') assets โฟร์เ้อใหญ่สุดที่ ไฟล์รูปภาพเก็บไว้
        Background โฟเด้อรองลงมา back_G_help.jpg ไฟล์รูปภาพ or 'graphic', name: graphic is bigger folder that
         keep file picture, name is file picture """
        image = pygame.image.load(path)
        __, __, width_image, height_image = image.get_rect()
        tiles = []

        for i in range(self.width // width_image + 1):
            for j in range(self.height//height_image + 1):
                pos = [i * width_image, j * height_image]
                tiles.append(pos)

        return tiles, image

    def draw(self, screen_, background, bg_image, player, objects, offset_x):
        for tile in background:
            screen_.blit(bg_image, tuple(tile))

        for obj in objects:
            obj.draw(screen_, offset_x)

        player.draw_player(screen_, offset_x)


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, _screen, offset_x):
        _screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = self.get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

    def get_block(self, size):
        path = join('graphic', 'walland green.jpg')
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(0, 0, size, size)
        surface.blit(image, (0, 0), rect)
        return pygame.transform.scale(surface, (size, size))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=15):
        super().__init__()
        # Make bullet more visible
        self.image = pygame.Surface((20, 5))  # Wider bullet
        self.image.fill(((0, 255, 255)))  # Bright yellow color
        pygame.draw.rect(self.image, (255, 0, 0), self.image.get_rect(), 1)  # Red border
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.direction = direction
        self.lifetime = 90  # Longer lifetime
        self.true_x = x  # Store absolute position for scrolling

    def update(self, offset_x=0):
        # Move bullet
        if self.direction == 'right':
            self.true_x += self.speed
        else:
            self.true_x -= self.speed

        # Update position with camera offset
        self.rect.x = self.true_x - offset_x

        # Remove old bullets
        # self.lifetime -= 1
        # if self.lifetime <= 0:
        #     self.kill()

class Game:
    block_size = 50
    width = 1000
    height = 800
    player_pos_x = block_size * (-17)
    player_pos_y = 790

    def __init__(self):
        # self.all_sprites = pygame.sprite.Group()
        self.player = Player(self.player_pos_x, self.player_pos_y, 60, 60)
        self.platform = Platform(self.width, self.height)
        # self.block = [Block(0, self.height - self.block_size, self.block_size)]
        self.floor = [Block(i * self.block_size, self.height - self.block_size, self.block_size)
                      for i in range(-self.width // self.block_size, (self.width * 2) // self.block_size)]
        self.wall_left = [Block(- self.width, i * self.block_size, self.block_size)
                     for i in range(-self.height // self.block_size, (self.height * 2) // self.block_size)]
        self.wall_right = [Block(self.width * 2, i * self.block_size, self.block_size)
                          for i in range(-self.height // self.block_size, (self.height * 2) // self.block_size)]

        self.offset_x = -(-self.player.rect.x + self.width // 2 - self.player.rect.width // 2)

        self.scroll_area_width = 200
        self.scroll_speed = 10
        self.all_sprites = pygame.sprite.Group(self.player)
        # self.gun = Gun(self.player, self.all_sprites)
        self.objs = [*self.floor,
                     *self.wall_left,
                     *self.wall_right,
                     Block(0, self.height - self.block_size * 2, self.block_size),
                     Block(self.block_size, self.height - self.block_size * 2, self.block_size),
                     Block(self.block_size * (-1), self.height - self.block_size * 2, self.block_size),

                     Block(self.block_size * 3, self.height - self.block_size * 4, self.block_size),
                     Block(self.block_size * 4, self.height - self.block_size * 4, self.block_size),
                     Block(self.block_size * 5, self.height - self.block_size * 4, self.block_size),
                     Block(self.block_size * 6, self.height - self.block_size * 5, self.block_size),
                     Block(self.block_size * 7, self.height - self.block_size * 5, self.block_size),

                     Block(self.block_size * 8, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 9, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 10, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 11, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 12, self.height - self.block_size * 9, self.block_size),

                     Block(self.block_size * 18, self.height - self.block_size * 5, self.block_size),
                     Block(self.block_size * 19, self.height - self.block_size * 5, self.block_size),
                     Block(self.block_size * 20, self.height - self.block_size * 5, self.block_size),
                     Block(self.block_size * 21, self.height - self.block_size * 5, self.block_size),
                     Block(self.block_size * 22, self.height - self.block_size * 5, self.block_size),

                     Block(self.block_size * 23, self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * 24, self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * 25, self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * 26, self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * 27, self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * 28, self.height - self.block_size * 7, self.block_size),

                     Block(self.block_size * 32, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 33, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 34, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 35, self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * 36, self.height - self.block_size * 9, self.block_size),

                     Block(self.block_size * 38, self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * 39, self.height - self.block_size * 7, self.block_size),

                     Block(self.block_size * (-4), self.height - self.block_size * 5, self.block_size),
                     Block(self.block_size * (-5), self.height - self.block_size * 5, self.block_size),
                     Block(self.block_size * (-6), self.height - self.block_size * 5, self.block_size),

                     Block(self.block_size * (-17), self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * (-18), self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * (-19), self.height - self.block_size * 11, self.block_size),

                     Block(self.block_size * (-7), self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * (-6), self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * (-5), self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * (-4), self.height - self.block_size * 11, self.block_size),

                     Block(self.block_size * 15, self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * 16, self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * 17, self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * 18, self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * 19, self.height - self.block_size * 11, self.block_size),
                     Block(self.block_size * 20, self.height - self.block_size * 11, self.block_size),

                     Block(self.block_size * (-8), self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * (-9), self.height - self.block_size * 7, self.block_size),
                     Block(self.block_size * (-10), self.height - self.block_size * 7, self.block_size),

                     Block(self.block_size * (-16), self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * (-15), self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * (-14), self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * (-13), self.height - self.block_size * 9, self.block_size),
                     Block(self.block_size * (-12), self.height - self.block_size * 9, self.block_size),

                     Block(0, self.height - self.block_size * 8, self.block_size),
                     Block(self.block_size, self.height - self.block_size * 8, self.block_size),
                     Block(self.block_size * 2, self.height - self.block_size * 8, self.block_size),
                     Block(self.block_size * 3, self.height - self.block_size * 8, self.block_size),]
        # self.block_size * (-19) before end map left

    def handle_check_collision(self, player, objects, dy):
        collided_object = []
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                if player.y_vel > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                if player.y_vel < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()

                # if player.x_vel > 0:
                #     player.rect.right = obj.rect.left
                # elif player.x_vel < 0:
                #     player.rect.left = obj.rect.right
            collided_object.append(obj)
        return collided_object

    def collide(self, player, objects, dx):
        player.move(dx, 0)
        player.update()
        collided_obj = None
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                collided_obj = obj
                break

        player.move(-dx, 0)
        player.update()
        return collided_obj

    def check_collision_(self, player: Player, objects):
        key = pygame.key.get_pressed()
        player_vel = 10
        collide_left = self.collide(player, objects, -player_vel * 2)
        collide_right = self.collide(player, objects, player_vel * 2)
        # if not key[pygame.K_a] and key[pygame.K_d]:
        #     player.x_vel = 0

        if key[pygame.K_a] and not collide_left:
            player.move_left(player_vel)
        elif key[pygame.K_d] and not collide_right:
            player.move_right(player_vel)
        else:
            """if not pressed any key the Player stop"""
            player.x_vel = 0

        self.handle_check_collision(player, objects, player.y_vel)

    def start_game(self):
        # platform = Platform()
        """set the frame rate"""
        self.clock = pygame.time.Clock()
        self.background, self.bg_image = self.platform.get_background('black_imresizer.jpg')
        self.update()

    def check_bullet_collisions(self):
        # Check bullet collisions with blocks
        for bullet in self.player.bullets:
            for block in self.objs:
                if pygame.sprite.collide_rect(bullet, block):
                    print(f"Bullet hit block at {block.rect}")
                    bullet.kill()
                    break  # Stop checking other blocks for this bullet

    def update(self):
        """Main game loop"""
        while True:
            """Convert to seconds"""
            dt = self.clock.tick(60) / 1000
            """pygame.event.get() เรียกใช้ในทุก frames ป้องการการค้าง"""
            """1. When the player presses a key, clicks the mouse, or closes the window → Pygame creates an event.
            2. These events are stored in the event queue (a list).
            3. pygame.event.get() takes all the events from the queue and allows you to handle them one by one."""
            for event in pygame.event.get():
                """ .type only works with objects created from pygame.event.get()"""
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                """stop movement when not pressed any key"""
                """KEYUP == release the key
                KEYDOWN == press a key"""
                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_a, pygame.K_d]:
                        self.player.stop()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.player.jump_count < 2:
                        self.player.jump()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.player.shoot()

            # self.player.update()
            # self.player.bullets.update(self.offset_x)
            # self.player.bullets.draw(screen)

            # self.all_sprites.update()
            # self.player.bullets.update()

            # screen.fill((0, 0, 0))
            # self.all_sprites.draw(screen)
            # self.player.bullets.update(self.offset_x)
            # self.player.bullets.draw(screen)
            # pygame.display.flip()

            self.player.loop(60)
            self.player.animate(dt)
            self.player.bullets.update(self.offset_x)
            self.check_collision_(self.player, self.objs)
            self.check_bullet_collisions()
            self.platform.draw(screen, self.background, self.bg_image, self.player, self.objs, self.offset_x)
            self.player.bullets.draw(screen)
            # self.platform.draw(screen, self.background, self.bg_image, self.player, self.objs, self.offset_x)

            if (self.player.rect.right - self.offset_x >= self.width - self.scroll_area_width
                    and self.player.x_vel > 0) or (self.player.rect.left - self.offset_x <= self.scroll_area_width
                                                   and self.player.x_vel < 0):
                self.offset_x += self.player.x_vel
                """dt * 60 beacues เพราะ dt = 1/60 ใน fps 60
                จะได้ความเร็วปกติเท่ากับค่าเดิม (x_vel = 10)"""

            if self.player.rect.top > self.height:
                self.player.die()
                print('game over')
                exit()

            # self.check_bullet_collisions(self.player.bullets, self.objs)

            pygame.display.update()
            """setup frames per second be 60"""
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.start_game()
