WIN_WIDTH = 1080
WIN_HEIGHT = 660
TILESIZES = 32
#ENEMY_COUNT = 0
OBSTACLE_COUNT = 25

SHIELD_LAYER = 7
PLAYER_LAYER = 6
OBSTACLE_LAYER = 5
PORTAL_LAYER = 5
ENEMY_LAYER = 4
NPC_LAYER = 4
BLOCK_LAYER = 3
GROUND_LAYER = 2
ITEM_LAYER = 4
BOSS_LAYER = 4 # Nova camada para o boss


#PLAYER_LIFE = 20
ENEMY_LIFE = 36
BAT_LIFE = 20
NERO_LIFE = 120 
 # Velocidade do Nero


#self.base_speed = 4
ENEMY_SPEED = 1
BAT_SPEED = 6
NERO_SPEED = 6
#DAMAGE
#PLAYER_DAMAGE = 4


NERO_WHIP_DAMAGE = 25 # Dano do chicote
NERO_FIRE_DAMAGE = 8 # Dano da área de fogo
NERO_KNIFE_DAMAGE = 15 # Dano do ataque giratório

NERO_WHIP_RANGE = 250 # Distância para o ataque de chicote
NERO_KNIFE_RANGE = 70 # Distância para o ataque de faca

FIRE_AREA_LIFETIME = 1500 # Tempo de duração da área de fogo em ms
FIRE_DAMAGE_INTERVAL = 900 # Intervalo de dano da área de fogo em ms

# Adicione no config.py
# Configurações da tela de seleção
CHAR_SELECT_TITLE = "Escolha seu Jogador"
CHAR_SELECT_FONT_SIZE = 36
CHAR_DESC_FONT_SIZE = 22
CHAR_ARROW_SIZE = 50
# Personagens

# Atributos dos personagens

PLAYER1_ATTR = {
    "name": "Jack",
    "life": 18,
    "damage": 4,
    "speed": 5,
    "sprite": "sprt/PLAYERS/player1tst.png",
    # MANTENHA OU ALTERE PARA A SPRITESHEET CORRETA DO ESPADACHIM
    "animation_sheet": "sprt/img/character.png",
    "description": "Ataques rápidos e precisos usando uma lâmina",
    "type": "swordsman"
}

PLAYER2_ATTR = {
    "name": "Emma",
    "life": 18,
    "damage": 7,
    "speed": 5,
    "sprite": "sprt/PLAYERS/player2tst.png",
    # ALTERADO para a spritesheet do arqueiro
    "animation_sheet": "sprt/img/character.png", 
    "description": "Dispara flechas com uma mira precisa",
    "type": "archer"
}

PLAYER3_ATTR = {
    "name": "Harald",
    "life": 25,
    "damage": 9,
    "speed": 3,
    "sprite": "sprt/PLAYERS/player3tst.png",
    # ALTERADO para a spritesheet do boxeador
    "animation_sheet": "sprt/PLAYERS/character (3).png",
    "description": "Grande resistência e força",
    "type": "boxer"
}


CHARACTERS = {
    1: PLAYER1_ATTR,
    2: PLAYER2_ATTR,
    3: PLAYER3_ATTR
}
player3spr = "sprt/PLAYERS/player3tst.png"
# Cooldowns das habilidades
ATTACK_COOLDOWN = 1000  # 1 segundos em milissegundos
DODGE_COOLDOWN = 3000   # 3 segundos em milissegundos
ARROW_COOLDOWN = 3500
BOXING_COOLDOWN = 400
SHIELD_DURATION = 5000  # 5 segundos em milissegundos
SHIELD_COOLDOWN = 30000     
SPECIAL_ARROW_DURATION = 20000  # 20 segundos em milissegundos
SPECIAL_ARROW_COOLDOWN = 40000  # 40 segundos em milissegundos

GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0,0, 0)
WHITE_SNOW = (220, 255, 248)
FPS = 45
# --- Estética Estilo Pokémon ---
UI_BORDER_WIDTH = 3
UI_BORDER_COLOR = (248, 248, 248)      # Branco
UI_BG_COLOR = (48, 80, 144, 230)       # Azul escuro, semi-transparente
UI_FONT_COLOR = (248, 248, 248)      # Branco
UI_TITLE_COLOR = (255, 215, 0)         # Dourado
SELECTED_COLOR = (248, 248, 88)        # Amarelo brilhante
DISABLED_COLOR = (120, 120, 120)       # Cinza para cooldown

# --- Barras de Vida ---
HEALTH_BAR_WIDTH = 40
HEALTH_BAR_HEIGHT = 8                  # Mais espessa para melhor visualização
HEALTH_BAR_OFFSET = 12
HEALTH_BAR_BG_COLOR = (88, 88, 88)     # Fundo cinza escuro
HEALTH_COLOR_HIGH = (48, 216, 48)      # Verde para vida alta
HEALTH_COLOR_MEDIUM = (248, 248, 88)   # Amarelo para vida média
HEALTH_COLOR_LOW = (248, 56, 32)       # Vermelho para vida baixa
HEALTH_BAR_BORDER_COLOR = (16, 16, 16) # Borda preta

# --- Barras de Habilidade ---
BAR_WIDTH = 120
BAR_HEIGHT = 15
BAR_BG_COLOR = (50, 50, 50)
# Cores do Ataque
ATTACK_READY_COLOR = (248, 128, 72)     # Laranja/Vermelho
ATTACK_COOLDOWN_COLOR = DISABLED_COLOR
# Cores da Esquiva
DODGE_READY_COLOR = (88, 168, 248)      # Azul brilhante
DODGE_COOLDOWN_COLOR = DISABLED_COLOR


# --- Painel de Habilidades ---
ABILITY_PANEL_WIDTH = 280
ABILITY_PANEL_HEIGHT = 200
ABILITY_PANEL_X = WIN_WIDTH - ABILITY_PANEL_WIDTH - 10
ABILITY_PANEL_Y = 10
ABILITY_PANEL_COLOR = UI_BG_COLOR
ABILITY_TEXT_COLOR = UI_FONT_COLOR
ABILITY_TITLE_FONT_SIZE = 22
ABILITY_FONT_SIZE = 18

# --- Loja do Vendedor ---
SHOP_WIDTH = 480
SHOP_HEIGHT = 400
SHOP_X = WIN_WIDTH // 2 - SHOP_WIDTH // 2
SHOP_Y = WIN_HEIGHT // 2 - SHOP_HEIGHT // 2
SHOP_BG_COLOR = UI_BG_COLOR
SHOP_TEXT_COLOR = UI_FONT_COLOR
SHOP_TITLE_COLOR = UI_TITLE_COLOR
SHOP_OPTION_COLOR = UI_FONT_COLOR
SHOP_SELECTED_COLOR = SELECTED_COLOR
SHOP_FONT_SIZE = 22
SHOP_TITLE_FONT_SIZE = 28

# --- Caixa de Diálogo ---
DIALOG_BOX_WIDTH = WIN_WIDTH - 40
DIALOG_BOX_HEIGHT = 150
DIALOG_BOX_X = 20
DIALOG_BOX_Y = WIN_HEIGHT - DIALOG_BOX_HEIGHT - 20
DIALOG_BOX_COLOR = UI_BG_COLOR
DIALOG_TEXT_COLOR = UI_FONT_COLOR
DIALOG_FONT_SIZE = 26
DIALOG_SMALL_FONT_SIZE = 20
DIALOG_TEXT_MARGIN = 15
DIALOG_TEXT_SPEED = 2

#audios


# audios song
MUSIC_LEVELS = {
    1: 'audios/som_da_floresta (mp3).mp3',
    2: 'audios/ambiente1swamp.mp3',
    3: 'audios/Cave1song.mp3',
    3: 'audios/WaterDrops-Cave.mp3',
    4: 'audios/vento-Snow.mp3',
    'store': 'audios/store-backsong.mp3'
}
#fases
tilemap = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B...V..O........................M................B',
    'B.P.....O........................................B',
    'B....S...O.......................................B',
    'BOQQOOOOO........................................B',
    'B..Q....C........................................B',
    'B................................................B',
    'BQ.........................Q.....................B',
    'B.QQ...............Q.............................B',
    'BQ..............C................................B',
    'B................................................B',
    'B................................................B',
    'B....Q...........................................B',
    'B................................................B',
    'B...........................Q....................B',
    'B.......E..............Q.Q.......................B',
    'B...................Q............................B',
    'B................................................B',
    'B............................Q...................B',
    'B................................................B',
    'B...........................QQQ..................B',
    'B......................................Q.........B',
    'B................................................B',
    'B................................................B',
    'BQ............................Q..................B',
    'BTQ..............................................B',
    'B.Q...........................C....Q...C.........B',
    'B..................................Q.............B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]

# Fase 2 - Tilemap com spawn na parte inferior
tilemap2 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'BT.....WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW..WWWWWQ...B',
    'B......WWWW..WWWWWWWWWWWWWWWWWWWWWWWW....C..QQ...B',
    'B.C....WQWWWWWWWWW.............WWWWWWW...C..WWQ..B',
    'B....WWWQWWWWW..................WWQQWW......WW...B',
    'B......WQQWW.............C.......QQQ....W..WW....B',
    'B......WWWWWW....................QWW.........W...B',
    'B.....QWQQWWW..........C.........WWWWWW.....WWWQ.B',
    'B.....WWWWWWWWWWWWWW...........WWWWWWW...WWWWW...B',
    'B......WWWWWQQWWWWW..........WWWWWWWWWWWWQQWW....B',
    'B......WWWWWW....WW......C.......WWWWWWW.WWWWW...B',
    'B......WWWWWWWWWWWWW...........WWWWWWWQWWWWWW....B',
    'B......WQWWWWWQWWWWWWWWWWWW..QWWWWWWWWWWWWW..W...B',
    'B.....WWWWWWWWWWWWWWWQQWWWWQQ.WWWWWWW......WWWW..B',
    'B......WWWQQWWWW..WWWWWWWW..Q..........WWQWWWW...B',
    'B.......WWWWWWWWWWWWWWWWWWWWWWW..........WWWWW...B',
    'B......WWWWWWW.......WWWWWW.WWWWWWW......WW.WWQ..B',
    'B......QQ...........WQQWW...W.QQQ...C....WW.WQ...B',
    'B........QQW..........QQ.....Q..........WWWQWWQ..B',
    'B......QWWWWWWWWWWWWWWWQQWWWWQ.....WWWWWWWWWWWW.PB',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]

tilemap3 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B......O.......................QQQ...............B',
    'B.PQ....O........................................B',
    'B.QQQ.......................Q....................B',
    'B..QQ.Q..............................QQ..Q.......B',
    'B..Q....C........................................B',
    'B...........................Q....................B',
    'BQ.......G.................Q.....................B',
    'B.QQ...............Q.............................B',
    'BQ...............................................B',
    'B................................................B',
    'B................................................B',
    'B....Q.........G..................G..............B',
    'B........Q.......................................B',
    'B...........................Q....................B',
    'B......................Q.Q.......................B',
    'B........Q..........Q..................Q.........B',
    'B................................................B',
    'B............QQQ..............Q........QQQ.......B',
    'B......................................Q.........B',
    'B..........QQQQ.............QQQ........Q.........B',
    'B......................................Q.........B',
    'B................................................B',
    'B..........................................QQ....B',
    'B........Q....................Q..................B',
    'B........QQ...................................QQQB',
    'B.Q......Q...................................QQQTB',
    'B.............................................Q..B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]
tilemap4 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B......O........................M................B',
    'B.P.....O........................................B',
    'B....S...O.......................................B',
    'BOQQOOOOO........................................B',
    'B..Q....C........................................B',
    'B................................................B',
    'BQ.........................Q.....................B',
    'B.QQ...............Q.............................B',
    'BQ..............C................................B',
    'B................................................B',
    'B................................................B',
    'B....Q...........................................B',
    'B..................................C.............B',
    'B...........................Q....................B',
    'B......................Q.Q.......................B',
    'B...................Q............................B',
    'B................................................B',
    'B............................Q.........C.........B',
    'B................................................B',
    'B...........................QQQ..................B',
    'B......................................Q.........B',
    'B................................................B',
    'B................................................B',
    'BQ............................Q..................B',
    'BTQ..............................................B',
    'B.Q...........................C....Q...C.........B',
    'B..................................Q.............B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
]
store = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B..OVO...................B',
    'B.......................TB',
    'B.........P..............B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBB'
]
boss_arena = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.QQQP.Q......O.........................B',
    'B...QQ.QQ.........................N.....B',
    'B..........C...C........................B',
    'B.......................................B',
    'B.....C.........QQQ.....Q...............B',
    'B..........C............................B',
    'B...QQ.........C........................B',
    'B.............................QQ........B',
    'B.......................................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
]