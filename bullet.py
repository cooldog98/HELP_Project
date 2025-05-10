import pygame
import random


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=15, damage=10):
        super().__init__()

        # Visual properties
        self.image = pygame.Surface((20, 5), pygame.SRCALPHA)  # Transparent background
        pygame.draw.rect(self.image, (0, 255, 255), (0, 0, 20, 5))  # Bright cyan bullet
        pygame.draw.rect(self.image, (255, 255, 0), (0, 0, 20, 5), 1)  # Yellow border

        # Positioning
        self.rect = self.image.get_rect()
        if direction == 'right':
            self.rect.midleft = (x, y-100)
        else:
            self.rect.midright = (x, y-100)

        # Movement properties
        self.speed = speed
        self.direction = direction
        self.lifetime = 90  # Frames until bullet disappears
        self.damage = damage

        # For scrolling worlds
        self.true_x = x
        self.true_y = y

        # Collision detection
        self.mask = pygame.mask.from_surface(self.image)

        # Visual effects
        self.trail_particles = []
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt, offset_x=0):
        # Calculate movement with frame-rate independence
        move_distance = self.speed * dt * 60

        # Update position
        if self.direction == 'right':
            self.true_x += move_distance
        else:
            self.true_x -= move_distance

        # self.rect.y -= 10

        # Handle world scrolling
        self.rect.x = self.true_x - offset_x
        self.rect.y = self.true_y

        # Update lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

        # Add visual trail effect
        if pygame.time.get_ticks() - self.spawn_time > 50:  # Every 50ms
            self.add_trail_particle()
            self.spawn_time = pygame.time.get_ticks()

        self.update_trail_particles()

    def add_trail_particle(self):
        """Add a visual effect particle to the trail"""
        if self.direction == 'right':
            pos = (self.rect.left - 2, self.rect.centery)
        else:
            pos = (self.rect.right + 2, self.rect.centery)

        self.trail_particles.append({
            'pos': pos,
            'size': random.randint(2, 4),
            'life': random.randint(10, 20),
            'color': (random.randint(200, 255), random.randint(200, 255), 0)
        })

    def update_trail_particles(self):
        """Update and remove expired trail particles"""
        for particle in self.trail_particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)

    def draw_trail(self, surface):
        """Draw the bullet's trail effect"""
        for particle in self.trail_particles:
            pygame.draw.circle(
                surface,
                particle['color'],
                (int(particle['pos'][0]), int(particle['pos'][1])),
                particle['size']
            )

    def draw(self, surface):
        """Draw the bullet and its trail"""
        self.draw_trail(surface)
        surface.blit(self.image, self.rect)
