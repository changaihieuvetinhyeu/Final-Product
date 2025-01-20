from settings import * 
from math import atan2, degrees
import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player
        self.blocked = False
        self.defeated = False

        # Image setup
        self.frames = frames
        self.frame_index = 0
        self.original_image = self.frames[self.frame_index]
        self.image = self.original_image.copy()
        self.animation_speed = 6

        # Rect setup
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 200

        # Health setup
        self.health = 50  # Current health
        self.max_health = 50  # Maximum health

        # Hit effect setup
        self.hit_time = 0
        self.hit_duration = 100  # Duration of the white flash effect (ms)
        self.is_hit = False

    def animate(self, dt):
        """Handle enemy animation by cycling through frames."""
        self.frame_index += self.animation_speed * dt
        self.frame_index %= len(self.frames)  # Ensure the index stays within bounds
        self.original_image = self.frames[int(self.frame_index)]

    def move(self, dt):
        """Move the enemy toward the player unless blocked."""
        if self.blocked or self.defeated:
            return

        # Calculate direction toward the player
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        direction = player_pos - enemy_pos

        if direction.length() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.Vector2()

        # Update position with collision handling
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        """Handle collisions with obstacles."""
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                elif direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom

    def block(self):
        """Block the enemy from moving."""
        self.blocked = True

    def unblock(self):
        """Unblock the enemy to allow movement."""
        self.blocked = False

    def take_damage(self, damage):
        if not self.defeated:
            self.health -= damage
            self.is_hit = True
            self.hit_time = pygame.time.get_ticks()

            # Check if health drops to zero or below
            if self.health <= 0:
                self.kill()
                self.defeated = True
                self.block()  # Block movement upon defeat

    def update(self, dt):
        """Update enemy state, including movement, animation, and hit effects."""
        current_time = pygame.time.get_ticks()

        # Handle hit effect
        if self.is_hit:
            # Change image to white tint
            self.image = self.original_image.copy()
            white_surf = pygame.Surface(self.image.get_size(), flags=pygame.SRCALPHA)
            white_surf.fill((255, 255, 255, 128))
            self.image.blit(white_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # Check if hit effect duration is over
            if current_time - self.hit_time > self.hit_duration:
                self.is_hit = False

        elif not self.defeated:
            # Restore original image if not defeated
            self.image = self.original_image.copy()

        # Update movement and animation if not defeated
        if not self.defeated:
            self.move(dt)
            self.animate(dt)

