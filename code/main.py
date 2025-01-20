import pygame
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from mission import Mission
from ui import UI
from random import choice

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Blazor Vortex")
        self.clock = pygame.time.Clock()
        self.running = True

        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Mission/Dialogues
        self.dialogue = None

        # Setup
        self.player = None
        self.ui = UI(self)
        self.load_images()
        self.setup()

    def load_images(self):
        folders = list(walk(join("images", "enemies")))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join("images", "enemies", folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(name.split(".")[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def setup(self):
        map = load_pygame(join("data", "maps", "world.tmx"))

        for x, y, image in map.get_layer_by_name("Ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name("Objects"):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name("Collisions"):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
            else:
                Enemy(
                    (obj.x, obj.y),
                    choice(list(self.enemy_frames.values())),
                    (self.all_sprites, self.enemy_sprites),
                    self.player,
                    self.collision_sprites,
                )

    def handle_attack(self):
        for enemy in self.enemy_sprites:
            if enemy.defeated:
                continue

            player_pos = pygame.Vector2(self.player.rect.center)
            enemy_pos = pygame.Vector2(enemy.rect.center)
            distance = player_pos.distance_to(enemy_pos)

            if distance < 100:
                enemy.take_damage(10)
                if enemy.health <= 0:
                    print(f"Enemy defeated: {enemy}")
                    enemy.defeated = True

        # Kiểm tra nếu tất cả Enemy đã bị đánh bại
        self.check_all_enemies_defeated()

    def check_all_enemies_defeated(self):
        if all(enemy.defeated for enemy in self.enemy_sprites):
            self.start_new_scene()

    def start_new_scene(self):
        self.player.set_position((1200, 1200))  

        self.dialogue = Mission(
            self,
            [
                "Thời Đăng: Đây là đâu? Sao mình lại ở đây?",
                "Thời Đăng: Mình phải tìm cách thoát khỏi nơi này.",
            ],
            on_complete=self.unblock_player_after_dialogue,
        )

    def unblock_player_after_dialogue(self):
        self.dialogue = None
        self.player.unblock()

    def run(self):
        self.dialogue = Mission(
            self,
            [
                "Minh Hàn: Mày học hành kiểu đéo gì thế này?",
                "Thời Đăng: Kệ mẹ tao.",
                "Minh Hàn: Thích thì đánh mẹ nhau đi!",
            ],
        )

        while self.running:
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_attack()

            if self.dialogue and self.dialogue.running:
                self.dialogue.update()
            else:
                self.all_sprites.update(dt)

            self.display_surface.fill("black")
            self.all_sprites.draw(self.player.rect.center)

            if not self.dialogue or not self.dialogue.running:
                self.ui.draw()

            if self.dialogue and self.dialogue.running:
                self.dialogue.show_dialog()

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
