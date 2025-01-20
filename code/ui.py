import pygame

class UI:
    def __init__(self, game):
        self.game = game  # Tham chiếu đến game để truy cập các nhân vật
        self.bar_width = 200  # Chiều rộng thanh máu
        self.bar_height = 20  # Chiều cao thanh máu
        self.player_bar_pos = (50, 50)  # Vị trí thanh máu của Player
        self.enemy_bar_pos = (self.game.display_surface.get_width() - 250, 50)  # Thanh máu của Enemy

        # Màu sắc
        self.bg_color = (0, 0, 0)  # Màu nền thanh máu
        self.health_color = (255, 0, 0)  # Màu máu (xanh lá)
        self.border_color = (255, 255, 255)  # Màu viền thanh máu

    def draw_health_bar(self, health, max_health, position):
        """Vẽ thanh máu tại vị trí được chỉ định."""
        x, y = position

        # Vẽ nền thanh máu
        pygame.draw.rect(self.game.display_surface, self.bg_color, (x, y, self.bar_width, self.bar_height))
        # Vẽ thanh máu dựa trên tỷ lệ máu còn lại
        health_width = int(self.bar_width * (health / max_health))
        pygame.draw.rect(self.game.display_surface, self.health_color, (x, y, health_width, self.bar_height))
        # Vẽ viền thanh máu
        pygame.draw.rect(self.game.display_surface, self.border_color, (x, y, self.bar_width, self.bar_height), 3)

    def draw(self):
        """Vẽ thanh máu của Player và Enemy."""
        # Giả sử Player và Enemy có thuộc tính `health` và `max_health`
        self.draw_health_bar(self.game.player.health, self.game.player.max_health, self.player_bar_pos)
        for enemy in self.game.enemy_sprites:
            if enemy.health > 0:
                self.draw_health_bar(enemy.health, enemy.max_health, self.enemy_bar_pos)
