import pygame
from ui.renderer import Renderer
from models.shape import Rectangle
from algorithms.first_fit import FirstFitDecreasing  

class CuttingGame:
    def __init__(self, parts):
        pygame.init()
        self.width, self.height = 1400, 900
        self.sidebar_width = 300
        self.sheet_offset_x = 50
        self.sheet_offset_y = 50

        # Размеры листа металла
        self.sheet_w = 800
        self.sheet_h = 600

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Cutting Optimizer")

        self.renderer = Renderer(self.screen)
        self.clock = pygame.time.Clock()

        # Данные деталей
        self.parts = parts          # Детали в "буфере" (справа)
        self.placed_parts = []      # Детали на листе
        self.selected_part = None
        self.drag_offset = (0, 0)

        # --- Phase 2: AI Packer ---
        self.packer = FirstFitDecreasing(step=10) # step=10 для скорости, 1 для точности
        self.button_rect = None     # Сюда сохраним координаты кнопки для кликов

        # Раскидываем детали в меню при старте
        self._reset_parts_position()

    def _reset_parts_position(self):
        """Возвращает все детали из списка self.parts в зону сайдбара"""
        x_start = self.width - self.sidebar_width + 20
        y_start = 300 
        
        current_x = x_start
        current_y = y_start
        
        for part in self.parts:
            part.x = current_x
            part.y = current_y
            # Сброс вращения на дефолтное (опционально, можно убрать)
            if part.width < part.height: 
                part.width, part.height = part.height, part.width
                
            current_y += 40
            if current_y > self.height - 150: # -150 чтобы не наехать на кнопку
                current_y = y_start
                current_x += 60 

    def run_auto_pack(self):
        """Логика автоматической упаковки с отступами"""
        print("AI Start Packing...")
        
        # Настройка отступа (в пикселях/мм)
        margin = 4 
        
        all_parts = self.parts + self.placed_parts
        
        # 1. Запускаем алгоритм на УМЕНЬШЕННОМ листе
        # Мы "обманываем" алгоритм, говоря, что места меньше, чем на самом деле.
        # Так он не поставит детали вплотную к краям.
        effective_width = self.sheet_w - (margin * 2)
        effective_height = self.sheet_h - (margin * 2)
        
        packed_results = self.packer.pack(all_parts, effective_width, effective_height)
        
        # 2. Применяем координаты со смещением
        for part in packed_results:
            # Сдвиг = (начало листа) + (отступ внутрь)
            part.x += self.sheet_offset_x + margin
            part.y += self.sheet_offset_y + margin
        
        # 3. Обновляем списки
        self.placed_parts = packed_results
        self.parts = [p for p in all_parts if p not in packed_results]
        
        # 4. Возвращаем остальные в меню
        self._reset_parts_position()
        print(f"Finish! Placed: {len(self.placed_parts)}, Left: {len(self.parts)}")

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # --- Event Handling ---  #
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left Click
                        # Проверка клика по кнопке AUTO PACK
                        if self.button_rect and self.button_rect.collidepoint(event.pos):
                            self.run_auto_pack()
                        else:
                            self.handle_mouse_down(event)
                            
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_move(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.selected_part:
                        self.selected_part.rotate()

            # --- Rendering ---  #
            self.renderer.draw_background()
            
            # Рисуем лист
            self.renderer.draw_sheet(self.sheet_offset_x, self.sheet_offset_y, self.sheet_w, self.sheet_h)
            
            # Статистика
            stats = {
                'efficiency': self.calculate_efficiency(),
                'placed': len(self.placed_parts),
                'total': len(self.parts) + len(self.placed_parts)
            }

            # 2.1 Сайдбар (меню)
            self.renderer.draw_sidebar(self.width - self.sidebar_width, self.sidebar_width, self.height, stats)

            # 2.2 Кнопка AUTO PACK (рисуем поверх сайдбара)
            btn_x = self.width - self.sidebar_width + 20
            btn_y = self.height - 80
            # Проверяем наведение мыши для эффекта подсветки
            is_hover = self.button_rect.collidepoint(mouse_pos) if self.button_rect else False
            
            self.button_rect = self.renderer.draw_button(
                btn_x, btn_y, 
                self.sidebar_width - 40, 50, 
                "AUTO PACK (AI)", 
                is_hover
            )

            # 2.3 Детали (рисуем поверх всего)
            all_parts = self.parts + self.placed_parts
            
            # Выбранную деталь рисуем последней (чтобы была сверху)
            if self.selected_part and self.selected_part in all_parts:
                all_parts.remove(self.selected_part)
                all_parts.append(self.selected_part)

            for part in all_parts:
                is_selected = (part == self.selected_part)
                is_valid = self.check_valid_position(part)
                
                self.renderer.draw_shape(part, is_selected, is_valid)
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()

    def handle_mouse_down(self, event):
        mouse_x, mouse_y = event.pos
        # Ищем, кликнули ли по детали (проверяем с конца)
        for part in reversed(self.parts + self.placed_parts):
            if (part.x <= mouse_x <= part.right and 
                part.y <= mouse_y <= part.bottom):
                self.selected_part = part
                self.drag_offset = (mouse_x - part.x, mouse_y - part.y)
                
                # Если взяли с листа - временно считаем "в полете" (возвращаем в общий пул визуально)
                if part in self.placed_parts:
                    self.placed_parts.remove(part)
                    self.parts.append(part)
                break

    def handle_mouse_up(self, event):
        if self.selected_part:
            # Проверяем границы и пересечения
            if (self.selected_part.is_inside(self.sheet_w, self.sheet_h) and 
                self.check_valid_position(self.selected_part)):
                
                # Фиксируем на листе
                if self.selected_part in self.parts:
                    self.parts.remove(self.selected_part)
                self.placed_parts.append(self.selected_part)
            else:
                pass
            self.selected_part = None

    def handle_mouse_move(self, event):
        if self.selected_part:
            mouse_x, mouse_y = event.pos
            self.selected_part.x = mouse_x - self.drag_offset[0]
            self.selected_part.y = mouse_y - self.drag_offset[1]

    def check_valid_position(self, current_part):
        for other in self.placed_parts:
            if current_part != other and current_part.intersects(other):
                return False
        return True

    def calculate_efficiency(self):
        if not self.placed_parts: return 0.0
        used_area = sum(p.area for p in self.placed_parts)
        total_area = self.sheet_w * self.sheet_h
        return (used_area / total_area) * 100