# Архитектура проекта Cutting-Optimizer

## System Context Diagram

Диаграмма показывает взаимодействие системы с внешними акторами.

```mermaid
graph TD
    User[👤 Пользователь]
    System[🎮 Cutting Optimizer<br/>Система оптимизации раскроя]
    Pygame[🖼️ Pygame Framework<br/>Графический движок]
    
    User -->|Drag & Drop деталей<br/>Клики по кнопкам<br/>Вращение деталей| System
    System -->|Визуализация<br/>Статистика<br/>Обратная связь| User
    System -->|Рендеринг графики<br/>Обработка событий| Pygame
    Pygame -->|События мыши/клавиатуры<br/>Отрисовка кадров| System
    
    style System fill:#52a8d9,stroke:#333,stroke-width:3px,color:#fff
    style User fill:#2ecc71,stroke:#333,stroke-width:2px,color:#fff
    style Pygame fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
```

---

## Component Diagram

Внутренняя структура приложения с разделением на модули.

```mermaid
graph TB
    subgraph "🎯 Entry Point"
        Main[main.py<br/>Точка входа]
    end
    
    subgraph "🎨 UI Layer"
        Game[pygame_app.py<br/>CuttingGame<br/>- Игровой цикл<br/>- Обработка событий<br/>- Координация]
        Renderer[renderer.py<br/>Renderer<br/>- Отрисовка фигур<br/>- UI элементы<br/>- Визуальные эффекты]
    end
    
    subgraph "🧮 Business Logic"
        BaseAlgo[base.py<br/>PackingAlgorithm<br/>ABC интерфейс]
        FirstFit[first_fit.py<br/>FirstFitDecreasing<br/>- Сортировка по высоте<br/>- Scanline поиск<br/>- Проверка коллизий]
    end
    
    subgraph "📦 Data Models"
        Shape[shape.py<br/>Rectangle, Point<br/>- Геометрия<br/>- Проверка пересечений<br/>- Вращение]
    end
    
    subgraph "🎲 Generators"
        Random[random_parts.py<br/>- Генерация деталей<br/>- Случайные размеры]
    end
    
    Main --> Random
    Main --> Game
    Random --> Shape
    Game --> Renderer
    Game --> FirstFit
    Game --> Shape
    FirstFit --> BaseAlgo
    FirstFit --> Shape
    Renderer --> Shape
    
    style Main fill:#9b59b6,stroke:#333,stroke-width:2px,color:#fff
    style Game fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    style Renderer fill:#1abc9c,stroke:#333,stroke-width:2px,color:#fff
    style FirstFit fill:#e67e22,stroke:#333,stroke-width:2px,color:#fff
    style BaseAlgo fill:#e67e22,stroke:#333,stroke-width:2px,color:#fff
    style Shape fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    style Random fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
```

---

## Sequence Diagram

Основные потоки данных в системе.

### Поток 1: Запуск приложения

```mermaid
sequenceDiagram
    actor User
    participant Main as main.py
    participant Gen as random_parts
    participant Game as CuttingGame
    participant Renderer
    
    User->>Main: python main.py
    Main->>Gen: generate_random_parts(12)
    Gen->>Gen: Создание 12 Rectangle объектов
    Gen-->>Main: List[Rectangle]
    Main->>Game: CuttingGame(parts)
    Game->>Game: Инициализация pygame<br/>Создание окна 1400x900
    Game->>Game: _reset_parts_position()<br/>Размещение в сайдбаре
    Game->>Game: run() - Игровой цикл
    loop Каждый кадр (60 FPS)
        Game->>Renderer: draw_background()
        Game->>Renderer: draw_sheet()
        Game->>Renderer: draw_sidebar(stats)
        Game->>Renderer: draw_shape(part)
        Renderer-->>User: Отображение кадра
    end
```

### Поток 2: Ручное размещение детали

```mermaid
sequenceDiagram
    actor User
    participant Game as CuttingGame
    participant Shape as Rectangle
    
    User->>Game: Mouse Down на детали
    Game->>Game: handle_mouse_down()
    Game->>Game: selected_part = part<br/>drag_offset = (dx, dy)
    Game->>Game: parts.remove(part) если на листе
    
    loop Перетаскивание
        User->>Game: Mouse Move
        Game->>Game: handle_mouse_move()
        Game->>Shape: part.x = mouse_x - offset_x<br/>part.y = mouse_y - offset_y
    end
    
    User->>Game: Mouse Up
    Game->>Game: handle_mouse_up()
    alt Валидная позиция
        Game->>Shape: is_inside(sheet_w, sheet_h)
        Shape-->>Game: True
        Game->>Game: check_valid_position()
        Game->>Game: placed_parts.append(part)
        Game-->>User: Деталь зафиксирована ✅
    else Невалидная позиция
        Game-->>User: Деталь остается в parts ❌
    end
```

### Поток 3: Автоматическая упаковка (AI)

```mermaid
sequenceDiagram
    actor User
    participant Game as CuttingGame
    participant Packer as FirstFitDecreasing
    participant Shape as Rectangle
    
    User->>Game: Клик на "AUTO PACK" кнопку
    Game->>Game: run_auto_pack()
    Game->>Game: all_parts = parts + placed_parts
    Game->>Game: effective_size = sheet - margin*2
    
    Game->>Packer: pack(all_parts, effective_width, effective_height)
    Packer->>Packer: sorted_shapes = sort by height DESC
    
    loop Для каждой детали
        loop Scanline: Y coordinate
            loop X coordinate (шаг=10)
                Packer->>Shape: shape.x = x, shape.y = y
                Packer->>Packer: _has_collision(shape, placed)
                alt Нет коллизий
                    Packer->>Packer: placed_shapes.append(shape)
                    Packer->>Packer: break
                end
            end
        end
    end
    
    Packer-->>Game: List[Rectangle] размещенных
    
    loop Для каждой размещенной
        Game->>Shape: part.x += offset + margin<br/>part.y += offset + margin
    end
    
    Game->>Game: placed_parts = packed_results
    Game->>Game: parts = неразмещенные
    Game->>Game: _reset_parts_position()
    Game-->>User: Статистика обновлена<br/>efficiency: X%
```

---

## Ключевые компоненты

### CuttingGame (pygame_app.py)
**Ответственность:**
- Главный игровой цикл (60 FPS)
- Обработка событий мыши и клавиатуры
- Управление состоянием деталей (parts / placed_parts)
- Расчет эффективности использования листа
- Интеграция с AI упаковщиком

**Основные методы:**
- `run()` - главный цикл
- `handle_mouse_down/up/move()` - drag & drop логика
- `run_auto_pack()` - запуск AI алгоритма
- `calculate_efficiency()` - метрики использования

### FirstFitDecreasing (first_fit.py)
**Алгоритм:**
1. Сортировка деталей по высоте (DESC)
2. Scanline поиск: перебор координат с шагом `step`
3. Проверка пересечений через AABB collision
4. Жадное размещение: первая подходящая позиция

**Параметры:**
- `step=10` - баланс скорости/качества (1=точно, 20=быстро)

### Rectangle (shape.py)
**Данные:**
- Размеры: `width`, `height`
- Позиция: `x`, `y`
- Идентификация: `id`, `color`

**Операции:**
- `intersects(other)` - проверка AABB пересечения
- `is_inside(sheet_w, sheet_h)` - проверка границ
- `rotate()` - поворот на 90°
- `area` - вычисление площади

### Renderer (renderer.py)
**Функции:**
- Отрисовка листа с сеткой и тенями
- Рендеринг деталей с подсветкой и валидацией
- Сайдбар со статистикой
- Кнопка "AUTO PACK" с hover эффектом
- Размерные аннотации

---

## Потоки данных

```mermaid
flowchart LR
    A[Генерация деталей] --> B[Сайдбар<br/>parts list]
    B --> C{Пользователь}
    C -->|Drag & Drop| D[Ручное<br/>размещение]
    C -->|AUTO PACK| E[AI алгоритм<br/>FirstFit]
    D --> F[placed_parts]
    E --> F
    F --> G[Рендер на листе]
    G --> H[Статистика<br/>efficiency %]
```

## Технологический стек

- **Python 3.12.7**
- **Pygame** - графический движок и обработка событий
- **Dataclasses** - модели данных
- **ABC (Abstract Base Classes)** - интерфейсы алгоритмов

## Метрики производительности

- **FPS:** 60 кадров/сек
- **Разрешение:** 1400x900 пикселей
- **Размер листа:** 800x600 мм
- **Шаг алгоритма:** 10 пикселей (настраиваемый)
- **Margin:** 4 мм между деталями
