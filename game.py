import sys
import pygame
import pytmx
# import json
import time
import csv
import os


from player import Player
from game_platform import Platform
from health import HealthBar
from enemy import Enemy_1


"""start pygame"""
pygame.init()

"""change name in windows pygame"""
pygame.display.set_caption('PLATFORMER GAME: HELP')

"""set the screen size (w, h)"""
screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()


class TiledObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(255, 0, 0), name=None):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)  # Set the color of the object
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name  # Add a name attribute


class Game:
    block_size = 50
    width = 1000
    height = 800
    player_pos_x = block_size * (-17)
    player_pos_y = 790

    def __init__(self, player_name):
        self.player_name = player_name
        # self.player = Player(-950, self.height - self.block_size * 2, 60, 60)
        self.player = Player(100, self.height - self.block_size * 2, 60, 60)

        self.level = 1
        self.max_level = 3

        # self.enemies = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.spawn_enemies_by_level()

        # self.enemies.add(Enemy_1(700, self.height - self.block_size * 1.6, 50, 50),
        #                  Enemy_1(100, self.height - (self.block_size * 9), 50, 50),
        #                  Enemy_1(900, self.height - (self.block_size * 9.3), 50, 50),
        #                  Enemy_1(200, self.height - (self.block_size * 13.8), 50, 50))

        self.platform = Platform(self.width, self.height)

        self.offset_x = -(-self.player.rect.x + self.width // 2 - self.player.rect.width // 2)

        self.scroll_area_width = 200
        self.scroll_speed = 10
        self.objs = pygame.sprite.Group()

        # self.tmx_data, self.map_sprites = self.load_map('map_level1.tmx', screen)
        self.tmx_data, self.map_sprites = self.load_map(screen)
        self.objs.add(self.map_sprites)

        self.health_bar = HealthBar(5, 40, 300, 15, 100)
        # damage that player hit enemy
        self.damage = 10

        self.enemies_defeated = 0
        # self.health_lost = 0

        self.font = pygame.font.SysFont('Arial', 24)

        self.get_key = False

        self.start_time = None
        self.end_time = None
        self.time_recorded = False  # เพื่อป้องกันบันทึกซ้ำ

        self.distance = 0
        self.last_position = self.player.rect.x
        self.distance_log = []
        self.enemy_kill = []
        self.total_enemy = 0
        self.distance_timer = 0

    def spawn_enemies_by_level(self):
        self.enemies.empty()  # remove old enemies

        if self.level == 1:
            self.enemies.add(
                Enemy_1(700, self.height - self.block_size * 1.6, 50, 50),
                Enemy_1(90, self.height - (self.block_size * 7.5), 50, 50),
                Enemy_1(900, self.height - (self.block_size * 9.3), 50, 50),
                Enemy_1(500, self.height - (self.block_size * 6.2), 50, 50),
                Enemy_1(700, self.height - (self.block_size * 11.3), 50, 50)
            )
        elif self.level == 2:
            self.enemies.add(
                Enemy_1(400, self.height - self.block_size * 2.7, 50, 50),
                Enemy_1(200, self.height - self.block_size * 7.4, 50, 50),
                Enemy_1(900, self.height - self.block_size * 13.1, 50, 50),
                Enemy_1(400, self.height - self.block_size * 10.6, 50, 50),
                Enemy_1(900, self.height - self.block_size * 7.4, 50, 50),
                Enemy_1(100, self.height - self.block_size * 13.1, 50, 50)
            )
        elif self.level == 3:
            self.enemies.add(
                Enemy_1(150, self.height - self.block_size * 1.6, 50, 50),
                Enemy_1(350, self.height - self.block_size * 6, 50, 50),
                Enemy_1(890, self.height - self.block_size * 9.2, 50, 50),
                Enemy_1(900, self.height - self.block_size * 3.8, 50, 50),
                Enemy_1(200, self.height - self.block_size * 13.2, 50, 50),
                Enemy_1(300, self.height - self.block_size * 8, 50, 50),
                Enemy_1(500, self.height - self.block_size * 11.2, 50, 50)
            )

    def draw_player_name(self):
        """show name of player"""
        name_surface = self.font.render(f"Player: {self.player_name}", True, (255, 255, 255))
        screen.blit(name_surface, (5, 5))

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer_and_save(self, player_name):
        if not self.time_recorded and self.start_time is not None:
            self.end_time = time.time()
            elapsed_time = round(self.end_time - self.start_time, 2)
            self.save_data(player_name, elapsed_time)
            self.time_recorded = True
            self.player.timer_running = False

    def save_data(self, player_name, elapsed_time):
        filename = "data_record.csv"
        file_exists = os.path.isfile(filename)

        # Prepare the data for this level
        level_key = f"level_{self.level}"
        row = {
            "Player Name": player_name,
            "Level": self.level,
            "Time (s)": elapsed_time,
            "Enemies Defeated": self.enemies_defeated,
            "HP": self.player.hp,
            "Distance": round(self.distance, 2)
        }

        # Write to CSV
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ["Player Name", "Level", "Time (s)", "Enemies Defeated", "HP", "Distance"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if file didn't exist
            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

    def render_time(self):
        """Render the time on the screen."""
        if self.player.timer_running:
            time_text = f"Time: {(pygame.time.get_ticks() - self.player.time_start) / 1000:.2f} s"
        else:
            time_text = f"Time: {self.player.time_elapsed / 1000:.2f} s"
            print(f'Time: {self.player.time_elapsed / 1000:.2f} s')

        # Render the time text
        time_surface = self.font.render(time_text, True, (255, 255, 255))  # White color text
        screen.blit(time_surface, (5, 55))  # Position it at (10, 10) on the screen

    def move_and_check_collision(self, player, objects, dt):
        # Move and check X axis
        move_x = player.x_vel * dt * 60
        player.rect.x += move_x
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                if player.x_vel > 1:
                    player.rect.right = obj.rect.left
                    player.x_vel = 0
                elif player.x_vel < 0:
                    player.rect.left = obj.rect.right
                    player.x_vel = 0
                player.x_vel = 0

        # Move and check Y axis
        move_y = player.y_vel * dt * 60
        player.rect.y += move_y
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                if player.y_vel > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                elif player.y_vel < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()
                player.y_vel = 0
        self.player.update()

    def handle_check_collision_x(self, player, objects):
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                if player.x_vel > 0:  # Moving right
                    player.rect.right = obj.rect.left
                elif player.x_vel < 0:  # Moving left
                    player.rect.left = obj.rect.right
                player.x_vel = 0
        self.player.update()

    def check_for_key_collision(self):
        """Final robust key collision check"""
        if self.get_key:  # Already collected
            return

        # Find all keys in the scene
        key_objects = [obj for obj in self.objs if hasattr(obj, 'name') and obj.name == "key"]

        if not key_objects:
            print("No keys found in scene!")
            return

        for key_obj in key_objects:

            # Check both simple and mask collision
            simple_collision = self.player.rect.colliderect(key_obj.rect)
            mask_collision = pygame.sprite.collide_mask(self.player, key_obj)

            if mask_collision or simple_collision:
                self.get_key = True
                key_obj.kill()  # Remove the key
                print("SUCCESS: Key collected!")
                # self.stop_timer_and_save()
                return

        # print("Player near key but no collision detected")

    def handle_check_collision_y(self, player, objects):
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                if player.y_vel > 0:  # Falling
                    player.rect.bottom = obj.rect.top
                    player.landed()
                elif player.y_vel < 0:  # Jumping
                    player.rect.top = obj.rect.bottom
                    player.hit_head()
                player.y_vel = 0
        self.player.update()

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

    def start_game(self):
        # platform = Platform()
        """set the frame rate"""
        self.get_key = False
        self.start_timer()
        self.clock = pygame.time.Clock()
        # self.background, self.bg_image = self.platform.get_background('black_imresizer.jpg')
        self.update()

    def check_bullet_collisions(self):
        # Check bullet collisions with blocks
        for bullet in self.player.bullets:
            for block in self.objs:
                if pygame.sprite.collide_mask(bullet, block):
                    # print(f"Bullet hit block at {block.rect}")
                    bullet.kill()
                    # Stop checking other blocks for this bullet
                    break

            for enemy in self.enemies:
                if pygame.sprite.collide_rect(bullet, enemy):
                    enemy.get_attack = True
                    # enemy.state = 'hurt'
                    # print(f"Bullet hit enemy at {enemy.rect}")
                    bullet.kill()
                    enemy.health(self.damage)
                    # enemy.get_attack = False
                    if enemy.hp <= 0:
                        enemy.kill()
                        self.enemies_defeated += 1
                        self.enemy_kill.append(self.enemies_defeated)
                        self.total_enemy = sum(self.enemy_kill)

                    # print(enemy.hp)

    def load_map(self, screen):
        map_file = f"map_level{self.level}.tmx"  # dynamically load map
        # tmx_data = pytmx.load_pygame(map_file)
        tmx_data = pytmx.load_pygame(map_file)
        all_sprites = pygame.sprite.Group()

        # Draw the Tile Layer
        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

        # Convert Object Layer to sprites - FIXED NAMING
        for obj in tmx_data.objects:
            if obj.name == "box":
                object_sprite = TiledObject(obj.x, obj.y, obj.width, obj.height, (255, 0, 0), name="box")  # Red box
                all_sprites.add(object_sprite)
            elif obj.name == 'key':
                object_sprite = TiledObject(obj.x, obj.y, obj.width, obj.height, (255, 255, 0),
                                            name="key")  # Yellow key
                all_sprites.add(object_sprite)

        return tmx_data, all_sprites

    def load_next_level(self):
        if self.level < self.max_level:
            self.level += 1
            self.spawn_enemies_by_level()
            self.get_key = False
            self.start_timer()  # reset timer for new level
            self.tmx_data, self.map_sprites = self.load_map(screen)
            self.objs.empty()
            self.objs.add(self.map_sprites)
            self.player.rect.x = 100  # Reset player position
            self.player.rect.y = self.height - self.block_size * 2
            self.time_recorded = False

            self.distance = 0
            self.distance_log = []
            self.enemies_defeated = 0  # ถ้ามีระบบนี้ใน Player

        else:
            print("All levels completed!")
            pygame.quit()
            sys.exit()

    def update_distance_log(self, dt):
        self.distance_timer += dt
        distance_delta = abs(self.player.rect.x - self.last_position)
        self.distance += distance_delta
        self.last_position = self.player.rect.x

        if self.distance_timer >= 10:  # log ทุก 10 วินาที
            self.distance_log.append(round(self.distance, 2))
            self.distance_timer = 0

    def update(self):
        # tmx_data = self.load_map('map_lavel1.tmx', screen)
        """Main game loop"""
        while True:
            screen.fill((0, 0, 0))
            # screen.blit(self.background, self.camera.apply_offset(self.background))
            # screen.blit(self.player.image, self.camera.apply(self.player))
            # self.load_map('map_lavel1.tmx', screen)
            self.load_map(screen)
            self.player.render(screen)
            # self.camera.update(self.player)
            """Convert to seconds"""
            dt = self.clock.tick(60) / 1000
            """distance"""
            self.update_distance_log(dt)
            """pygame.event.get() เรียกใช้ในทุก frames ป้องการการค้าง"""
            """1. When the player presses a key, clicks the mouse, or closes the window → Pygame creates an event.
            2. These events are stored in the event queue (a list).
            3. pygame.event.get() takes all the events from the queue and allows you to handle them one by one."""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_SPACE and self.player.jump_count < 2:
                        self.player.jump()

                    if event.key == pygame.K_RETURN:
                        self.player.shoot()

            # Check keys every frame
            keys = pygame.key.get_pressed()
            player_speed = 10

            if keys[pygame.K_a]:
                self.player.move_left(player_speed)
            elif keys[pygame.K_d]:
                self.player.move_right(player_speed)
            else:
                self.player.stop()

            self.player.loop(60, dt)
            self.player.update()
            for enemy in self.enemies:
                # enemy.offset_x = self.offset_x
                enemy.update_enemy(self.player)
                enemy.render(screen)

            self.player.bullets.update(dt)
            self.check_bullet_collisions()
            self.move_and_check_collision(self.player, self.objs, dt)

            self.player.animate(dt)
            self.check_bullet_collisions()
            # self.platform.draw(screen, self.background, self.bg_image, self.player, self.objs, self.offset_x)
            self.player.bullets.draw(screen)

            for enemy in self.enemies:
                # enemy.draw_enemy(screen, self.offset_x)
                enemy.render(screen)

            self.check_for_key_collision()

            """health bar"""
            self.health_bar.hp = self.player.hp
            self.health_bar.draw(screen)
            """draw name of player"""
            self.draw_player_name()
            """draw time"""
            self.render_time()

            if self.health_bar.hp <= 0:
                print('Player Dying')
                pygame.quit()
                sys.exit()

            if (self.player.rect.right - self.offset_x >= self.width - self.scroll_area_width
                and self.player.x_vel > 0) or (self.player.rect.left - self.offset_x <= self.scroll_area_width
                                               and self.player.x_vel < 0):
                self.offset_x += self.player.x_vel * dt * 60
                """dt * 60 beacues เพราะ dt = 1/60 ใน fps 60
                จะได้ความเร็วปกติเท่ากับค่าเดิม (x_vel = 10)"""

            # if self.player.is_landed:
            #     self.stop_timer()

            if self.get_key:
                self.stop_timer_and_save(self.player_name)
                screen.fill((0, 0, 0))
                passed = self.font.render(f"Level {self.level} Passed!", True, (255, 255, 255))
                screen.blit(passed, (screen_width // 2 - 100, screen_height // 2))
                pygame.display.update()
                pygame.time.wait(1500)
                self.load_next_level()

            # if self.get_key:
            #     self.stop_timer_and_save(self.player_name)
            #     pygame.display.update()
            #     pygame.time.wait(1000)  # wait 1 second before switching
            #     self.load_next_level()

            if self.player.rect.top > self.height:
                # self.player.die()
                print('game over')
                # exit()

            if self.get_key:
                screen.fill((0, 0, 0))
                name_surface = self.font.render(f"Pass Level 1", True, (255, 255, 255))
                text_rect = name_surface.get_rect()
                text_rect.center = (screen_width // 2, screen_height // 2)
                screen.blit(name_surface, text_rect.center)
                # self.player.timer_running = False
                print('pass')

            # self.load_map('map_lavel1.tmx', screen)
            # self.player.render(screen)
            pygame.display.update()
            """setup frames per second be 60"""
            self.clock.tick(60)
