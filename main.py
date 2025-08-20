import pygame
import sys
from sprites import *
from config import *
# NOVAS IMPORTAÇÕES PARA O MULTIPLAYER
from network import Server, Client
from ui_elements import InputBox
import socket


class Game:
    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        pygame.joystick.init()
        self.music_volume = 0.15  
        pygame.mixer.music.set_volume(self.music_volume)
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Joystick conectado: {self.joystick.get_name()}")
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont('arial.ttf', 32)
        self.dialog_box = DialogBox(self)
        self.next_level_triggered = False
        self.running = True
        self.paused = False 
        self.font = pygame.font.SysFont('arial.ttf', 32)
        
        # Atributos do jogador (serão definidos na seleção)
        self.player_attrs = {}
        
        # NOVOS ATRIBUTOS PARA O MULTIPLAYER
        self.network = None
        self.other_players = {} # Dicionário para armazenar sprites de outros jogadores {player_id: sprite}
        self.player_id = None
        self.game_mode = 'single_player' # 'single_player', 'host', ou 'client'
        
        # Inicializa grupos de sprites
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.arrows = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.snowflakes = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.bats = pygame.sprite.LayeredUpdates() 
        self.attacks = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.LayeredUpdates()
        self.water = pygame.sprite.LayeredUpdates()
        self.bosses = pygame.sprite.LayeredUpdates()
        self.fire_areas = pygame.sprite.LayeredUpdates()
        self.house = pygame.sprite.LayeredUpdates()
        self.watermelon = pygame.sprite.LayeredUpdates()
        self.particles = pygame.sprite.LayeredUpdates() 
        self.player_attacks = pygame.sprite.LayeredUpdates()
        
        self.shield_spritesheet = Spritesheet('sprt/img/shield.png')
        self.arrowsSpecial_spritesheet = Spritesheet('sprt/img/arrowSpecial_spr.png')
        self.arrows_spritesheet = Spritesheet('sprt/img/arrow_spr.png')
        self.boxer_spritesheet = Spritesheet(PLAYER3_ATTR["animation_sheet"])
        self.boxe_spritesheet = Spritesheet('sprt/img/boxing_glove.png')
        self.watermelon_spritesheet = Spritesheet("sprt/img/watermelon.png")
        self.snowflakes_spritesheet = Spritesheet('sprt/img/snowflake_spr.png')
        self.house_spritesheet = Spritesheet('sprt/img/pixel-art-house.png')
        self.terrain_spritesheet = Spritesheet('sprt/terrain/terrain.png')
        self.obstacle_spritesheet = Spritesheet('sprt/terrain/TreesSpr.png')
        self.portal_spritsheet = Spritesheet('sprt/terrain/portalpurplespr.png')
        self.enemy_spritesheet = Spritesheet('sprt/img/enemy.png')
        self.enemycoin_spritesheet = Spritesheet('sprt/img/enemy.png')
        self.bats_spritesheet = Spritesheet('sprt/npc/bat.png')
        self.coin = Spritesheet('sprt/img/coin_spr.png')
        self.attack_spritsheet = Spritesheet('sprt/guts-spr-full_noise1_scale.png')
        self.plant_spritesheet = Spritesheet('sprt/terrain/terrain.png')
        self.block_spritesheet = Spritesheet('sprt/terrain/terrain.png')
        self.intro_background = pygame.image.load('sprt/img/introbackground.png')
        self.go_background = pygame.image.load('sprt/img/gameover.png')
        self.slimenpc = Spritesheet('sprt/npc/slime_spr.png')
        self.seller_spritesheet = Spritesheet('sprt/npc/seller.png')
        
        self.ability_panel = AbilityPanel(self)
        self.current_level = 1
        self.max_levels = 6

    # V-- MÉTODOS DE MULTIPLAYER ADICIONADOS AQUI --V
    def get_local_ip(self):
        """Tenta encontrar o endereço IP local."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Não precisa ser um IP alcançável
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1' # Fallback
        finally:
            s.close()
        return IP

    def show_mode_selection_screen(self):
        """Mostra a tela para escolher entre Single Player e Multiplayer."""
        title_font = pygame.font.SysFont('arial', 60, bold=True)
        
        single_player_btn = Button(WIN_WIDTH//2 - 150, WIN_HEIGHT//2 - 60, 300, 80, WHITE, BLACK, "Single Player", 40)
        multiplayer_btn = Button(WIN_WIDTH//2 - 150, WIN_HEIGHT//2 + 40, 300, 80, WHITE, BLACK, "Multiplayer (LAN)", 40)

        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if single_player_btn.is_pressed(mouse_pos, mouse_pressed):
                self.game_mode = 'single_player'
                return 'single_player'
            
            if multiplayer_btn.is_pressed(mouse_pos, mouse_pressed):
                return 'multiplayer'

            self.screen.blit(self.intro_background, (0, 0))
            title = title_font.render("GameAdventure", True, BLACK)
            self.screen.blit(title, (WIN_WIDTH//2 - title.get_width()//2, 100))
            self.screen.blit(single_player_btn.image, single_player_btn.rect)
            self.screen.blit(multiplayer_btn.image, multiplayer_btn.rect)
            
            pygame.display.update()
            self.clock.tick(FPS)

    def show_multiplayer_role_screen(self):
        """Mostra a tela para escolher entre Host e Cliente."""
        title_font = pygame.font.SysFont('arial', 50, bold=True)
        info_font = pygame.font.SysFont('arial', 28)
        
        host_btn = Button(WIN_WIDTH//2 - 125, WIN_HEIGHT//2 - 120, 250, 70, WHITE, BLACK, "Ser Host", 36)
        client_btn = Button(WIN_WIDTH//2 - 125, WIN_HEIGHT//2 + 80, 250, 70, WHITE, BLACK, "Conectar", 36)
        back_btn = Button(20, WIN_HEIGHT - 70, 100, 50, WHITE, RED, "Voltar", 30)

        local_ip = self.get_local_ip()
        ip_input = InputBox(WIN_WIDTH//2 - 150, WIN_HEIGHT//2, 300, 50, self.font)
        
        selecting = True
        while selecting:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                ip_input.handle_event(event)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if host_btn.is_pressed(mouse_pos, mouse_pressed):
                self.game_mode = 'host'
                self.network = Server(local_ip, 5555)
                if not self.network.start():
                    print("Não foi possível iniciar o servidor.")
                    return 'back'
                self.player_id = self.network.player_id
                return 'host'
            
            if client_btn.is_pressed(mouse_pos, mouse_pressed) and ip_input.text:
                self.game_mode = 'client'
                self.network = Client(ip_input.text, 5555)
                if not self.network.connect():
                    print(f"Não foi possível conectar a {ip_input.text}")
                    continue
                return 'client'

            if back_btn.is_pressed(mouse_pos, mouse_pressed):
                return 'back'

            self.screen.blit(self.intro_background, (0, 0))
            
            title_host = title_font.render("Iniciar um Jogo", True, BLACK)
            self.screen.blit(title_host, (WIN_WIDTH//2 - title_host.get_width()//2, 100))
            info_host = info_font.render(f"Seu IP: {local_ip}", True, BLACK)
            self.screen.blit(info_host, (WIN_WIDTH//2 - info_host.get_width()//2, 160))
            self.screen.blit(host_btn.image, host_btn.rect)

            title_client = title_font.render("Entrar em um Jogo", True, BLACK)
            self.screen.blit(title_client, (WIN_WIDTH//2 - title_client.get_width()//2, 300))
            info_client = info_font.render("IP do Host:", True, BLACK)
            self.screen.blit(info_client, (ip_input.rect.x, ip_input.rect.y - 35))
            ip_input.draw(self.screen)
            self.screen.blit(client_btn.image, client_btn.rect)
            
            self.screen.blit(back_btn.image, back_btn.rect)

            pygame.display.update()
            self.clock.tick(FPS)

    def character_selection_screen(self):
        selected = 1
        
        
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        char_font = pygame.font.SysFont('arial', 36)
        desc_font = pygame.font.SysFont('arial', 24)
        
        left_btn = Button(100, WIN_HEIGHT//2, 50, 50, WHITE, BLACK, "<", 32)
        right_btn = Button(WIN_WIDTH-150, WIN_HEIGHT//2, 50, 50, WHITE, BLACK, ">", 32)
        play_btn = Button(WIN_WIDTH//2 - 60, WIN_HEIGHT - 100, 120, 50, WHITE, BLACK, "Jogar", 32)
        
        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            if left_btn.is_pressed(mouse_pos, mouse_pressed):
                selected = (selected - 2) % len(CHARACTERS) + 1
                pygame.time.delay(200)
            if right_btn.is_pressed(mouse_pos, mouse_pressed):
                selected = selected % len(CHARACTERS) + 1
                pygame.time.delay(200)
            if play_btn.is_pressed(mouse_pos, mouse_pressed):
                self.player_attrs = CHARACTERS[selected]
                selecting = False
            
            self.screen.blit(self.intro_background, (0,0))
            
            panel_width = 640
            panel_height = 400
            panel_x = WIN_WIDTH // 2 - panel_width // 2
            panel_y = WIN_HEIGHT // 2 - panel_height // 2
            
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            
            pygame.draw.rect(panel_surface, UI_BG_COLOR, (0, 0, panel_width, panel_height), border_radius=15)
            
            pygame.draw.rect(panel_surface, UI_BORDER_COLOR, (0, 0, panel_width, panel_height), width=UI_BORDER_WIDTH, border_radius=15)
            
            self.screen.blit(panel_surface, (panel_x, panel_y))
            
            current_char = CHARACTERS[selected]
            
            title = title_font.render("Selecione seu personagem", True, UI_TITLE_COLOR)
            self.screen.blit(title, (WIN_WIDTH//2 - title.get_width()//2, panel_y +17))
            
            try:
                char_img = pygame.image.load(current_char["sprite"]).convert_alpha()
                char_img = pygame.transform.scale(char_img, (200, 200))
                img_rect = char_img.get_rect(center=(WIN_WIDTH//2, panel_y + 170))
                self.screen.blit(char_img, img_rect)
            except:
                placeholder = pygame.Surface((200, 200))
                placeholder.fill(RED)
                self.screen.blit(placeholder, (WIN_WIDTH//2 - 100, panel_y + 60))
            
            name_text = char_font.render(current_char["name"], True, UI_FONT_COLOR)
            self.screen.blit(name_text, (WIN_WIDTH//2 - name_text.get_width()//2, panel_y + 280))
            
            stats_text = desc_font.render(
                f"Vida: {current_char['life']} | Dano: {current_char['damage']} | Velocidade: {current_char['speed']}", 
                True, SELECTED_COLOR
            )
            
            self.screen.blit(stats_text, (WIN_WIDTH//2 - stats_text.get_width()//2, panel_y + 320))
            
            desc_text = desc_font.render(current_char["description"], True, UI_FONT_COLOR)
            self.screen.blit(desc_text, (WIN_WIDTH//2 - desc_text.get_width()//2, panel_y + 350))
            
            self.screen.blit(left_btn.image, left_btn.rect)
            self.screen.blit(right_btn.image, right_btn.rect)
            self.screen.blit(play_btn.image, play_btn.rect)
            
            pygame.display.update()
            self.clock.tick(FPS)
            
    # O método intro_screen original foi substituído pelos novos menus, mas pode ser mantido se desejado.

    # main.py

    def next_level(self):
        # Salva o estado completo do jogador antes de limpar os sprites
        if hasattr(self, 'player'):
            player_life = self.player.life
            player_coins = self.player.coins
            player_damage = self.player.damage
            player_speed_boost = self.player.speed_boost
            player_attack_cooldown_multiplier = self.player.attack_cooldown_multiplier
            player_dodge_cooldown_multiplier = self.player.dodge_cooldown_multiplier
        else:
            # Valores de fallback
            player_life = 20
            player_coins = 0
            player_damage = None
            player_speed_boost = 0
            player_attack_cooldown_multiplier = 1.0
            player_dodge_cooldown_multiplier = 1.0

        # Limpa todos os sprites e grupos relevantes
        self.all_sprites.empty()
        self.arrows.empty()
        self.blocks.empty()
        self.bats.empty()
        self.enemies.empty()
        self.attacks.empty()
        self.npcs.empty()
        self.water.empty()
        self.bosses.empty()
        self.snowflakes.empty()
        self.fire_areas.empty()
        self.other_players.clear()
        self.particles.empty() # Limpa as partículas da tela anterior

        music = None # Inicializa a variável de música

        # --- LÓGICA REVISADA PARA TRANSIÇÃO DE NÍVEL ---
        
        # Verifica se estamos vindo da loja para um novo nível/chefe
        if getattr(self, 'loading_store', False):
            self.loading_store = False
            self.current_level += 1  # Incrementa o nível (ex: 5 -> 6)

            # Imediatamente verifica se o novo nível ultrapassa o máximo
            if self.current_level >= self.max_levels:
                print("Todos os níveis normais completados! Preparando para o boss...")
                self.load_boss_level()
                return  # Encerra o método aqui, pois load_boss_level cuida do resto
            else:
                # Carrega o próximo nível normal
                music = MUSIC_LEVELS.get(self.current_level, MUSIC_LEVELS.get(1))
                self.createTilemap(create_player=True) # Usa self.current_level para carregar o mapa
        else:
            # Se não, estamos indo de um nível para a loja
            self.loading_store = True
            music = MUSIC_LEVELS.get('store')
            self.createTilemap(create_player=True, force_map='store')

        # Restaura os atributos do jogador (não será executado para o chefe devido ao 'return')
        if hasattr(self, 'player'):
            self.player.life = player_life
            self.player.coins = player_coins
            if player_damage is not None:
                self.player.damage = player_damage
            self.player.speed_boost = player_speed_boost
            self.player.attack_cooldown_multiplier = player_attack_cooldown_multiplier
            self.player.dodge_cooldown_multiplier = player_dodge_cooldown_multiplier

            if self.game_mode in ['host', 'client']:
                self.player.id = self.player_id

        # Carrega a música apropriada
        if music:
            try:
                pygame.mixer.music.load(music)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception as e:
                print(f"Erro ao carregar música: {e}")

    def load_boss_level(self):
        # Salva o estado completo do jogador antes de limpar os sprites
        if hasattr(self, 'player'):
            player_life = self.player.life
            player_coins = self.player.coins
            player_damage = self.player.damage
            player_speed_boost = self.player.speed_boost
            player_attack_cooldown_multiplier = self.player.attack_cooldown_multiplier
            player_dodge_cooldown_multiplier = self.player.dodge_cooldown_multiplier
        else:
            # Valores de fallback
            player_life = 20
            player_coins = 0
            player_damage = None
            player_speed_boost = 0
            player_attack_cooldown_multiplier = 1.0
            player_dodge_cooldown_multiplier = 1.0

        self.all_sprites.empty()
        self.arrows.empty()
        self.blocks.empty()
        self.enemies.empty()
        self.bats.empty()
        self.attacks.empty()
        self.npcs.empty()
        self.water.empty()
        self.bosses.empty()
        self.fire_areas.empty()
        self.other_players.clear()
        self.particles.empty()

        self.createTilemap(create_player=True, force_map='boss_arena')
        
        # Restaura o estado completo do jogador após sua recriação
        if hasattr(self, 'player'):
            self.player.life = player_life
            self.player.coins = player_coins
            if player_damage is not None:
                self.player.damage = player_damage
            self.player.speed_boost = player_speed_boost
            self.player.attack_cooldown_multiplier = player_attack_cooldown_multiplier
            self.player.dodge_cooldown_multiplier = player_dodge_cooldown_multiplier
            
            if self.game_mode in ['host', 'client']:
                self.player.id = self.player_id

        print("Carregando mapa do boss!")
        try:
            pygame.mixer.music.load(MUSIC_LEVELS.get('boss', MUSIC_LEVELS[1]))
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception as e:
            print(f"Erro ao carregar música do boss: {e}")

    def createTilemap(self, create_player=True, force_map=None):
        try:
            if force_map == 'store':
                current_tilemap = store
            elif force_map == 'boss_arena':
                current_tilemap = boss_arena
            elif self.current_level == 1:
                current_tilemap = tilemap
            elif self.current_level == 2:
                current_tilemap = tilemap2
            elif self.current_level == 3:
                current_tilemap = tilemap3
            elif self.current_level == 4:
                current_tilemap = tilemap4
                for _ in range(50):
                    Snowflake(self)
            elif self.current_level == 5:
                current_tilemap = tilemap5
                

            temp_tilemap = [list(row) for row in current_tilemap]
            obstacle_positions = []
            
            if force_map not in ['store', 'boss_arena'] and self.current_level != 2:
                while len(obstacle_positions) < OBSTACLE_COUNT:
                    x = random.randint(0, len(temp_tilemap[0]) - 1)
                    y = random.randint(0, len(temp_tilemap) - 1)
                    if temp_tilemap[y][x] == '.':
                        temp_tilemap[y][x] = 'O'
                        obstacle_positions.append((x, y))
            
            for i, row in enumerate(temp_tilemap):
                for j, column in enumerate(row):
                    Ground1(self, j, i)
                    if column == "B": Block(self, j, i)
                    if column == "E" and force_map not in ['store', 'boss_arena']: enemy(self, j, i)
                    if column == "C" and force_map not in ['store', 'boss_arena']: EnemyCoin(self, j, i)
                    if column == "P" and create_player: self.player = Player(self, j, i)
                    if column == "Q": Plant(self, j, i)
                    if column == "O" and force_map not in ['store', 'boss_arena'] and self.current_level not in (2, 5):
                        Obstacle(self, j, i)

                    if column == "S": SlimeNPC(self, j, i)
                    if column == "T": Portal(self, j, i)
                    if column == "M": Seller1NPC(self, j, i)
                    if column == "V": Seller2NPC(self, j, i)
                    if column == "W": Water1(self, j, i)
                    if column == "H": House(self, j, i)
                    if column == "G" and self.current_level == 3: Bat(self, j, i)
                    if column == "N": self.nero = Nero(self, j, i)
                    if column == "!": Water_Watermelon(self, j, i)
                    if column == "Z": Watermelon(self, j, i)
        except Exception as e:
            print(f"Erro ao criar tilemap: {e}")

    def new(self):
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(MUSIC_LEVELS[1])
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception as e:
            print(f"Erro ao carregar música: {e}")
        self.playing = True
        self.current_level = 1#Nível Start
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.arrows = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.bats = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.LayeredUpdates()
        self.bosses = pygame.sprite.LayeredUpdates()
        self.fire_areas = pygame.sprite.LayeredUpdates()
        self.particles = pygame.sprite.LayeredUpdates()
        self.watermelon = pygame.sprite.LayeredUpdates()
        
        self.createTilemap(create_player=True)

    def events(self):
        shop_active = any(isinstance(npc, Seller2NPC) and npc.shop_active for npc in self.npcs)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not shop_active:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.music_volume = min(1.0, self.music_volume + 0.05)
                    pygame.mixer.music.set_volume(self.music_volume)
                
                elif event.key == pygame.K_MINUS:
                    self.music_volume = max(0.0, self.music_volume - 0.05)
                    pygame.mixer.music.set_volume(self.music_volume)

                elif event.key == pygame.K_F11:
                    if self.screen.get_flags() & pygame.FULLSCREEN:
                        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
                    else:
                        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.FULLSCREEN)
                
                elif event.key == pygame.K_SPACE:
                    if hasattr(self, 'dialog_box') and self.dialog_box.active:
                        if self.dialog_box.text_progress < len(self.dialog_box.current_text):
                            self.dialog_box.text_progress = len(self.dialog_box.current_text)
                        else:
                            if not self.dialog_box.next_dialog():
                                self.dialog_box.close()
                    elif hasattr(self, 'player') and self.player.can_attack() and self.player.life > 0:
                        self.player.last_attack_time = pygame.time.get_ticks()
                        self.perform_attack()
            
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 9 and not shop_active:
                    self.paused = not self.paused
                
                elif event.button == 1:
                    if hasattr(self, 'dialog_box') and self.dialog_box.active:
                        self.dialog_box.text_progress = len(self.dialog_box.current_text)
                    elif hasattr(self, 'player') and self.player.can_attack() and self.player.life > 0:
                        self.player.last_attack_time = pygame.time.get_ticks()
                        self.perform_attack()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if hasattr(self, 'dialog_box') and self.dialog_box.active:
                        self.dialog_box.text_progress = len(self.dialog_box.current_text)
                    elif hasattr(self, 'player') and self.player.can_attack() and self.player.life > 0:
                        self.player.last_attack_time = pygame.time.get_ticks()
                        self.perform_attack()
    
    def archer_attack(self):
        if hasattr(self, 'player'):
            Arrow(self, self.player.rect.centerx, self.player.rect.centery, self.player.facing)

    def perform_attack(self):
        if self.player.char_type == 'swordsman':
            if self.player.facing == 'up': SwordAttack(self, self.player.rect.x, self.player.rect.y - 35)
            elif self.player.facing == 'down': SwordAttack(self, self.player.rect.x, self.player.rect.y + 40)
            elif self.player.facing == 'right': SwordAttack(self, self.player.rect.x + 40, self.player.rect.y)
            elif self.player.facing == 'left': SwordAttack(self, self.player.rect.x - 30, self.player.rect.y)
        
        elif self.player.char_type == 'archer':
            self.archer_attack()

        elif self.player.char_type == 'boxer':
            if self.player.facing == 'up': Boxing(self, self.player.rect.x, self.player.rect.y - TILESIZES)
            elif self.player.facing == 'down': Boxing(self, self.player.rect.x, self.player.rect.y + TILESIZES)
            elif self.player.facing == 'right': Boxing(self, self.player.rect.x + TILESIZES, self.player.rect.y)
            elif self.player.facing == 'left': Boxing(self, self.player.rect.x - TILESIZES, self.player.rect.y)

    def update(self):
        if self.paused:
            return

        # Lógica de rede para modo multiplayer
        if self.game_mode in ['host', 'client']:
            # Enviar estado do jogador local
            if hasattr(self, 'player') and self.player.alive():
                player_state = {
                    "x": self.player.x, 
                    "y": self.player.y, 
                    "facing": self.player.facing,
                    "char_type": self.player.char_type # Envia o tipo de personagem
                }
                if self.game_mode == 'host':
                    self.network.update_local_player_state(player_state)
                else: # client
                    self.network.send_data(player_state)
            
            # Garante que o ID do jogador já foi recebido do servidor antes de continuar
            if self.game_mode == 'client' and self.player_id is None:
                self.player_id = self.network.player_id
                if self.player_id is None: # Ainda esperando
                    return # Pula o resto do update até receber o ID
            
            # Receber e processar estado do jogo
            game_state = self.network.game_state
            all_player_ids = list(game_state.keys())
            current_other_ids = list(self.other_players.keys())
            
            # Adiciona novos jogadores
            for p_id_str in all_player_ids:
                p_id = int(p_id_str)
                if p_id != self.player_id and p_id not in current_other_ids:
                    print(f"Novo jogador {p_id} detectado. Criando sprite.")
                    new_player_state = game_state[p_id_str]
                    
                    char_type = new_player_state.get("char_type", "swordsman")
                    char_id_for_new_player = 1
                    for id_val, attrs in CHARACTERS.items():
                        if attrs["type"] == char_type:
                            char_id_for_new_player = id_val
                            break
                    
                    original_attrs = self.player_attrs
                    self.player_attrs = CHARACTERS[char_id_for_new_player]
                    
                    # Cria o sprite em uma posição inicial (será atualizada em seguida)
                    other_player_sprite = Player(self, 0, 0)
                    other_player_sprite.id = p_id
                    self.other_players[p_id] = other_player_sprite
                    
                    self.player_attrs = original_attrs

            # Remove jogadores desconectados
            for p_id in current_other_ids:
                if str(p_id) not in all_player_ids:
                    print(f"Jogador {p_id} desconectou. Removendo sprite.")
                    self.other_players[p_id].kill()
                    del self.other_players[p_id]
                    
            # Atualiza a posição e animação dos outros jogadores
            for p_id, sprite in self.other_players.items():
                if str(p_id) in game_state:
                    state = game_state[str(p_id)]
                    sprite.x = state['x']
                    sprite.y = state['y']
                    sprite.facing = state['facing']
                    sprite.animate()
        
        # --- Lógica de update original ---
        shop_active = any(isinstance(npc, Seller2NPC) and npc.shop_active for npc in self.npcs)
        
        # Atualiza todos os sprites, exceto o player se a loja estiver ativa
        for sprite in self.all_sprites:
            if sprite not in self.other_players.values(): # Não atualiza os remotos aqui
                if not (shop_active and isinstance(sprite, Player)):
                    sprite.update()

        self.check_enemies_and_spawn_portal()
        
        for boss in self.bosses:
            if boss.life <= 0:
                print("Nero derrotado!")
                boss.kill()
                self.playing = False
                self.win_screen()
    
        # Lógica da câmera (focada apenas no jogador local)
        if hasattr(self, 'player') and self.player.alive():
            camera_offset_x = WIN_WIDTH // 2 - self.player.rect.centerx
            camera_offset_y = WIN_HEIGHT // 2 - self.player.rect.centery
            
            # Aplica o deslocamento da câmera a todos os sprites
            for sprite in self.all_sprites:
                if sprite not in self.snowflakes:
                    sprite.rect.x += camera_offset_x
                    sprite.rect.y += camera_offset_y

            # Atualiza as posições `x` e `y` do jogador local com o offset da câmera
            # para que as colisões relativas ao mapa continuem funcionando.
            self.player.x += camera_offset_x
            self.player.y += camera_offset_y
            
            # Os outros jogadores são atualizados com base nos dados de rede,
            # então a câmera os moverá corretamente junto com o resto do cenário.

    def draw(self):
        self.screen.fill(BLACK)
        
        # Desenha todos os sprites (incluindo o jogador local e os outros jogadores)
        self.all_sprites.draw(self.screen)
        
        # Desenha as barras de vida
        if hasattr(self, 'player') and self.player.alive():
            self.player.draw_health_bar(self.screen)
        
        # MODIFICADO: Desenha a barra de vida dos outros jogadores
        for p_sprite in self.other_players.values():
            if p_sprite.alive():
                p_sprite.draw_health_bar(self.screen)
        for melon in self.watermelon: melon.draw_health_bar(self.screen)
        for enemy in self.enemies: enemy.draw_health_bar(self.screen)
        for bats in self.bats: bats.draw_health_bar(self.screen)
        for boss in self.bosses: boss.draw_health_bar()
        for npc in self.npcs:
            if isinstance(npc, Seller2NPC):
                npc.draw_shop(self.screen)

        volume_text = self.font.render(f"Volume: {int(self.music_volume * 100)}%", True, WHITE)
        self.screen.blit(volume_text, (10, 10))
        
        self.clock.tick(FPS)
        self.ability_panel.draw(self.screen)
        self.dialog_box.draw(self.screen)
        if self.paused:
            self.draw_pause_menu()
        pygame.display.update()

    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        text = self.font.render('Game Over, TENTE NOVAMENTE!', True, WHITE)
        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
        restart_button = Button(10, WIN_HEIGHT - 60, 120, 50, WHITE, BLACK, 'Restart', 32)
        
        for sprite in self.all_sprites: sprite.kill()
        
        restarting = True
        while restarting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                restarting = False # Sai deste loop para voltar ao loop principal de menu

            self.screen.blit(self.go_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()
    
    def win_screen(self):
        text = self.font.render('VOCÊ VENCEU!', True, WHITE)
        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
        restart_button = Button(10, WIN_HEIGHT - 60, 120, 50, WHITE, BLACK, 'Reiniciar', 32)
        for sprite in self.all_sprites: sprite.kill()
        
        restarting = True
        while restarting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                restarting = False

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def check_enemies_and_spawn_portal(self):
        if len(self.enemies) == 0 and len(self.bats) == 0 and not any(isinstance(boss, Nero) for boss in self.bosses):
            for sprite in self.all_sprites:
                if isinstance(sprite, Portal):
                    sprite.active = True
                    return
                    
            if hasattr(self, 'player'):
                x_pos = (self.player.rect.x // TILESIZES) + 2
                y_pos = self.player.rect.y // TILESIZES
                portal = Portal(self, x_pos, y_pos)
                portal.active = True
            
    def draw_pause_menu(self):
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.SysFont('arial', 72, bold=True)
        option_font = pygame.font.SysFont('arial', 30)
        controls_font = pygame.font.SysFont('arial', 22)

        title_text = title_font.render("PAUSADO", True, WHITE)
        title_rect = title_text.get_rect(center=(WIN_WIDTH / 2, 100))
        self.screen.blit(title_text, title_rect)

        # ... (Restante do código do menu de pausa pode ser mantido como está)

# NOVO LOOP PRINCIPAL DE EXECUÇÃO
g = Game()

while g.running:
    mode = g.show_mode_selection_screen()

    if mode is None:
        break
        
    if mode == 'multiplayer':
        role = g.show_multiplayer_role_screen()
        if role == 'back' or role is None:
            continue
    
    g.character_selection_screen()
    
    g.new()

    if g.game_mode in ['host', 'client']:
        if g.player and g.player_id is not None:
            g.player.id = g.player_id
            print(f"Jogador local {g.player.id} inicializado.")

    g.main()

    if not g.running:
        break

    g.game_over()


pygame.quit()
sys.exit()
