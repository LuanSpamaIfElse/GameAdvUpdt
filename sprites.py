import pygame
import pygame.sprite
from config import *
import math
import random


class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height], pygame.SRCALPHA)  # transparência
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = [self.game.all_sprites]  #uma lista
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Pega o tipo de personagem para usar no if/else
        self.char_type = self.game.player_attrs.get('type', 'swordsman')
        
        # Variável para o caminho da spritesheet que será definida no if/else
        animation_sheet_path = ''

        # --- ESTRUTURA IF/ELSE PARA CADA PERSONAGEM ---
        if self.char_type == 'swordsman':
            self.max_life = PLAYER1_ATTR['life']
            self.damage = PLAYER1_ATTR['damage']
            self.base_speed = PLAYER1_ATTR['speed']
            animation_sheet_path = PLAYER1_ATTR['animation_sheet']
        
        elif self.char_type == 'archer':
            self.max_life = PLAYER2_ATTR['life']
            self.damage = PLAYER2_ATTR['damage']
            self.base_speed = PLAYER2_ATTR['speed']
            animation_sheet_path = PLAYER2_ATTR['animation_sheet']
            
        elif self.char_type == 'boxer':
            self.max_life = PLAYER3_ATTR['life']
            self.damage = PLAYER3_ATTR['damage']
            self.base_speed = PLAYER3_ATTR['speed']
            animation_sheet_path = PLAYER3_ATTR['animation_sheet']
            
        

        # Atribui a vida com base na vida máxima definida
        self.life = self.max_life

        # O resto do código continua como estava, usando as variáveis definidas acima
        # Carrega a spritesheet correta para o personagem selecionado
        self.character_spritesheet = Spritesheet(animation_sheet_path)
        
        # Propriedades básicas
        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES
        self.x_change = 0
        self.y_change = 0
        self.facing = 'down'
        self.coins = 10

        #lentidão agua
        self.slow_modifier = 0.5  # Reduz a velocidade pela metade na água
        self.is_in_water = False
        self.last_water_damage_time = 0  # Controla se está na água
        # Sistema de flechas especiais para o arqueiro
        self.special_arrows_active = False
        self.special_arrows_start_time = 0
        self.last_special_arrows_time = -SPECIAL_ARROW_COOLDOWN
        # Sistema de cooldown

        self.last_attack_time = 0
        self.last_dodge_time = 0
        self.is_dodging = False
        self.dodge_duration = 500
        self.dodge_speed_multiplier = 10
        
        # Sistema de escudo para o boxeador
        self.shield_active = False
        self.shield_start_time = 0
        self.last_shield_time = -SHIELD_COOLDOWN  # Permite usar imediatamente
        self.shield_image = self.game.shield_spritesheet.get_sprite(1, 1, 40, 40)

        # Dodge Bar (esquiva)
        self.dodge_cooldown = DODGE_COOLDOWN
        self.last_dodge_time = -DODGE_COOLDOWN  
        
        # Sistema de animação
        self.animation_speed = 10
        self.animation_counter = 0
        self.current_frame = 0
        
        # Carregar animações
        self.load_animations()
        
        # Imagem inicial
        self.image = self.animation_frames['down'][0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.life = self.max_life # Adicione esta linha
        self.invulnerable = False
        self.invulnerable_time = 0
        self.damage = 1  # Dano base
        self.speed_boost = 0  # Bônus de velocidade
        self.attack_cooldown_multiplier = 1.0  # Multiplicador de cooldown
        self.dodge_cooldown_multiplier = 1.0  # Multiplicador de cooldown

    def draw_health_bar(self, surface, offset=(0, 0)):
        bar_x = self.rect.x + offset[0] + (self.rect.width // 2) - (HEALTH_BAR_WIDTH // 2)
        bar_y = self.rect.y + offset[1] - HEALTH_BAR_OFFSET
        
        border_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        bg_rect = border_rect.inflate(-2, -2)

        health_ratio = self.life / self.max_life
        if health_ratio > 0.6:
            health_color = HEALTH_COLOR_HIGH
        elif health_ratio > 0.3:
            health_color = HEALTH_COLOR_MEDIUM
        else:
            health_color = HEALTH_COLOR_LOW

        health_width = int(bg_rect.width * health_ratio)
        health_rect = pygame.Rect(bg_rect.x, bg_rect.y, health_width, bg_rect.height)
        
        pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, border_rect)
        pygame.draw.rect(surface, HEALTH_BAR_BG_COLOR, bg_rect)
        if health_width > 0:
            pygame.draw.rect(surface, health_color, health_rect)

    def take_damage(self, amount=1):
        if not self.invulnerable and not self.shield_active:
            self.life -= amount
            self.invulnerable = True
            self.invulnerable_time = pygame.time.get_ticks()
            if self.life <= 0:
                self.kill()
    def activate_special_arrows(self):
        if self.char_type == 'archer' and pygame.time.get_ticks() - self.last_special_arrows_time >= SPECIAL_ARROW_COOLDOWN:
            self.special_arrows_active = True
            self.special_arrows_start_time = pygame.time.get_ticks()
            self.last_special_arrows_time = pygame.time.get_ticks()
            return True
        return False

    def update_special_arrows(self):
        current_time = pygame.time.get_ticks()
        if self.special_arrows_active and current_time - self.special_arrows_start_time >= SPECIAL_ARROW_DURATION:
            self.special_arrows_active = False

    def activate_shield(self):
        current_time = pygame.time.get_ticks()
        if self.char_type == 'boxer' and current_time - self.last_shield_time >= SHIELD_COOLDOWN:
            self.shield_active = True
            self.shield_start_time = current_time
            self.last_shield_time = current_time
            return True
        return False

    def update_shield(self):
        current_time = pygame.time.get_ticks()
        if self.shield_active and current_time - self.shield_start_time >= SHIELD_DURATION:
            self.shield_active = False

    def can_attack(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack_time >= ATTACK_COOLDOWN * self.attack_cooldown_multiplier

        cooldown = ARROW_COOLDOWN if self.char_type == 'archer' else ATTACK_COOLDOWN
        return current_time - self.last_attack_time >= cooldown * self.attack_cooldown_multiplier
        
    def can_dodge(self):
        if self.char_type != 'swordsman':
            return False
        return pygame.time.get_ticks() - self.last_dodge_time >= self.dodge_cooldown * self.dodge_cooldown_multiplier

    def get_attack_cooldown_ratio(self):
        elapsed = pygame.time.get_ticks() - self.last_attack_time
        return min(elapsed / (ATTACK_COOLDOWN * self.attack_cooldown_multiplier), 1.0)

        cooldown = ARROW_COOLDOWN if self.char_type == 'archer' else ATTACK_COOLDOWN
        return min(elapsed / (cooldown * self.attack_cooldown_multiplier), 1.0)

    def get_dodge_cooldown_ratio(self):
        elapsed = pygame.time.get_ticks() - self.last_dodge_time
        return min(elapsed / (self.dodge_cooldown * self.dodge_cooldown_multiplier), 1.0)
    
    def load_animations(self):
        # AGORA USA a character_spritesheet que foi carregada para o personagem específico
        self.animation_frames = {
            'left': [
                self.character_spritesheet.get_sprite(3, 98, self.width, self.height),
                self.character_spritesheet.get_sprite(35, 98, self.width, self.height),
                self.character_spritesheet.get_sprite(68, 98, self.width, self.height)
            ],
            'right': [
                self.character_spritesheet.get_sprite(3, 66, self.width, self.height),
                self.character_spritesheet.get_sprite(35, 66, self.width, self.height),
                self.character_spritesheet.get_sprite(68, 66, self.width, self.height)
            ],
            'up': [
                self.character_spritesheet.get_sprite(3, 35, self.width, self.height),
                self.character_spritesheet.get_sprite(35, 35, self.width, self.height),
                self.character_spritesheet.get_sprite(68, 35, self.width, self.height)
            ],
            'down': [
                self.character_spritesheet.get_sprite(3, 2, self.width, self.height),
                self.character_spritesheet.get_sprite(35, 2, self.width, self.height),
                self.character_spritesheet.get_sprite(65, 2, self.width, self.height)
            ]
        }

    def animate(self):
        self.animation_counter += 1
        
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            frames = self.animation_frames.get(self.facing, [self.image])
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]
            self.image.set_colorkey(BLACK)
            
            # Atualiza rect mantendo a posição
            old_center = self.rect.center if hasattr(self, 'rect') else (self.x, self.y)
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def handle_water(self):
        #""Verifica colisão com água e aplica efeitos (lentidão + dano)."""
        # Define uma "área de colisão" apenas na parte inferior do jogador
        bottom_half_rect = pygame.Rect(
            self.rect.left,
            self.rect.centery,
            self.rect.width,
            self.rect.height / 2
        )

        self.is_in_water = any(water.rect.colliderect(bottom_half_rect) for water in self.game.water)

        
        # Aplica dano de 1 por segundo
        if self.is_in_water:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_water_damage_time >= 1700:  # 1.7segundo
                self.take_damage()
                self.last_water_damage_time = current_time

    def update(self):
        self.update_shield()
        self.update_special_arrows()
        self.movement()
        self.animate()
        self.handle_water()
        self.collide_enemy()
        # Aplica o movimento
        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.x = self.rect.x

        self.rect.y += self.y_change
        self.collide_blocks('y')
        self.y = self.rect.y
        
        # Verifica se está na água e causa dano (1 por segundo)
        bottom_half_rect = pygame.Rect(
            self.rect.left,
            self.rect.centery,
            self.rect.width,
            self.rect.height / 2
        )
        if any(water.rect.colliderect(bottom_half_rect) for water in self.game.water):

            current_time = pygame.time.get_ticks()
            if not hasattr(self, 'last_water_damage_time'):
                self.last_water_damage_time = current_time
            if current_time - self.last_water_damage_time >= 150:  # 1/2 segundo
                self.take_damage()
                self.last_water_damage_time = current_time
        if self.life <= 0:
            self.kill()
            return  # Impede que o resto do update seja executado para um jogador morto

        
        # Remove invulnerabilidade após 1 segundo
        if self.invulnerable and pygame.time.get_ticks() - self.invulnerable_time > 1000:
            self.invulnerable = False
        
        # Reseta os valores de movimento após cada frame
        self.x_change = 0
        self.y_change = 0

    def movement(self):
        shop_active = any(isinstance(npc, Seller2NPC) and npc.shop_active for npc in self.game.npcs)
        if shop_active:
            return

        keys = pygame.key.get_pressed()
        self.x_change, self.y_change = 0, 0
        
        current_speed = (self.base_speed + self.speed_boost) * (self.slow_modifier if self.is_in_water else 1)

        # Teclado
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x_change -= current_speed
            self.facing = 'left'
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x_change += current_speed
            self.facing = 'right'
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y_change -= current_speed
            self.facing = 'up'
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y_change += current_speed
            self.facing = 'down'
        
        # Joystick
        if hasattr(self.game, 'joystick') and self.game.joystick:
            axis_x = self.game.joystick.get_axis(0)
            axis_y = self.game.joystick.get_axis(1)
            deadzone = 0.3
            if abs(axis_x) > deadzone:
                self.x_change += axis_x * current_speed
                self.facing = 'right' if axis_x > 0 else 'left'
            if abs(axis_y) > deadzone:
                self.y_change += axis_y * current_speed
                self.facing = 'down' if axis_y > 0 else 'up'
        
        # Esquiva (para espadachim) ou Escudo (para boxeador)
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            if self.char_type == 'swordsman' and self.can_dodge():
                self.last_dodge_time = pygame.time.get_ticks()
                self.x_change *= self.dodge_speed_multiplier
                self.y_change *= self.dodge_speed_multiplier
           
            elif self.char_type == 'archer':
                self.activate_special_arrows()
           
            elif self.char_type == 'boxer':
                self.activate_shield()
                
        if hasattr(self.game, 'joystick') and self.game.joystick:
            if self.game.joystick.get_button(2):  # Botão X (Xbox) ou Quadrado (PS)
                if self.char_type == 'swordsman' and self.can_dodge():
                    self.last_dodge_time = pygame.time.get_ticks()
                    self.x_change *= self.dodge_speed_multiplier
                    self.y_change *= self.dodge_speed_multiplier
                elif self.char_type == 'boxer':
                    self.activate_shield()


    def kill(self):
        super().kill()
        self.game.playing = False


    def collide_enemy(self):
    # Verifica colisão com inimigos normais e morcegos
        hits_enemies = pygame.sprite.spritecollide(self, self.game.enemies, False)
        hits_bats = pygame.sprite.spritecollide(self, self.game.bats, False)
        
        # Se colidiu com qualquer inimigo e não está invulnerável
        if (hits_enemies or hits_bats) and not self.invulnerable:
            self.take_damage()
    def collide_blocks(self, direction):
    # Colisão apenas com blocos normais (não inclui água)
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        
        if direction == "x" and hits:
            if self.x_change > 0:
                self.rect.x = hits[0].rect.left - self.rect.width
                for sprite in self.game.all_sprites:
                    sprite.rect.x += self.base_speed
            if self.x_change < 0:
                self.rect.x = hits[0].rect.right
                for sprite in self.game.all_sprites:
                    sprite.rect.x -= self.base_speed

        if direction == "y" and hits:
            if self.y_change > 0:
                self.rect.y = hits[0].rect.top - self.rect.height
                for sprite in self.game.all_sprites:
                    sprite.rect.y += self.base_speed
            if self.y_change < 0:
                self.rect.y = hits[0].rect.bottom
                for sprite in self.game.all_sprites:
                    sprite.rect.y -= self.base_speed
    
    def collide_obstacle (self, direction):
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.obstacle, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                    for sprite in self.game.all_sprites:
                        sprite.rect.x += self.base_speed
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                    for sprite in self.game.all_sprites:
                        sprite.rect.x -= self.base_speed

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.obstacle, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                    for sprite in self.game.all_sprites:
                        sprite.rect.y += self.base_speed
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                    for sprite in self.game.all_sprites:
                        sprite.rect.y -= self.base_speed

        
    def activate_shield(self):
        current_time = pygame.time.get_ticks()
        if self.char_type == 'boxer' and current_time - self.last_shield_time >= SHIELD_COOLDOWN:
            self.shield_active = True
            self.shield_start_time = current_time
            self.last_shield_time = current_time
            Shield(self.game, self)  # <-- ADICIONE ESTA LINHA para criar o sprite do escudo
            return True
        return False

#GROUNDS
class Snowflake(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self._layer = 8 # Uma camada alta para ficar sobre os outros elementos
        self.groups = self.game.all_sprites, self.game.snowflakes
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = random.randrange(0, WIN_WIDTH)
        self.y = random.randrange(-50, -10)
        self.width = self.height = random.randint(2, 5)

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE_SNOW)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WIN_HEIGHT:
            self.rect.x = random.randrange(0, WIN_WIDTH)
            self.rect.y = random.randrange(-50, -10)

class Ground1(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Posição do tile
        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES
        
        # Diferentes sprites para cada tilemap
        self.tilemap_sprites = {
            1: game.terrain_spritesheet.get_sprite(0, 352, self.width, self.height),
            2: game.terrain_spritesheet.get_sprite(256, 352, self.width+6, self.height),
            3: game.terrain_spritesheet.get_sprite(925, 703, self.width+6, self.height),
            4: game.terrain_spritesheet.get_sprite(576, 544, self.width+4, self.height)
        }
        
        # Carrega o sprite baseado no nível atual
        self.update_sprite()
        
        # Define o retângulo de colisão
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update_sprite(self):
        """Atualiza o sprite baseado no nível atual"""
        self.image = self.tilemap_sprites.get(self.game.current_level, 
                                            self.tilemap_sprites[1])  # Default para tilemap1
    
    def update(self):
        """Atualiza o sprite se o nível mudar"""
        self.update_sprite()

class Water1(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites, self.game.water
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES
        
        # Carrega os frames de animação para cada nível
        self.tilemap_animations = {
            1: [
                game.terrain_spritesheet.get_sprite(0, 352, self.width, self.height),
                game.terrain_spritesheet.get_sprite(32, 352, self.width, self.height),
                game.terrain_spritesheet.get_sprite(64, 352, self.width, self.height)
            ],
            2: [
                game.terrain_spritesheet.get_sprite(864, 160, self.width, self.height),
                game.terrain_spritesheet.get_sprite(894, 160, self.width, self.height),
                game.terrain_spritesheet.get_sprite(924,160, self.width, self.height)
            ]
        }
        
        # Configuração da animação
        self.current_frame = 0
        self.animation_speed = 0.6  # Velocidade da animação (ajuste conforme necessário)
        self.animation_counter = 0
        
        self.update_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update_sprite(self):
        """Atualiza o sprite baseado no nível atual"""
        frames = self.tilemap_animations.get(self.game.current_level, 
                                          self.tilemap_animations[1])  # Default para nível 1
        self.image = frames[self.current_frame]
    
    def animate(self):
        """Atualiza a animação da água"""
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed * 60:  # 60 FPS
            self.animation_counter = 0
            frames = self.tilemap_animations.get(self.game.current_level, 
                                              self.tilemap_animations[1])
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]
    
    def update(self):
        """Atualiza o sprite e a animação"""
        self.animate()
        self.update_sprite()

class Plant(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Posição da planta
        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES

        # Diferentes sprites para cada nível
        self.level_sprites = {
            1: self.game.plant_spritesheet.get_sprite(510, 352, self.width, self.height),
            2: self.game.plant_spritesheet.get_sprite(352, 544, self.width, self.height),
            3: self.game.plant_spritesheet.get_sprite(993, 515, self.width, self.height),
            4: self.game.plant_spritesheet.get_sprite(581, 421, self.width, self.height) # Exemplo com coordenadas diferentes
        }
        
        self.update_sprite()
        self.image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update_sprite(self):
        """Atualiza o sprite baseado no nível atual"""
        self.image = self.level_sprites.get(self.game.current_level, 
                                          self.level_sprites[1])  # Default para nível 1
    
    def update(self):
        """Atualiza o sprite se o nível mudar"""
        self.update_sprite()

class Portal(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PORTAL_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES
        
        self.activated = False
        self.active = False  # Começa inativo
        self.pulse_effect = 0
        self.pulse_speed = 0.05
        self.pulse_max = 0.2

        # Carrega as animações do portal
        self.animation_frames = [
            self.game.portal_spritsheet.get_sprite(18, 15, self.width, 45),
            self.game.portal_spritsheet.get_sprite(83, 15, self.width, 45),
            self.game.portal_spritsheet.get_sprite(150, 15, self.width, 45)
        ]
        
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        
        self.image = self.animation_frames[self.current_frame]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.animate()
        if self.active and hasattr(self.game, 'player') and not self.activated:
            if pygame.sprite.collide_rect(self, self.game.player):
                self.activated = True
                # Chama next_level diretamente após um pequeno delay
                pygame.time.delay(300)  # Pequeno delay para efeito visual
                self.game.next_level()
                return True
        return False  # Dispara evento após 300ms

    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed * 60:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]
            self.image.set_colorkey(BLACK)
            
        # Efeito de pulsação quando ativo
        if self.active:
            self.pulse_effect = (self.pulse_effect + self.pulse_speed) % (2 * math.pi)
            scale = 1 + math.sin(self.pulse_effect) * self.pulse_max
            old_center = self.rect.center
            self.image = pygame.transform.scale(self.animation_frames[self.current_frame], 
                                             (int(self.width * scale), int(self.height * scale)))
            self.rect = self.image.get_rect(center=old_center)

class Bat(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.life = BAT_LIFE
        self.speed = BAT_SPEED
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.bats
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES

        self.x_change = 0
        self.y_change = 0
        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.movement_loop = 0  # Inicialização correta da variável
        self.max_travel = random.randint(7, 30)

        # Animação
        self.animation_frames = {
            'left': [
                self.game.bats_spritesheet.get_sprite(5, 40, self.width-2, self.height-2),
                self.game.bats_spritesheet.get_sprite(33, 40, self.width-2, self.height-2)
            ],
            'right': [
                self.game.bats_spritesheet.get_sprite(2, 8, self.width-2, self.height-2),
                self.game.bats_spritesheet.get_sprite(33, 8, self.width-2, self.height-2)
           ],
            'up': [
                self.game.bats_spritesheet.get_sprite(2, 8, self.width-2, self.height-2),
                self.game.bats_spritesheet.get_sprite(33, 8, self.width-2, self.height-2)
            ],
            'down' :[
                self.game.bats_spritesheet.get_sprite(5, 40, self.width-2, self.height-2),
                self.game.bats_spritesheet.get_sprite(33, 40, self.width-2, self.height-2)
            ]
        }
        self.current_frame = 0
        self.animation_speed = 5
        self.animation_counter = 0

        self.image = self.animation_frames[self.facing][self.current_frame]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def draw_health_bar(self, surface, offset=(0, 0)):
        if self.life == BAT_LIFE: return # Não desenha a barra com vida cheia
        bar_x = self.rect.x + offset[0] + (self.rect.width // 2) - (HEALTH_BAR_WIDTH // 2)
        bar_y = self.rect.y + offset[1] - HEALTH_BAR_OFFSET

        border_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        bg_rect = border_rect.inflate(-2, -2)

        health_ratio = self.life / BAT_LIFE
        if health_ratio > 0.6: health_color = HEALTH_COLOR_HIGH
        elif health_ratio > 0.3: health_color = HEALTH_COLOR_MEDIUM
        else: health_color = HEALTH_COLOR_LOW

        health_width = int(bg_rect.width * health_ratio)
        health_rect = pygame.Rect(bg_rect.x, bg_rect.y, health_width, bg_rect.height)

        pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, border_rect)
        pygame.draw.rect(surface, HEALTH_BAR_BG_COLOR, bg_rect)
        if health_width > 0:
            pygame.draw.rect(surface, health_color, health_rect)

    def take_damage(self, amount):
        self.life -= amount
        if self.life <= 0:
            self.kill()

    def update(self):
        self.movement()
        self.animate()  # Atualiza a animação
        
        # Aplica o movimento antes de verificar colisões
        self.rect.x += self.x_change
        self.collide_blocks('x')
        
        self.rect.y += self.y_change
        self.collide_blocks('y')
        
        # Verifica se o inimigo morreu
        if self.life <= 0:
            self.kill()
    def kill(self):
    # Remove o inimigo de todos os grupos
        for group in self.groups:
            group.remove(self)
        
        # Verifica se todos os inimigos foram derrotados
        if len(self.game.bats ) == 0:
            # Spawna o portal se não existir
            self.game.check_enemies_and_spawn_portal()

    def movement(self):
        if self.facing == 'left':
            self.x_change = -ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel:
                self.facing = random.choice(['up', 'down', 'right'])

        if self.facing == 'up':
            self.y_change = -ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel:
                self.facing = random.choice(['right', 'left', 'down'])
                 
        if self.facing == 'down':
            self.y_change = ENEMY_SPEED
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel:
                self.facing = random.choice(['up', 'left', 'right'])

        if self.facing == 'right':
            self.x_change = ENEMY_SPEED 
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel:
                self.facing = random.choice(['up', 'down', 'left'])

    def animate(self):
        # Alterna entre os frames de animação
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames[self.facing])
            self.image = self.animation_frames[self.facing][self.current_frame]

    def collide_blocks(self, direction):
        # Colisão com blocos normais e água
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        water_hits = pygame.sprite.spritecollide(self, self.game.water, False)
        all_hits = hits + water_hits
        
        if direction == "x" and all_hits:
            self.speed = ENEMY_SPEED / 2
            if self.x_change > 0:
                self.rect.right = all_hits[0].rect.left
                self.facing = random.choice(['up', 'down', 'left'])
            if self.x_change < 0:
                self.rect.left = all_hits[0].rect.right
                self.facing = random.choice(['up', 'down', 'right'])

        if direction == "y" and all_hits:
            self.speed = ENEMY_SPEED / 2
            if self.y_change > 0:
                self.rect.bottom = all_hits[0].rect.top
                self.facing = random.choice(['up', 'left', 'right'])
            if self.y_change < 0:
                self.rect.top = all_hits[0].rect.bottom
                self.facing = random.choice(['down', 'left', 'right'])

class enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.life = ENEMY_LIFE
        self.speed = ENEMY_SPEED
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES

        self.x_change = 0
        self.y_change = 0
        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.movement_loop = 0  # Inicialização correta da variável
        self.max_travel = random.randint(7, 30)

        # Animação
        self.animation_frames = {
            'left': [
                self.game.enemy_spritesheet.get_sprite(3, 98, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(35, 98, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(68, 98, self.width, self.height)
            ],
            'right': [
                self.game.enemy_spritesheet.get_sprite(3, 66, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(35, 66, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(68, 66, self.width, self.height)
           ],
            'up': [
                self.game.enemy_spritesheet.get_sprite(3, 35, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(35, 35, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(68, 35, self.width, self.height)
            ],
            'down' :[
                self.game.enemy_spritesheet.get_sprite(3, 3, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(35, 3, self.width, self.height),
                self.game.enemy_spritesheet.get_sprite(68, 3, self.width, self.height)
            ]
        }
        self.current_frame = 0
        self.animation_speed = 5
        self.animation_counter = 0

        self.image = self.animation_frames[self.facing][self.current_frame]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    def draw_health_bar(self, surface, offset=(0, 0)):
        if self.life == ENEMY_LIFE: return
        bar_x = self.rect.x + offset[0] + (self.rect.width // 2) - (HEALTH_BAR_WIDTH // 2)
        bar_y = self.rect.y + offset[1] - HEALTH_BAR_OFFSET
        border_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        bg_rect = border_rect.inflate(-2, -2)
        health_ratio = self.life / ENEMY_LIFE
        health_color = HEALTH_COLOR_LOW # Inimigos comuns sempre mostram vida vermelha
        health_width = int(bg_rect.width * health_ratio)
        health_rect = pygame.Rect(bg_rect.x, bg_rect.y, health_width, bg_rect.height)
        pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, border_rect)
        pygame.draw.rect(surface, HEALTH_BAR_BG_COLOR, bg_rect)
        if health_width > 0:
            pygame.draw.rect(surface, health_color, health_rect)

    def take_damage(self, amount):
        self.life -= amount
        if self.life <= 0:
            self.kill()

    def update(self):
        self.movement()
        self.animate()  # Atualiza a animação
        
        # Aplica o movimento antes de verificar colisões
        self.rect.x += self.x_change
        self.collide_blocks('x')
        
        self.rect.y += self.y_change
        self.collide_blocks('y')
        
        # Verifica se o inimigo morreu
        if self.life <= 0:
            self.kill()
    def kill(self):
    # Remove o inimigo de todos os grupos
        for group in self.groups:
            group.remove(self)
        
        # Verifica se todos os inimigos foram derrotados
        if len(self.game.enemies) == 0:
            # Spawna o portal se não existir
            self.game.check_enemies_and_spawn_portal()

    def movement(self):
        # Verifica se o jogador existe para evitar erros
        if not hasattr(self.game, 'player'):
            return

        player_pos = self.game.player.rect.center
        enemy_pos = self.rect.center
        distance = math.hypot(player_pos[0] - enemy_pos[0], player_pos[1] - enemy_pos[1])
        
        detection_radius = 256  # Raio de detecção de 256px

        if distance < detection_radius:
            # O jogador está no alcance, move-se em direção a ele
            dx = player_pos[0] - enemy_pos[0]
            dy = player_pos[1] - enemy_pos[1]
            
            # Normaliza o vetor de direção
            norm = math.sqrt(dx**2 + dy**2)
            if norm != 0:
                # Define a mudança de posição com base na velocidade do inimigo
                self.x_change = (dx / norm) * self.speed
                self.y_change = (dy / norm) * self.speed
            
            # Atualiza a direção do sprite para a animação correta
            if abs(dx) > abs(dy):
                self.facing = 'right' if dx > 0 else 'left'
            else:
                self.facing = 'down' if dy > 0 else 'up'
        else:
            # O jogador está fora do alcance, usa o movimento aleatório original
            self.x_change = 0
            self.y_change = 0
            
            if self.facing == 'left':
                self.x_change = -self.speed
                self.movement_loop -= 1
                if self.movement_loop <= -self.max_travel:
                    self.movement_loop = 0
                    self.facing = random.choice(['up', 'down', 'right'])

            elif self.facing == 'right':
                self.x_change = self.speed
                self.movement_loop += 1
                if self.movement_loop >= self.max_travel:
                    self.movement_loop = 0
                    self.facing = random.choice(['up', 'down', 'left'])

            elif self.facing == 'up':
                self.y_change = -self.speed
                self.movement_loop -= 1
                if self.movement_loop <= -self.max_travel:
                    self.movement_loop = 0
                    self.facing = random.choice(['right', 'left', 'down'])
                     
            elif self.facing == 'down':
                self.y_change = self.speed
                self.movement_loop += 1
                if self.movement_loop >= self.max_travel:
                    self.movement_loop = 0
                    self.facing = random.choice(['up', 'left', 'right'])

    def animate(self):
        # Alterna entre os frames de animação
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames[self.facing])
            self.image = self.animation_frames[self.facing][self.current_frame]

    def collide_blocks(self, direction):
        # Colisão com blocos normais e água
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        water_hits = pygame.sprite.spritecollide(self, self.game.water, False)
        all_hits = hits + water_hits
        
        if direction == "x" and all_hits:
            self.speed = ENEMY_SPEED / 2
            if self.x_change > 0:
                self.rect.right = all_hits[0].rect.left
                self.facing = random.choice(['up', 'down', 'left'])
            if self.x_change < 0:
                self.rect.left = all_hits[0].rect.right
                self.facing = random.choice(['up', 'down', 'right'])

        if direction == "y" and all_hits:
            self.speed = ENEMY_SPEED / 2
            if self.y_change > 0:
                self.rect.bottom = all_hits[0].rect.top
                self.facing = random.choice(['up', 'left', 'right'])
            if self.y_change < 0:
                self.rect.top = all_hits[0].rect.bottom
                self.facing = random.choice(['down', 'left', 'right'])

        

class EnemyCoin(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.life = ENEMY_LIFE
        self.speed = ENEMY_SPEED
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES

        self.x_change = 0
        self.y_change = 0
        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.movement_loop = 0  # Inicialização correta da variável
        self.max_travel = random.randint(7, 30)

        # Animação
        self.animation_frames = {
            'left': [
                self.game.enemycoin_spritesheet.get_sprite(3, 98, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(35, 98, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(68, 98, self.width, self.height)
            ],
            'right': [
                self.game.enemycoin_spritesheet.get_sprite(3, 66, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(35, 66, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(68, 66, self.width, self.height)
           ],
            'up': [
                self.game.enemycoin_spritesheet.get_sprite(3, 35, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(35, 35, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(68, 35, self.width, self.height)
            ],
            'down' :[
                self.game.enemycoin_spritesheet.get_sprite(3, 3, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(35, 3, self.width, self.height),
                self.game.enemycoin_spritesheet.get_sprite(68, 3, self.width, self.height)
            ]
        }
        self.current_frame = 0
        self.animation_speed = 10
        self.animation_counter = 0

        self.image = self.animation_frames[self.facing][self.current_frame]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    def draw_health_bar(self, surface, offset=(0, 0)):
        if self.life == ENEMY_LIFE: return
        bar_x = self.rect.x + offset[0] + (self.rect.width // 2) - (HEALTH_BAR_WIDTH // 2)
        bar_y = self.rect.y + offset[1] - HEALTH_BAR_OFFSET
        border_rect = pygame.Rect(bar_x, bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        bg_rect = border_rect.inflate(-2, -2)
        health_ratio = self.life / ENEMY_LIFE
        health_color = HEALTH_COLOR_LOW # Inimigos comuns sempre mostram vida vermelha
        health_width = int(bg_rect.width * health_ratio)
        health_rect = pygame.Rect(bg_rect.x, bg_rect.y, health_width, bg_rect.height)
        pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, border_rect)
        pygame.draw.rect(surface, HEALTH_BAR_BG_COLOR, bg_rect)
        if health_width > 0:
            pygame.draw.rect(surface, health_color, health_rect)

    def take_damage(self, amount):
        self.life -= amount
        if self.life <= 0:
            self.kill()

    def update(self):
        self.movement()
        self.animate()  # Atualiza a animação
        
        # Aplica o movimento antes de verificar colisões
        self.rect.x += self.x_change
        self.collide_blocks('x')
        
        self.rect.y += self.y_change
        self.collide_blocks('y')
        
        # Verifica se o inimigo morreu
        if self.life <= 0:
            self.kill()
    def kill(self):
    # Remove o inimigo de todos os grupos
        for group in self.groups:
            group.remove(self)
        # Dropa uma moeda quando morre
        Coin(self.game, self.rect.centerx, self.rect.centery)
        # Verifica se todos os inimigos foram derrotados
        if len(self.game.enemies) == 0:
            # Spawna o portal se não existir
            self.game.check_enemies_and_spawn_portal()

    def movement(self):
        if self.facing == 'left':
            self.x_change = -ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel:
                self.facing = random.choice(['up', 'down', 'right'])

        if self.facing == 'up':
            self.y_change = -ENEMY_SPEED
            self.movement_loop -= 1
            if self.movement_loop <= -self.max_travel:
                self.facing = random.choice(['right', 'left', 'down'])
                 
        if self.facing == 'down':
            self.y_change = ENEMY_SPEED
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel:
                self.facing = random.choice(['up', 'left', 'right'])

        if self.facing == 'right':
            self.x_change = ENEMY_SPEED 
            self.movement_loop += 1
            if self.movement_loop >= self.max_travel:
                self.facing = random.choice(['up', 'down', 'left'])

    def animate(self):
        # Alterna entre os frames de animação
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames[self.facing])
            self.image = self.animation_frames[self.facing][self.current_frame]

    def collide_blocks(self, direction):
    # Colisão com blocos normais e água
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        water_hits = pygame.sprite.spritecollide(self, self.game.water, False)
        all_hits = hits + water_hits
        
        if direction == "x" and all_hits:
            self.speed = ENEMY_SPEED / 2
            if self.x_change > 0:
                self.rect.right = all_hits[0].rect.left
                self.facing = random.choice(['up', 'down', 'left'])
            if self.x_change < 0:
                self.rect.left = all_hits[0].rect.right
                self.facing = random.choice(['up', 'down', 'right'])

        if direction == "y" and all_hits:
            self.speed = ENEMY_SPEED / 2
            if self.y_change > 0:
                self.rect.bottom = all_hits[0].rect.top
                self.facing = random.choice(['up', 'left', 'right'])
            if self.y_change < 0:
                self.rect.top = all_hits[0].rect.bottom
                self.facing = random.choice(['down', 'left', 'right'])

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Posição do bloco
        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES

        # Define a aparência do bloco
        self.image = self.game.block_spritesheet.get_sprite(960, 448, self.width, self.height)
        self.image.set_colorkey(BLACK)

        # Define o retângulo de colisão
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class AbilityPanel:
    def __init__(self, game):
        self.game = game
        self.rect = pygame.Rect(ABILITY_PANEL_X, ABILITY_PANEL_Y, ABILITY_PANEL_WIDTH, ABILITY_PANEL_HEIGHT)
        
        self.title_font = pygame.font.SysFont('arial', ABILITY_TITLE_FONT_SIZE, bold=True)
        self.text_font = pygame.font.SysFont('arial', ABILITY_FONT_SIZE)
        self.coin_icon = self.game.coin.get_sprite(9, 5, 16, 16)
        
    def draw(self, surface):
        if not hasattr(self.game, 'player'): return
        
        # Desenha borda e fundo do painel
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect)
        bg_rect = self.rect.inflate(-UI_BORDER_WIDTH * 2, -UI_BORDER_WIDTH * 2)
        pygame.draw.rect(surface, ABILITY_PANEL_COLOR, bg_rect)
        
        # Título
        title = self.title_font.render("Habilidades", True, UI_FONT_COLOR)
        surface.blit(title, (self.rect.x + 15, self.rect.y + 15))
        
        y_offset = 60
        # Ataque
        attack_key = self.text_font.render("Ataque [ESPAÇO]", True, UI_FONT_COLOR)
        surface.blit(attack_key, (self.rect.x + 15, self.rect.y + y_offset))
        self.draw_attack_bar(surface, self.rect.x + 15, self.rect.y + y_offset + 25)

        # Esquiva
        y_offset += 60
        if self.game.player.char_type == 'boxer':
            ability_key = self.text_font.render("Escudo [SHIFT]", True, UI_FONT_COLOR)
            surface.blit(ability_key, (self.rect.x + 15, self.rect.y + y_offset))
            self.draw_shield_bar(surface, self.rect.x + 15, self.rect.y + y_offset + 25)
            #%
        elif self.game.player.char_type == 'archer':
            ability_key = self.text_font.render("Flechas Especiais [SHIFT]", True, UI_FONT_COLOR)
            surface.blit(ability_key, (self.rect.x + 15, self.rect.y + y_offset))
            self.draw_special_arrows_bar(surface, self.rect.x + 15, self.rect.y + y_offset + 25)
            #%
        else:
            ability_key = self.text_font.render("Esquiva [SHIFT]", True, UI_FONT_COLOR)
            surface.blit(ability_key, (self.rect.x + 15, self.rect.y + y_offset))
            self.draw_dodge_bar(surface, self.rect.x + 15, self.rect.y + y_offset + 25)


        # Moedas
        y_offset += 45
        surface.blit(self.coin_icon, (self.rect.x + 15, self.rect.y + y_offset + 2))
        coin_text = self.text_font.render(f": {self.game.player.coins}", True, UI_TITLE_COLOR)
        surface.blit(coin_text, (self.rect.x + 35, self.rect.y + y_offset))

    def draw_special_arrows_bar(self, surface, x, y):
        if not hasattr(self.game.player, 'last_special_arrows_time'):
            ratio = 0
        else:
            elapsed = pygame.time.get_ticks() - self.game.player.last_special_arrows_time
            ratio = min(elapsed / SPECIAL_ARROW_COOLDOWN, 1.0)
        
        self.draw_bar(surface, x, y, ratio, DODGE_READY_COLOR, DODGE_COOLDOWN_COLOR)
        
        # Mostra tempo restante das flechas especiais se estiverem ativas
        if hasattr(self.game.player, 'special_arrows_active') and self.game.player.special_arrows_active:
            remaining = (SPECIAL_ARROW_DURATION - (pygame.time.get_ticks() - self.game.player.special_arrows_start_time)) / 1000
            time_text = self.text_font.render(f"{remaining:.1f}s", True, WHITE)
            surface.blit(time_text, (x + BAR_WIDTH + 10, y))

    def draw_shield_bar(self, surface, x, y):
        if not hasattr(self.game.player, 'shield_active'):
            ratio = 0
        else:
            elapsed = pygame.time.get_ticks() - self.game.player.last_shield_time
            ratio = min(elapsed / SHIELD_COOLDOWN, 1.0)
        
        self.draw_bar(surface, x, y, ratio, DODGE_READY_COLOR, DODGE_COOLDOWN_COLOR)
        
        # Mostra tempo restante do escudo se estiver ativo
        if hasattr(self.game.player, 'shield_active') and self.game.player.shield_active:
            remaining = (SHIELD_DURATION - (pygame.time.get_ticks() - self.game.player.shield_start_time)) / 1000
            time_text = self.text_font.render(f"{remaining:.1f}s", True, WHITE)
            surface.blit(time_text, (x + BAR_WIDTH + 10, y))

    def draw_bar(self, surface, x, y, ratio, ready_color, cooldown_color):
        fill_width = int(BAR_WIDTH * ratio)
        color = ready_color if ratio >= 1.0 else cooldown_color
        
        border_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
        bg_rect = border_rect.inflate(-2, -2)
        fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_width, bg_rect.height)

        pygame.draw.rect(surface, HEALTH_BAR_BORDER_COLOR, border_rect)
        pygame.draw.rect(surface, BAR_BG_COLOR, bg_rect)
        pygame.draw.rect(surface, color, fill_rect)

    def draw_attack_bar(self, surface, x, y):
        ratio = self.game.player.get_attack_cooldown_ratio()
        self.draw_bar(surface, x, y, ratio, ATTACK_READY_COLOR, ATTACK_COOLDOWN_COLOR)

    def draw_dodge_bar(self, surface, x, y):
        ratio = self.game.player.get_dodge_cooldown_ratio()
        self.draw_bar(surface, x, y, ratio, DODGE_READY_COLOR, DODGE_COOLDOWN_COLOR)
        
        # Texto de status
        #status = "PRONTO" if ratio >= 1.0 else f"{int(ratio*100)}%"
        #status_text = self.small_font.render(status, True, WHITE)
        #surface.blit(status_text, (x + DODGE_BAR_WIDTH + 5, y))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = OBSTACLE_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Posição do obstáculo
        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES

        # Diferentes sprites para cada nível
        self.level_sprites = {
            1: self.game.obstacle_spritesheet.get_sprite(640, 203, self.width-4, self.height-4),  # Tronco
            2: self.game.obstacle_spritesheet.get_sprite(670, 260, self.width, self.height),
            3: self.game.plant_spritesheet.get_sprite(994, 545, self.width, self.height),
            4: self.game.plant_spritesheet.get_sprite(928, 480, self.width, self.height)
        }
        
        self.update_sprite()
        self.image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update_sprite(self):
        #""Atualiza o sprite baseado no nível atual"""
        self.image = self.level_sprites.get(self.game.current_level)  # Default para nível 1
    
    def update(self):
        """Atualiza o sprite se o nível mudar"""
        self.update_sprite()



class Button:
    def __init__(self, x ,y, width, height, fg, bg, content, fontsize):
        self.font = pygame.font.SysFont('arial.ttf', fontsize)
        self.content = content
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
        #%
class Nero(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BOSS_LAYER
        self.groups = self.game.all_sprites, self.game.bosses
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES * 2
        self.height = TILESIZES * 2

        self.life = NERO_LIFE
        self.max_life = NERO_LIFE
        self.speed = NERO_SPEED
        self.y_change = 0

        self.direction = 1  # 1 para baixo, -1 para cima

        self.has_spawned_minions = False

        self.attack_cooldown = 2000
        self.last_attack_time = pygame.time.get_ticks()
        
        # CORRIGIDO: Adiciona sistema de invulnerabilidade
        self.invulnerable = False
        self.invulnerable_time = 0
        self.invulnerability_duration = 250 # 0.25 segundos

        # Placeholder da imagem
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.attacking = False
        self.attack_type = None

    def update(self):
        now = pygame.time.get_ticks()
        
        # CORRIGIDO: Lógica de invulnerabilidade
        if self.invulnerable and now - self.invulnerable_time > self.invulnerability_duration:
            self.invulnerable = False

        self.movement()
        self.check_player_distance_and_attack()
        self.check_for_minion_spawn()
        # Aplica movimento e checa colisão
        self.rect.y += self.y_change
        self.collide_blocks('y') # CORRIGIDO: Checa colisão com paredes
        
        # Atualiza áreas de fogo
        for fire_area in self.game.fire_areas:
            fire_area.update()

        if self.life <= 0:
            self.kill()
    def check_for_minion_spawn(self):
        # Verifica se a vida está abaixo de 30% e se os inimigos ainda não foram invocados
        if (self.life / self.max_life) <= 0.5 and not self.has_spawned_minions:
            self.has_spawned_minions = True  # Garante que a invocação ocorra apenas uma vez
            
            for _ in range(5):
                # Calcula uma posição aleatória próxima ao Nero
                offset_x = random.randint(-TILESIZES * 3, TILESIZES * 3)
                offset_y = random.randint(-TILESIZES * 3, TILESIZES * 3)
                
                # Converte a posição de pixels para tiles, que é o formato esperado pelo construtor do inimigo
                spawn_x_tile = (self.rect.centerx + offset_x) // TILESIZES
                spawn_y_tile = (self.rect.centery + offset_y) // TILESIZES

                # Cria uma nova instância do inimigo comum
                enemy(self.game, spawn_x_tile, spawn_y_tile)
    def movement(self):
        # A direção é trocada quando colide, não baseada em posição fixa
        self.y_change = self.direction * self.speed

    # CORRIGIDO: Adicionado método de colisão com blocos
    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if direction == "y" and hits:
            if self.y_change > 0: # Movendo para baixo
                self.rect.bottom = hits[0].rect.top
                self.direction = -1 # Muda para cima
            if self.y_change < 0: # Movendo para cima
                self.rect.top = hits[0].rect.bottom
                self.direction = 1 # Muda para baixo
            self.y_change = 0


    def check_player_distance_and_attack(self):
        if not hasattr(self.game, 'player') or self.game.player.life <= 0 or self.attacking:
            return

        player_center = self.game.player.rect.center
        nero_center = self.rect.center
        distance = math.hypot(player_center[0] - nero_center[0], player_center[1] - nero_center[1])

        now = pygame.time.get_ticks()

        if now - self.last_attack_time > self.attack_cooldown:
            # Decide o ataque com base na distância
            attack_choice = random.choice(['whip', 'knife'])

            if attack_choice == 'knife' and distance <= NERO_KNIFE_RANGE:
                self.knife_attack()
            elif attack_choice == 'whip' and distance <= NERO_WHIP_RANGE:
                self.whip_attack()
            
            # Tenta o outro ataque se o primeiro não estiver no alcance
            elif distance <= NERO_WHIP_RANGE:
                 self.whip_attack()
            elif distance <= NERO_KNIFE_RANGE:
                 self.knife_attack()


    def whip_attack(self):
        self.attacking = True
        self.last_attack_time = pygame.time.get_ticks()
        
        if not hasattr(self.game, 'player'):
            self.attacking = False
            return
            
        player_pos = self.game.player.rect.center
        # Cria a área de fogo na posição do jogador
        FireArea(self.game, player_pos[0], player_pos[1], NERO_FIRE_DAMAGE, FIRE_AREA_LIFETIME, FIRE_DAMAGE_INTERVAL)
        
        self.attacking = False

    def knife_attack(self):
        self.attacking = True
        self.last_attack_time = pygame.time.get_ticks()

        if not hasattr(self.game, 'player'):
            self.attacking = False
            return

        player_center = self.game.player.rect.center
        nero_center = self.rect.center
        distance = math.hypot(player_center[0] - nero_center[0], player_center[1] - nero_center[1])

        if distance <= NERO_KNIFE_RANGE + 20: # Aumenta um pouco a área para garantir o acerto
            # CORRIGIDO: Usa o método take_damage do jogador
            self.game.player.take_damage(NERO_KNIFE_DAMAGE)
        
        self.attacking = False

    # CORRIGIDO: Lógica de dano e invulnerabilidade
    def take_damage(self, amount):
        if not self.invulnerable:
            self.life -= amount
            self.invulnerable = True
            self.invulnerable_time = pygame.time.get_ticks()

    def draw_health_bar(self):
        bar_x = self.rect.x
        bar_y = self.rect.y - 20
        bar_width = self.width
        bar_height = 15
        
        border_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        bg_rect = border_rect.inflate(-2, -2)

        health_ratio = self.life / self.max_life
        health_width = int(bg_rect.width * health_ratio)
        health_rect = pygame.Rect(bg_rect.x, bg_rect.y, health_width, bg_rect.height)
        
        pygame.draw.rect(self.game.screen, HEALTH_BAR_BORDER_COLOR, border_rect)
        pygame.draw.rect(self.game.screen, HEALTH_BAR_BG_COLOR, bg_rect)
        if health_width > 0:
            pygame.draw.rect(self.game.screen, HEALTH_COLOR_HIGH, health_rect)

class FireArea(pygame.sprite.Sprite):
    def __init__(self, game, x, y, damage, lifetime, damage_interval):
        self.game = game
        self._layer = GROUND_LAYER # Ou uma camada acima para visibilidade
        self.groups = self.game.all_sprites, self.game.fire_areas
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZES +32 # Tamanho da área de fogo
        self.height = TILESIZES +32

        self.damage = damage
        self.lifetime = lifetime
        self.damage_interval = damage_interval
        self.spawn_time = pygame.time.get_ticks()
        self.last_damage_time = pygame.time.get_ticks()

        # Representação: um quadrado laranja/vermelho
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.image.fill((255, 100, 0, 150)) # Laranja transparente
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        # Verifica o tempo de vida da área de fogo
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

        if hasattr(self.game, 'player') and self.rect.colliderect(self.game.player.rect):
            self.deal_damage()

    def deal_damage(self):
        now = pygame.time.get_ticks()
        if now - self.last_damage_time > self.damage_interval:
            self.game.player.life -= self.damage
            self.last_damage_time = now

class SwordAttack(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x
        self.y = y
        self.width = TILESIZES
        self.height = TILESIZES
        
        self.animation_loop = 0
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = self.game.player.facing

    def collide(self):
        hits_enemies = pygame.sprite.spritecollide(self, self.game.enemies, False)
        hits_bats = pygame.sprite.spritecollide(self, self.game.bats, False)
        hits_bosses = pygame.sprite.spritecollide(self, self.game.bosses, False)

        if self.game.player.char_type == 'swordsman':
            damage = PLAYER1_ATTR["damage"]

        for enemy in hits_enemies:
            enemy.take_damage(damage)

        for bats in hits_bats:
            bats.take_damage(damage)

        for boss in hits_bosses:
            boss.take_damage(damage)

    def update(self):
        self.animate()
        self.collide()

    def animate(self):
        direction = self.direction
        
        # Use the attack spritesheet for sword attacks
        right_animations = [
            self.game.attack_spritsheet.get_sprite(40, 122, self.width, self.height)
        ]
        down_animations = [
            self.game.attack_spritsheet.get_sprite(114, 130, self.width, self.height)
        ]
        left_animations = [
            self.game.attack_spritsheet.get_sprite(77, 123, self.width, self.height)
        ]
        up_animations = [
            self.game.attack_spritsheet.get_sprite(0, 130, self.width, self.height)
        ]
        
        if direction == 'up':
            self.image = up_animations[0]
        elif direction == 'down':
            self.image = down_animations[0]
        elif direction == 'right':
            self.image = right_animations[0]
        elif direction == 'left':
            self.image = left_animations[0]
            
        # Remove the attack after a short period
        self.animation_loop += 0.5
        if self.animation_loop >= 2:
            self.kill()
# Adicione esta classe inteira em sprites.py
class Shield(pygame.sprite.Sprite):
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self._layer = SHIELD_LAYER  # Usa a nova camada
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Carrega a imagem do escudo
        self.image = self.game.shield_spritesheet.get_sprite(1, 1, 40, 40)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

    def update(self):
        # Se o escudo do jogador não estiver mais ativo, o sprite se destrói
        if not self.player.shield_active:
            self.kill()
            return
        
        # Mantém o escudo centralizado no jogador
        self.rect.center = self.player.rect.center
class Arrow(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.arrows
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 7  # Increased speed for better feel
        self.damage = PLAYER2_ATTR["damage"]
        self.state = 'flying'  # Initial state
        
        # Verifica se são flechas especiais
        self.is_special = hasattr(self.game.player, 'special_arrows_active') and self.game.player.special_arrows_active
        
        # Carrega sprites diferentes para flechas normais e especiais
        if self.is_special:
            self.flying_sprites = {
                'up': self.game.arrowsSpecial_spritesheet.get_sprite(13, 25, 10, 16),
                'down': self.game.arrowsSpecial_spritesheet.get_sprite(22, 26, 10, 16),
                'left': self.game.arrowsSpecial_spritesheet.get_sprite(25, 0, 14, 10),
                'right': self.game.arrowsSpecial_spritesheet.get_sprite(5, 0, 14, 9)
            }
            self.fallen_sprite = self.game.arrowsSpecial_spritesheet.get_sprite(33, 26, 10, 16)
            self.damage *= 1.5  # Dano aumentado para flechas especiais
        else:
            self.flying_sprites = {
                'up': self.game.arrows_spritesheet.get_sprite(13, 25, 10, 16),
                'down': self.game.arrows_spritesheet.get_sprite(22, 26, 10, 16),
                'left': self.game.arrows_spritesheet.get_sprite(25, 0, 14, 10),
                'right': self.game.arrows_spritesheet.get_sprite(5, 0, 14, 9)
            }
            self.fallen_sprite = self.game.arrows_spritesheet.get_sprite(33, 26, 10, 16)
        
        # Set initial image based on direction
        self.image = self.flying_sprites[direction]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Timing variables
        self.lifetime = 900  # 1 second lifetime while flying
        self.fallen_lifetime = 3000  # 3 seconds lifetime after falling
        self.spawn_time = pygame.time.get_ticks()
        self.fall_time = 0

    def update(self):
        if self.state == 'flying':
            self.move()
            self.check_collisions()
            
            # Check lifetime while flying
            if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
                self.fall()
                
        elif self.state == 'fallen':
            # Check lifetime while fallen
            if pygame.time.get_ticks() - self.fall_time > self.fallen_lifetime:
                self.kill()

    def move(self):
        if self.is_special and self.state == 'flying':
            # Encontra o inimigo mais próximo
            closest_enemy = None
            min_distance = float('inf')
            
            # Verifica todos os grupos de inimigos
            for enemy_group in [self.game.enemies, self.game.bats, self.game.bosses]:
                for enemy in enemy_group:
                    dist = math.hypot(enemy.rect.centerx - self.rect.centerx, 
                                     enemy.rect.centery - self.rect.centery)
                    if dist < min_distance:
                        min_distance = dist
                        closest_enemy = enemy
            
            # Se encontrou um inimigo, move em sua direção
            if closest_enemy and min_distance < 500:  # Alcance de perseguição
                dx = closest_enemy.rect.centerx - self.rect.centerx
                dy = closest_enemy.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    dx, dy = dx / dist, dy / dist
                    self.rect.x += dx * self.speed
                    self.rect.y += dy * self.speed
                    return
        """Move the arrow based on its direction"""

        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed

    def check_collisions(self):
        """Check for collisions with blocks and enemies"""
        # Check collision with blocks
        if pygame.sprite.spritecollide(self, self.game.blocks, False):
            self.fall()
            return
            
        # Check collision with enemies
        hits_enemies = pygame.sprite.spritecollide(self, self.game.enemies, False)
        hits_bats = pygame.sprite.spritecollide(self, self.game.bats, False)
        hits_bosses = pygame.sprite.spritecollide(self, self.game.bosses, False)
        
        # Damage enemies and disappear
        for enemy in hits_enemies:
            enemy.take_damage(self.damage)
            self.kill()
            
        for bat in hits_bats:
            bat.take_damage(self.damage)
            self.kill()
            
        for boss in hits_bosses:
            boss.take_damage(self.damage)
            self.kill()

    def fall(self):
        """Change state to fallen and switch to fallen sprite"""
        if self.state != 'fallen':  # Only fall if not already fallen
            self.state = 'fallen'
            self.image = self.fallen_sprite
            self.image.set_colorkey(BLACK)
            self.fall_time = pygame.time.get_ticks()
            # Stop movement
            self.speed = 0
class Boxing(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.spritesheet = game.boxer_spritesheet

        self.x = x
        self.y = y
        self.width = TILESIZES   # Aumenta o tamanho do ataque
        self.height = TILESIZES
        
        self.animation_loop = 0
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Surface transparente
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = self.game.player.facing  # Armazena a direção do jogador

    def collide(self):
        hits_enemies = pygame.sprite.spritecollide(self, self.game.enemies, False)
        hits_bats = pygame.sprite.spritecollide(self, self.game.bats, False)
        hits_bosses = pygame.sprite.spritecollide(self, self.game.bosses, False)

        if self.game.player.char_type == 'boxer':
            damage = PLAYER3_ATTR["damage"]  # Dano alto para o boxeador

        for enemy in hits_enemies:
            enemy.take_damage(damage)

        for bats in hits_bats:
            bats.take_damage(damage)

        for boss in hits_bosses:
            boss.take_damage(damage)

    def update(self):
        self.animate()
        self.collide()

    def animate(self):
        direction = self.direction
        
        # Use self.spritesheet em vez de player3spr
        right_animations = [
            self.game.boxe_spritesheet.get_sprite(70, 14, self.width, self.height)
        ]
        down_animations = [
            self.game.boxe_spritesheet.get_sprite(12, 71, self.width, self.height)
        ]
        left_animations = [
            self.game.boxe_spritesheet.get_sprite(12, 14, self.width, self.height)
        ]
        up_animations = [
            self.game.boxe_spritesheet.get_sprite(12, 14, self.width, self.height)
        ]
        if direction == 'up':
            self.image = up_animations[0]
        elif direction == 'down':
            self.image = down_animations[0]
        elif direction == 'right':
            self.image = right_animations[0]
        elif direction == 'left':
            self.image = left_animations[0]
            
        # Mantém a posição relativa ao jogador
        
            
        # Remove o ataque após um curto período
        self.animation_loop += 0.25
        if self.animation_loop >= 1:
            self.kill()  # Ajuste este valor conforme necessário

class DialogBox:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.current_text = ""
        self.visible_text = ""
        self.text_progress = 0
        self.font = pygame.font.SysFont('arial', DIALOG_FONT_SIZE)
        self.rect = pygame.Rect(DIALOG_BOX_X, DIALOG_BOX_Y, DIALOG_BOX_WIDTH, DIALOG_BOX_HEIGHT)
        self.current_speaker = ""
        self.npc = None

    def start_dialog(self, npc):
        if self.active: return
        self.active = True
        self.npc = npc
        # Pega o primeiro diálogo para iniciar
        self.npc.current_dialog_index = 0
        dialog = self.npc.get_current_dialog()
        if dialog:
            self.current_speaker = dialog["speaker"]
            self.current_text = dialog["text"]
            self.visible_text = ""
            self.text_progress = 0

    def next_dialog(self):
        """Avança para o próximo diálogo na sequência do NPC."""
        if self.npc and self.npc.next_dialog():
            # Se o NPC tiver um próximo diálogo, atualiza a caixa
            current_dialog = self.npc.get_current_dialog()
            if current_dialog:
                self.current_speaker = current_dialog["speaker"]
                self.current_text = current_dialog["text"]
                self.visible_text = ""
                self.text_progress = 0
                return True # Indica que há mais diálogos
        # Se não houver mais diálogos, retorna False
        return False

    def update(self):
        """Atualiza a animação do texto."""
        if self.active and self.text_progress < len(self.current_text):
            self.text_progress += DIALOG_TEXT_SPEED
            self.visible_text = self.current_text[:int(self.text_progress)]

    def draw(self, surface):
        if not self.active: return
        
        # Desenha a borda e o fundo da caixa
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect)
        bg_rect = self.rect.inflate(-UI_BORDER_WIDTH * 2, -UI_BORDER_WIDTH * 2)
        pygame.draw.rect(surface, DIALOG_BOX_COLOR, bg_rect)

        # Speaker
        speaker_color = (255, 220, 100) if self.current_speaker == "Player" else (120, 220, 255)
        speaker_surface = self.font.render(f"{self.current_speaker}:", True, speaker_color)
        surface.blit(speaker_surface, (self.rect.x + DIALOG_TEXT_MARGIN, self.rect.y + DIALOG_TEXT_MARGIN))
        
        # Texto do Diálogo com quebra de linha
        text_x = self.rect.x + DIALOG_TEXT_MARGIN
        text_y = self.rect.y + DIALOG_TEXT_MARGIN + speaker_surface.get_height() + 5
        max_width = self.rect.width - (DIALOG_TEXT_MARGIN * 2)
        words = self.visible_text.split(' ')
        space = self.font.size(' ')[0]
        line_spacing = self.font.get_linesize()
        current_x, current_y = text_x, text_y

        for word in words:
            word_surface = self.font.render(word, True, DIALOG_TEXT_COLOR)
            word_width, _ = word_surface.get_size()
            if current_x + word_width >= text_x + max_width:
                current_x = text_x
                current_y += line_spacing
            surface.blit(word_surface, (current_x, current_y))
            current_x += word_width + space

        # Indicador para continuar
        if self.text_progress >= len(self.current_text) and pygame.time.get_ticks() % 1000 > 500:
            indicator_points = [
                (self.rect.right - 35, self.rect.bottom - 25),
                (self.rect.right - 25, self.rect.bottom - 25),
                (self.rect.right - 30, self.rect.bottom - 15)
            ]
            pygame.draw.polygon(surface, UI_FONT_COLOR, indicator_points)

    def close(self):
        """Fecha a caixa de diálogo."""
        self.active = False
        self.current_text = ""
        self.visible_text = ""
        self.text_progress = 0
        self.current_speaker = ""
        if self.npc:
            self.npc.current_dialog_index = 0 # Reseta o diálogo do NPC
            self.npc = None
class SlimeNPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = NPC_LAYER
        self.groups = self.game.all_sprites, self.game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES
        
        # Carrega as animações do slime
        self.animation_frames = {
            'idle': [
                self.game.slimenpc.get_sprite(1, 1, self.width, self.height)
            ]
        }
        
        # Configuração de animação
        self.current_frame = 0
        self.animation_speed = 10
        self.animation_counter = 0
        self.image = self.animation_frames['idle'][self.current_frame]
        self.image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Diálogo sequencial
        self.dialog_sequence = [
            {'speaker': 'Slime', 'text': 'Blub! Blub! (olá...humano.)'},
            {"speaker": "Slime", "text": "Blub, Blub, Blub! (Derrotar...Goblins...Portal...Ativar)."},
            {"speaker": "Player", "text": "Não entendo o que esse pedaço de gosma fala..."},
            {"speaker": "Player", "text": "Mas suponho que tenha a ver com aquelas coisas feias"}
        ]
        self.current_dialog_index = 0
        self.in_range = False
        self.can_interact = True  # Adicione esta linha para definir o atributo
        self.last_interact_time = 0
        self.interact_cooldown = 1000  # 1 segundo de cooldown
        
    def next_dialog(self):
        """Avança para o próximo diálogo na sequência"""
        self.current_dialog_index += 1
        if self.current_dialog_index < len(self.dialog_sequence):
            return True
        return False
    
    def get_current_dialog(self):
        """Retorna o diálogo atual"""
        if self.current_dialog_index < len(self.dialog_sequence):
            return self.dialog_sequence[self.current_dialog_index]
        return None
        
    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames['idle'])
            self.image = self.animation_frames['idle'][self.current_frame]
            self.image.set_colorkey(BLACK)
            
    def update(self):
        self.animate()
        
        current_time = pygame.time.get_ticks()
        
        # Verifica colisão com o jogador
        if hasattr(self.game, 'player'):
            colliding = pygame.sprite.collide_rect(self, self.game.player)
            
            if colliding and not self.in_range and self.can_interact:
                self.in_range = True
                if not self.game.dialog_box.active:
                    self.current_dialog_index = 0
                    current_dialog = self.get_current_dialog()
                    if current_dialog:
                        self.game.dialog_box.start_dialog(self)
                        self.last_interact_time = current_time
                        self.can_interact = False
            
            if not colliding and self.in_range:
                self.in_range = False
                if self.game.dialog_box.active and self.game.dialog_box.npc == self:
                    self.game.dialog_box.close()
        
        # Verifica cooldown de interação
        if not self.can_interact and current_time - self.last_interact_time > self.interact_cooldown:
            self.can_interact = True

class Seller1NPC(pygame.sprite.Sprite): #vendedor dialogo
    def __init__(self, game, x, y):
        self.game = game
        self._layer = NPC_LAYER
        self.groups = self.game.all_sprites, self.game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x * TILESIZES
        self.y = y * TILESIZES
        self.width = TILESIZES
        self.height = TILESIZES
        
        # Carrega as animações do slime
        self.animation_frames = {
            'idle': [
                self.game.seller_spritesheet.get_sprite(1, 0, self.width, self.height),
                self.game.seller_spritesheet.get_sprite(1, 32, self.width, self.height)
            ]
        }
        
        # Configuração de animação
        self.current_frame = 0
        self.animation_speed = 30
        self.animation_counter = 0
        self.image = self.animation_frames['idle'][self.current_frame]
        self.image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Diálogo sequencial
        self.dialog_sequence = [
            {'speaker': '???', 'text': 'Olá, Forasteiro.'},
            {"speaker": "Player", "text": "Quem é você?"},
            {"speaker": "Mercador", "text": "Apenas um vendedor ambulante pelas regiôes."},
            {"speaker": "Player", "text": "uhm... boto fé..."},
            {"speaker": "Mercador", "text": "Está precisando de algumas melhorias em seu equipamento? Forasteiro."},
            {"speaker": "Player", "text": "Não... por enquanto..."},
            {"speaker": "Mercador", "text": "He he he he, te vejo por aí, Forasteiro"}
        ]
        self.current_dialog_index = 0
        self.in_range = False
        self.can_interact = True  # Adicione esta linha para definir o atributo
        self.last_interact_time = 1
        self.interact_cooldown = 0.5  # 0.5 segundo de cooldown
        
    def next_dialog(self):
        #"""Avança para o próximo diálogo na sequência"""
        self.current_dialog_index += 1
        if self.current_dialog_index < len(self.dialog_sequence):
            return True
        return False
    
    def get_current_dialog(self):
        #"""Retorna o diálogo atual"""
        if self.current_dialog_index < len(self.dialog_sequence):
            return self.dialog_sequence[self.current_dialog_index]
        return None
        
    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames['idle'])
            self.image = self.animation_frames['idle'][self.current_frame]
            self.image.set_colorkey(BLACK)
            
    def update(self):
        self.animate()
        
        current_time = pygame.time.get_ticks()
        
        # Verifica colisão com o jogador
        if hasattr(self.game, 'player'):
            colliding = pygame.sprite.collide_rect(self, self.game.player)
            
            if colliding and not self.in_range and self.can_interact:
                self.in_range = True
                if not self.game.dialog_box.active:
                    self.current_dialog_index = 0
                    current_dialog = self.get_current_dialog()
                    if current_dialog:
                        self.game.dialog_box.start_dialog(self)
                        self.last_interact_time = current_time
                        self.can_interact = False
            
            if not colliding and self.in_range:
                self.in_range = False
                if self.game.dialog_box.active and self.game.dialog_box.npc == self:
                    self.game.dialog_box.close()
        
        # Verifica cooldown de interação
        if not self.can_interact and current_time - self.last_interact_time > self.interact_cooldown:
            self.can_interact = True

class Seller2NPC(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = NPC_LAYER
        self.groups = self.game.all_sprites, self.game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x, self.y, self.width, self.height = x * TILESIZES, y * TILESIZES, TILESIZES, TILESIZES
        self.load_animations()
        self.current_frame, self.animation_speed, self.animation_counter = 0, 30, 0
        self.image = self.animation_frames['idle'][self.current_frame]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        self.shop_active = False
        self.selected_option = 0
        self.last_interact_time = 0
        self.interact_cooldown = 500 # ms
        
        self.upgrade_options = [
            {"name": "Restaurar Vida", "cost": 5, "description": "Recupera toda a sua vida.", "effect": self.upgrade_health},
            {"name": "Aumentar Dano", "cost": 2, "description": "+2 de dano por ataque.", "effect": self.upgrade_damage},
            {"name": "Aumentar Velocidade", "cost": 2, "description": "Aumenta permanentemente a velocidade.", "effect": self.upgrade_speed},
            {"name": "Melhorar Recarga", "cost": 3, "description": "-30% no tempo de recarga de habilidades.", "effect": self.upgrade_cooldown}
        ]

    def load_animations(self):
        self.animation_frames = {'idle': [
                self.game.seller_spritesheet.get_sprite(1, 0, self.width, self.height),
                self.game.seller_spritesheet.get_sprite(1, 32, self.width, self.height)
            ]}

    def upgrade_health(self, player):
        if player.coins >= 5:
            player.coins -= 5
            player.life = self.game.player.max_life
            return True
        return False
    
    def upgrade_damage(self, player):
        if player.coins >= 2:
            player.coins -= 2
            player.damage += 2
            return True
        return False
    
    def upgrade_speed(self, player):
        if player.coins >= 2:
            player.coins -= 2
            player.speed_boost += 1
            return True
        return False
    
    def upgrade_cooldown(self, player):
        if player.coins >= 3:
            player.coins -= 3
            player.attack_cooldown_multiplier *= 0.7
            player.dodge_cooldown_multiplier *= 0.7
            return True
        return False

    def draw_shop(self, surface):
        if not self.shop_active: return
            
        shop_rect = pygame.Rect(SHOP_X, SHOP_Y, SHOP_WIDTH, SHOP_HEIGHT)
        pygame.draw.rect(surface, UI_BORDER_COLOR, shop_rect)
        bg_rect = shop_rect.inflate(-UI_BORDER_WIDTH * 2, -UI_BORDER_WIDTH * 2)
        pygame.draw.rect(surface, SHOP_BG_COLOR, bg_rect)
        
        title_font = pygame.font.SysFont('arial', SHOP_TITLE_FONT_SIZE, bold=True)
        title = title_font.render("Loja de Melhorias", True, SHOP_TITLE_COLOR)
        
        surface.blit(title, title.get_rect(centerx=shop_rect.centerx, y=shop_rect.y + 20))
        
        
        coin_font = pygame.font.SysFont('arial', SHOP_FONT_SIZE)
        coin_text = coin_font.render(f"Moedas: {self.game.player.coins}", True, UI_TITLE_COLOR)
        surface.blit(coin_text, coin_text.get_rect(right=shop_rect.right - 20, y=shop_rect.y + 65))
        
        option_font = pygame.font.SysFont('arial', SHOP_FONT_SIZE)
        desc_font = pygame.font.SysFont('arial', 18)
        y_offset = 120
        for i, option in enumerate(self.upgrade_options):
            if i == self.selected_option:
                arrow_points = [(shop_rect.x + 25, shop_rect.y + y_offset + 10), (shop_rect.x + 40, shop_rect.y + y_offset + 17), (shop_rect.x + 25, shop_rect.y + y_offset + 24)]
                pygame.draw.polygon(surface, SHOP_SELECTED_COLOR, arrow_points)

            color = SHOP_SELECTED_COLOR if i == self.selected_option else SHOP_OPTION_COLOR
            text = option_font.render(f"{option['name']} - ({option['cost']} moedas)", True, color)
            surface.blit(text, (shop_rect.x + 55, shop_rect.y + y_offset))
            
            desc = desc_font.render(option['description'], True, (200, 200, 200))
            surface.blit(desc, (shop_rect.x + 60, shop_rect.y + y_offset + 30))
            
            y_offset += 70

    def handle_shop_input(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_interact_time < self.interact_cooldown: return
            
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.upgrade_options)
            self.last_interact_time = current_time
        elif keys[pygame.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.upgrade_options)
            self.last_interact_time = current_time
        
        if keys[pygame.K_f] or (self.game.joystick and self.game.joystick.get_button(0)):
            selected = self.upgrade_options[self.selected_option]
            selected["effect"](self.game.player)
            self.last_interact_time = current_time
        
        if keys[pygame.K_ESCAPE] or (self.game.joystick and self.game.joystick.get_button(1)):
            self.shop_active = False
            self.last_interact_time = current_time

    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames['idle'])
            self.image = self.animation_frames['idle'][self.current_frame]
            self.image.set_colorkey(BLACK)

    def update(self):
        self.animate()
        current_time = pygame.time.get_ticks()
        if hasattr(self.game, 'player'):
            colliding = pygame.sprite.collide_rect(self, self.game.player)
            
            if colliding and not self.shop_active and current_time - self.last_interact_time > 700:
                self.shop_active = True
                self.selected_option = 0
                self.last_interact_time = current_time
            
            if not colliding and self.shop_active:
                self.shop_active = False
            
            if self.shop_active:
                self.handle_shop_input()
        # Pode adicionar um efeito sonoro aqui
class Coin(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ITEM_LAYER  # Adicione ITEM_LAYER no config.py com valor apropriado
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.x = x
        self.y = y
        self.width = TILESIZES // 2
        self.height = TILESIZES // 2
        
        # Animação da moeda
        self.animation_frames = [
            self.game.coin.get_sprite(9, 5, 16, 16),
            self.game.coin.get_sprite(74, 5, 16, 16),
            self.game.coin.get_sprite(43, 36, 16, 16),
            self.game.coin.get_sprite(43, 70, 16, 16)
        ]
        
        self.current_frame = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
        
        self.image = self.animation_frames[self.current_frame]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        
        # Tempo de vida da moeda
        self.lifetime = 20000  # 10 segundos
        self.spawn_time = pygame.time.get_ticks()
    
    def update(self):
        # Atualiza animação
        self.animate()
        
        # Verifica colisão com o jogador
        if hasattr(self.game, 'player'):
            if pygame.sprite.collide_rect(self, self.game.player):
                self.game.player.coins += 1  # Incrementa contador de moedas
                self.kill()
        
        # Verifica tempo de vida
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
    
    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed * 60:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]
            self.image.set_colorkey(BLACK)