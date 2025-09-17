import pygame
import random
import sys
import os

pygame.init()

# -----------------------------
# BASE DIRECTORY (Universal Paths)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Folder where this script lives
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "pokemon sprites")

# -----------------------------
# Window setup
# -----------------------------
icon = pygame.image.load(os.path.join(ASSETS_DIR, "pokeball.jpeg"))
pygame.display.set_icon(icon)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokémon Battle :D")

# -----------------------------
# Backgrounds
# -----------------------------
battle_background = pygame.image.load(os.path.join(ASSETS_DIR, "battle_bg.jpg"))
lobby_background = pygame.image.load(os.path.join(ASSETS_DIR, "lobby_img.png"))
battle_background = pygame.transform.scale(battle_background, (WIDTH, HEIGHT))
lobby_background = pygame.transform.scale(lobby_background, (WIDTH, HEIGHT))

# -----------------------------
# Colors & Fonts
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (207, 126, 126)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 255, 0)
GRAY = (191, 189, 189)

font = pygame.font.Font(None, 32)
large_font = pygame.font.Font(None, 64)

# -----------------------------
# GIF loader helper
# -----------------------------
def load_gif_frames(folder, width=None, height=None):
    frames = []
    for frame_name in sorted(os.listdir(folder)):
        frame_path = os.path.join(folder, frame_name)
        frame = pygame.image.load(frame_path)
        if width and height:
            frame = pygame.transform.scale(frame, (width, height))
        frames.append(frame)
    return frames

# -----------------------------
# Sprite sizes
# -----------------------------
SPRITE_WIDTH, SPRITE_HEIGHT = 100, 100
BATTLESPRITE_WIDTH, BATTLESPRITE_HEIGHT = 300, 300
BATTLESPRITE2_WIDTH, BATTLESPRITE2_HEIGHT = 150, 150

# -----------------------------
# Load GIF frames (Relative Paths)
# -----------------------------
charmander_frames = load_gif_frames(os.path.join(SPRITES_DIR, "charmander_frames"), SPRITE_WIDTH, SPRITE_HEIGHT)
bulbasaur_frames = load_gif_frames(os.path.join(SPRITES_DIR, "bulbasaur_frames"), SPRITE_WIDTH, SPRITE_HEIGHT)
squirtle_frames = load_gif_frames(os.path.join(SPRITES_DIR, "squirtle_frames"), SPRITE_WIDTH, SPRITE_HEIGHT)

charmander_back_frames = load_gif_frames(os.path.join(SPRITES_DIR, "charmander_backframes"), BATTLESPRITE_WIDTH, BATTLESPRITE_HEIGHT)
bulbasaur_back_frames = load_gif_frames(os.path.join(SPRITES_DIR, "bulbasaur_backframes"), BATTLESPRITE_WIDTH, BATTLESPRITE_HEIGHT)
squirtle_back_frames = load_gif_frames(os.path.join(SPRITES_DIR, "squirtle_backframes"), BATTLESPRITE_WIDTH, BATTLESPRITE_HEIGHT)

# -----------------------------
# Pokémon classes
# -----------------------------
class Pokemon:
    type_chart = {
        ("Fire", "Grass"): 2.0, ("Fire", "Water"): 0.5, ("Fire", "Fire"): 1.0,
        ("Water", "Fire"): 2.0, ("Water", "Grass"): 0.5, ("Water", "Water"): 1.0,
        ("Grass", "Water"): 2.0, ("Grass", "Fire"): 0.5, ("Grass", "Grass"): 1.0,
    }

    def __init__(self, trainer, name, type_, hp, atk, sp_atk, defense, sp_def, gif, back_gif, special_move_name):
        self.trainer = trainer
        self.name = name
        self.type = type_
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.sp_atk = sp_atk
        self.defense = defense
        self.sp_def = sp_def
        self.battle_log = []
        self.gif = gif
        self.back_gif = back_gif
        self.current_frame = 0
        self.frame_counter = 0
        self.special_move_name = special_move_name
    
    def tackle(self):
        return ("normal", self.atk)
    
    def take_damage(self, incoming_damage):
        damage_type, damage_value, *attack_type = incoming_damage
        if damage_type == "normal":
            actual_damage = max(1, damage_value - self.defense)
        else:
            attack_type = attack_type[0]
            effectiveness = self.type_chart.get((attack_type, self.type), 1.0)
            actual_damage = max(1, int((damage_value - self.sp_def) * effectiveness))
            if effectiveness > 1.0: self.battle_log.append("It's super effective!")
            elif effectiveness < 1.0: self.battle_log.append("It's not very effective...")
        self.hp -= actual_damage
        self.battle_log.append(f"{self.name} took {actual_damage} damage! HP left: {self.hp}")
    
    def is_fainted(self):
        return self.hp <= 0
    
    def update_frame(self):
        self.frame_counter += 1
        if self.frame_counter >= 2:
            self.current_frame = (self.current_frame + 1) % len(self.gif)
            self.frame_counter = 0
    
    def get_current_frame(self):
        return self.gif[self.current_frame]
    
    def update_back_frame(self):
        self.frame_counter += 1
        if self.frame_counter >= 2:
            self.current_frame = (self.current_frame + 1) % len(self.back_gif)
            self.frame_counter = 0
    
    def get_current_back_frame(self):
        return self.back_gif[self.current_frame]

class Charmander(Pokemon):
    def __init__(self, trainer):
        super().__init__(trainer, "Charmander", "Fire", random.randint(37, 41), 17, 21, 12, 17, charmander_frames, charmander_back_frames, "Ember")
    def ember(self):
        return ("special", self.sp_atk, "Fire")

class Bulbasaur(Pokemon):
    def __init__(self, trainer):
        super().__init__(trainer, "Bulbasaur", "Grass", random.randint(43, 47), 15, 23, 13, 16, bulbasaur_frames, bulbasaur_back_frames, "Vine Whip")
    def vine_whip(self):
        return ("special", self.sp_atk, "Grass")

class Squirtle(Pokemon):
    def __init__(self, trainer):
        super().__init__(trainer, "Squirtle", "Water", random.randint(42, 46), 16, 22, 13, 15, squirtle_frames, squirtle_back_frames, "Water Gun")
    def water_gun(self):
        return ("special", self.sp_atk, "Water")

# -----------------------------
# Draw helpers
# -----------------------------
def draw_text(text, font, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))

def draw_hp_bar(pokemon, x, y):
    bar_width, bar_height = 200, 20
    health_ratio = pokemon.hp / pokemon.max_hp
    pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (x, y, bar_width * health_ratio, bar_height))
    draw_text(f"{pokemon.hp}/{pokemon.max_hp}", font, BLACK, x + 75, y + 25)

def draw_box(x, y, width, height, color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)

# -----------------------------
# Pokémon selection screen
# -----------------------------
def choose_pokemon(trainer_name):
    selected = False
    choice = 0
    options = ["Charmander", "Bulbasaur", "Squirtle"]
    pokemon_classes = [Charmander, Bulbasaur, Squirtle]
    pokemon_instances = [cls(trainer_name) for cls in pokemon_classes]

    clock = pygame.time.Clock()

    while not selected:
        screen.blit(lobby_background, (0, 0))
        draw_box(40, 40, 400, 400, GRAY)
        draw_text(f"{trainer_name}, choose your Pokémon:", font, BLACK, 50, 50)
        for i, option in enumerate(options):
            color = BLUE if i == choice else BLACK
            draw_text(f"{i + 1}: {option}", font, color, 50, 100 + i * 50)
            pokemon_instances[i].update_frame()
            screen.blit(pokemon_instances[i].get_current_frame(), (250, 90 + i * 80))
        
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    choice = (choice + 1) % 3
                elif event.key == pygame.K_UP:
                    choice = (choice - 1) % 3
                elif event.key == pygame.K_RETURN:
                    selected = True
        
    return pokemon_instances[choice]

# -----------------------------
# Player name input
# -----------------------------
def get_player_name(prompt):
    input_box = pygame.Rect(50, 100, 200, 32)
    color_inactive = BLACK
    color_active = BLUE
    color = color_inactive
    active = False
    text = ""
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.blit(lobby_background, (0, 0))
        draw_box(40, 40, 300, 100, GRAY)
        draw_text(prompt, font, BLACK, 50, 50)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()

    return text

# -----------------------------
# Battle function
# -----------------------------
def battle(trainer1, pokemon1, trainer2, pokemon2):
    clock = pygame.time.Clock()
    running = True
    action = None
    battle_log = []

    while running:
        screen.blit(battle_background, (0, 0))

        # Opponent
        draw_box(20, 20, 300, 100, GRAY)
        draw_text(f"{trainer2}'s {pokemon2.name}", font, BLACK, 30, 30)
        draw_hp_bar(pokemon2, 30, 60)
        pokemon2.update_frame()
        opponent_sprite = pygame.transform.scale(pokemon2.get_current_frame(), (BATTLESPRITE2_WIDTH, BATTLESPRITE2_HEIGHT))
        screen.blit(opponent_sprite, (WIDTH - 340, HEIGHT - 400))

        # Player
        draw_box(WIDTH - 320, HEIGHT - 120, 300, 100, GRAY)
        draw_text(f"{trainer1}'s {pokemon1.name}", font, BLACK, WIDTH - 310, HEIGHT - 110)
        draw_hp_bar(pokemon1, WIDTH - 310, HEIGHT - 80)
        pokemon1.update_back_frame()
        screen.blit(pokemon1.get_current_back_frame(), (20, HEIGHT - 407))

        # Battle log
        draw_box(20, HEIGHT - 150, 440, 140, GRAY)
        draw_text("What will "+f"{pokemon1.name} do?", font, BLACK, 30, HEIGHT - 140)
        for i, log in enumerate(battle_log[-3:]):
            draw_text(log, font, BLACK, 30, HEIGHT - 80 + i * 20)

        # Attack options
        draw_box(WIDTH - 320, HEIGHT - 200, 300, 70, RED)
        draw_text("1. Tackle", font, BLACK, WIDTH - 310, HEIGHT - 190)
        draw_text(f"2. {pokemon1.special_move_name}", font, BLACK, WIDTH - 310, HEIGHT - 160)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    action = "tackle"
                elif event.key == pygame.K_2:
                    action = "special"

        # Player's turn
        if action:
            if action == "tackle":
                pokemon2.take_damage(pokemon1.tackle())
                battle_log.extend(pokemon2.battle_log)
                pokemon2.battle_log.clear()
            elif action == "special":
                if isinstance(pokemon1, Charmander): pokemon2.take_damage(pokemon1.ember())
                elif isinstance(pokemon1, Bulbasaur): pokemon2.take_damage(pokemon1.vine_whip())
                elif isinstance(pokemon1, Squirtle): pokemon2.take_damage(pokemon1.water_gun())
                battle_log.extend(pokemon2.battle_log)
                pokemon2.battle_log.clear()
            
            if pokemon2.is_fainted():
                battle_log.append(f"{pokemon2.name} fainted! {trainer1} wins!")
                running = False
                continue

            # Enemy turn
            enemy_action = random.choice(["tackle", "special"])
            if enemy_action == "tackle":
                pokemon1.take_damage(pokemon2.tackle())
                battle_log.extend(pokemon1.battle_log)
                pokemon1.battle_log.clear()
            else:
                if isinstance(pokemon2, Charmander): pokemon1.take_damage(pokemon2.ember())
                elif isinstance(pokemon2, Bulbasaur): pokemon1.take_damage(pokemon2.vine_whip())
                elif isinstance(pokemon2, Squirtle): pokemon1.take_damage(pokemon2.water_gun())
                battle_log.extend(pokemon1.battle_log)
                pokemon1.battle_log.clear()
            
            if pokemon1.is_fainted():
                battle_log.append(f"{pokemon1.name} fainted! {trainer2} wins!")
                running = False
            
            action = None

        pygame.display.flip()
        clock.tick(30)

    # Show final result
    screen.fill(WHITE)
    draw_text(battle_log[-1], large_font, RED, WIDTH // 4, HEIGHT // 2)
    pygame.display.flip()
    pygame.time.wait(3000)

# -----------------------------
# Main function to run the game finally
# -----------------------------
def main():
    trainer1 = get_player_name("Enter Player 1 Name:")
    pokemon1 = choose_pokemon(trainer1)
    
    trainer2 = get_player_name("Enter Player 2 Name:")
    pokemon2 = choose_pokemon(trainer2)
    
    battle(trainer1, pokemon1, trainer2, pokemon2)

if __name__ == "__main__":
    main()
