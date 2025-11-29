import pygame

COLORS = {
    'background': (30, 33, 40),      # Темный фон приложения
    'sidebar': (40, 44, 52),         # Чуть светлее для меню
    'sheet_bg': (50, 54, 62),        # Фон листа
    'sheet_border': (70, 130, 180),  # SteelBlue обводка
    'grid': (60, 64, 72),            # Тонкие линии сетки
    'text_main': (220, 220, 220),    # Белый текст
    'text_dim': (150, 150, 160),     # Серый текст
    'shadow': (20, 20, 20),          # Тени
    'success': (46, 204, 113),       # Зеленый для хорошей позиции
    'danger': (231, 76, 60),         # Красный для ошибки
    'accent': (52, 152, 219)         # Синий акцент
}

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        # Используем системный шрифт, но посимпатичнее, или дефолтный
        self.title_font = pygame.font.SysFont("Verdana", 24, bold=True)
        self.font = pygame.font.SysFont("Verdana", 14)
        self.small_font = pygame.font.SysFont("Consolas", 12)

    def draw_background(self):
        self.screen.fill(COLORS['background'])

    def draw_grid(self, x, y, width, height, cell_size=50):
        """Рисуем инженерную сетку"""
        # Вертикальные линии
        for ix in range(0, width + 1, cell_size):
            pygame.draw.line(self.screen, COLORS['grid'], (x + ix, y), (x + ix, y + height), 1)
        # Горизонтальные линии
        for iy in range(0, height + 1, cell_size):
            pygame.draw.line(self.screen, COLORS['grid'], (x, y + iy), (x + width, y + iy), 1)

    def draw_sheet(self, sheet_x, sheet_y, width, height):
        # Тень под листом
        pygame.draw.rect(self.screen, COLORS['shadow'], 
                        (sheet_x + 10, sheet_y + 10, width, height), border_radius=4)
        
        # Сам лист
        pygame.draw.rect(self.screen, COLORS['sheet_bg'], (sheet_x, sheet_y, width, height), border_radius=4)
        
        # Сетка
        self.draw_grid(sheet_x, sheet_y, width, height)
        
        # Обводка листа
        pygame.draw.rect(self.screen, COLORS['sheet_border'], (sheet_x, sheet_y, width, height), 2, border_radius=4)

        # Размеры листа (подписи)
        w_text = self.small_font.render(f"{width}mm", True, COLORS['text_dim'])
        h_text = self.small_font.render(f"{height}mm", True, COLORS['text_dim'])
        self.screen.blit(w_text, (sheet_x + width // 2 - 20, sheet_y - 20))
        self.screen.blit(h_text, (sheet_x - 45, sheet_y + height // 2))

    def draw_shape(self, shape, is_selected=False, is_valid=True, offset_x=0, offset_y=0):
        # Реальные координаты отрисовки (с учетом смещения листа, если нужно)
        x = shape.x + offset_x
        y = shape.y + offset_y
        
        rect = (x, y, shape.width, shape.height)
        
        # 1. Тень (Deep Shadow) при перетаскивании
        if is_selected:
            shadow_rect = (x + 8, y + 8, shape.width, shape.height)
            s = pygame.Surface((shape.width, shape.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, 80), (0,0, shape.width, shape.height), border_radius=6)
            self.screen.blit(s, (x + 8, y + 8))
        else:
            # Легкая тень для лежащих деталей
            shadow_rect = (x + 2, y + 2, shape.width, shape.height)
            pygame.draw.rect(self.screen, (20, 20, 25), shadow_rect, border_radius=4)

        # 2. Основное тело детали
        color = shape.color
        if not is_valid:
            color = (200, 50, 50) # Красный оттенок при ошибке
            
        pygame.draw.rect(self.screen, color, rect, border_radius=4)

        # 3. Обводка (Highlight)
        border_color = (255, 255, 255) if is_selected else (0, 0, 0)
        thickness = 2 if is_selected else 1
        
        if not is_valid:
            border_color = COLORS['danger']
            thickness = 3
            
        pygame.draw.rect(self.screen, border_color, rect, thickness, border_radius=4)

        # 4. Текст размеров (автоматически прячем если деталь слишком мелкая)
        if shape.width > 30 and shape.height > 20:
            text = self.small_font.render(f"{int(shape.width)}x{int(shape.height)}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + shape.width // 2, y + shape.height // 2))
            self.screen.blit(text, text_rect)

    def draw_sidebar(self, x, width, height, stats):
        # Фон сайдбара
        pygame.draw.rect(self.screen, COLORS['sidebar'], (x, 0, width, height))
        pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, height), 2)

        # Заголовок
        title = self.title_font.render("OPTIMIZER", True, COLORS['accent'])
        self.screen.blit(title, (x + 20, 30))
        
        subtitle = self.font.render("Interactive Packing", True, COLORS['text_dim'])
        self.screen.blit(subtitle, (x + 20, 60))

        # Карточка статистики
        self._draw_stat_card(x + 20, 120, width - 40, "EFFICIENCY", f"{stats['efficiency']:.1f}%", 
                             COLORS['success'] if stats['efficiency'] > 70 else COLORS['text_main'])
        
        self._draw_stat_card(x + 20, 200, width - 40, "PARTS PLACED", f"{stats['placed']}/{stats['total']}")

        # Инструкции
        y_help = height - 150
        help_lines = [
            "LMB: Move Part",
            "Ниже, то что не реализовано:",
            "RMB: Rotate",  # TODO: "Не реализовано"
            "R: Reset All", # TODO: "Не реализовано"
            "G: Generate New" # TODO: "Не реализовано"
        ]
        
        pygame.draw.line(self.screen, COLORS['grid'], (x + 20, y_help - 20), (x + width - 20, y_help - 20), 1)
        for i, line in enumerate(help_lines):
            t = self.small_font.render(line, True, COLORS['text_dim'])
            self.screen.blit(t, (x + 20, y_help + i * 25))

    def _draw_stat_card(self, x, y, w, title, value, value_color=COLORS['text_main']):
        # Фон карточки
        pygame.draw.rect(self.screen, (50, 54, 62), (x, y, w, 60), border_radius=8)
        
        # Заголовок
        lbl = self.small_font.render(title, True, COLORS['text_dim'])
        self.screen.blit(lbl, (x + 10, y + 8))
        
        # Значение
        val = self.title_font.render(value, True, value_color)
        self.screen.blit(val, (x + 10, y + 25))

    def draw_button(self, x, y, width, height, text, hover=False):
        color = COLORS['accent'] if not hover else (70, 170, 240) # Светлее при наведении
        
        # Тень кнопки
        pygame.draw.rect(self.screen, (20, 20, 20), (x+2, y+2, width, height), border_radius=6)
        # Сама кнопка
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=6)
        
        # Текст
        lbl = self.font.render(text, True, (255, 255, 255))
        lbl_rect = lbl.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(lbl, lbl_rect)
        
        return pygame.Rect(x, y, width, height) # Возвращаем Rect для проверки клика