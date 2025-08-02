# ui_elements.py
import pygame
from config import *

class InputBox:
    """
    Uma caixa de texto simples para entrada de dados pelo usuário.
    """
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = UI_BORDER_COLOR
        self.text = text
        self.font = font
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Ativa a caixa de texto se for clicada
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = SELECTED_COLOR if self.active else UI_BORDER_COLOR
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # Pode ser usado para confirmar a entrada
                    self.active = False
                    self.color = UI_BORDER_COLOR
                    return "enter"
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-renderiza o texto
                self.txt_surface = self.font.render(self.text, True, self.color)
        return None

    def draw(self, screen):
        # Desenha a caixa e o texto
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)