import pygame
from ui import UI

class Mission:
    def __init__(self, game, dialogue, on_complete=None):
        self.game = game
        self.dialogue = dialogue
        self.dialog_index = 0
        self.typed_text = ""
        self.typing_speed = 50  # Tốc độ đánh chữ (ms/char)
        self.last_typing_time = 0
        self.running = True
        self.on_complete = on_complete

        # Cooldown cho SPACE
        self.last_space_press = 0  # Thời điểm SPACE được nhấn
        self.space_cooldown = 200  # Cooldown (ms)

        # Block tất cả nhân vật khi bắt đầu
        # self.game.player.block()
        # for enemy in self.game.enemy_sprites:
        #     enemy.block()

    def draw_dialogue_box(self):
        """Vẽ khung hội thoại."""
        box_width = self.game.display_surface.get_width() * 0.9
        box_height = self.game.display_surface.get_height() * 0.2
        box_x = (self.game.display_surface.get_width() - box_width) / 2
        box_y = self.game.display_surface.get_height() - box_height - 20

        pygame.draw.rect(self.game.display_surface, (0, 0, 0), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.game.display_surface, (255, 255, 255), (box_x, box_y, box_width, box_height), 3)

        return box_x, box_y

    def show_dialog(self):
        """Hiển thị hội thoại với hiệu ứng đánh chữ."""
        if not self.running:
            return

        if self.dialog_index < len(self.dialogue):
            full_text = self.dialogue[self.dialog_index]
            current_time = pygame.time.get_ticks()
            if current_time - self.last_typing_time > self.typing_speed and len(self.typed_text) < len(full_text):
                self.typed_text += full_text[len(self.typed_text)]
                self.last_typing_time = current_time
        else:
            self.running = False  # Kết thúc hội thoại

        # Vẽ hộp thoại
        box_x, box_y = self.draw_dialogue_box()
        font = pygame.font.Font('data/fonts/SVN-Retron 2000.otf', 36)
        text_surface = font.render(self.typed_text, True, (255, 255, 255))
        self.game.display_surface.blit(text_surface, (box_x + 20, box_y + 20))

    def handle_input(self):
        """Xử lý nhập liệu trong hội thoại."""
        if not self.running:
            return

        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Chỉ xử lý nếu SPACE được nhấn và vượt qua cooldown
        if keys[pygame.K_SPACE] and current_time - self.last_space_press > self.space_cooldown:
            self.last_space_press = current_time  # Cập nhật thời điểm SPACE được nhấn

            if len(self.typed_text) < len(self.dialogue[self.dialog_index]):
                # Hiển thị toàn bộ dòng ngay lập tức
                self.typed_text = self.dialogue[self.dialog_index]
            else:
                # Chuyển sang câu thoại tiếp theo
                self.dialog_index += 1
                self.typed_text = ""

    def finish(self):
        """Kết thúc nhiệm vụ."""
        self.running = False
        self.game.player.unblock()
        for enemy in self.game.enemy_sprites:
            enemy.unblock()

        # Thực thi callback nếu được cung cấp
        if self.on_complete:
            self.on_complete()

    def update(self):
        """Cập nhật trạng thái nhiệm vụ."""
        self.handle_input()
        self.show_dialog()

        # Khi hội thoại hoàn thành
        if not self.running and self.on_complete:
            self.on_complete()  # Gọi callback hoàn thành nhiệm vụ
            self.on_complete = None  # Đảm bảo không gọi lại callback này lần nữa

