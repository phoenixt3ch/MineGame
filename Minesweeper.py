import math
import random
import sys

import pygame

import Tile
import Colours

DEBUGGING_MODE = False
score = 0
GameOver = False


def cartToIso(cartX, cartY):
    isoX = (cartX - cartY)
    isoY = (cartX + cartY) / 2
    pos = (isoX, isoY)
    return pos


def isoToCart(isoX, isoY):
    cartX = ((2 * isoY + isoX) / 2)
    cartY = ((2 * isoY - isoX) / 2)
    pos = (cartX, cartY)
    return pos


def createGrid(rows, columns, TileWidth, TileHeight, centerX, centerY):
    pList = []
    row = []
    for x in range(rows):
        for y in range(columns):
            cartX = x * TileWidth / 2
            cartY = y * TileHeight
            isoX, isoY = cartToIso(cartX, cartY)
            isoX += centerX
            isoY += centerY
            poly = Tile.Tile(isoX, isoY, TileWidth, TileHeight, Colours.ARMOUR)
            poly.defaultColour = Colours.ARMOUR
            row.append(poly)
        pList.append(row)
        row = []
    return pList


def populate(screen, grid, count, blockX, blockY, limX,
             limY):  # blockX, blockY = плитки при первом нажатии. LimX,limY = границы сетки
    while count > 0:
        randX = random.randint(1, limX) - 1
        randY = random.randint(1, limY) - 1
        if grid[randX][randY].isBomb or (
                blockX - 1 <= randX <= blockX + 1 and blockY - 1 <= randY <= blockY + 1):  # создание безопасной зоны
            # 3x3 при первом нажатии
            continue
        else:
            grid[randX][randY].isBomb = True
            grid[randX][randY].value = -1
            grid[randX][randY].state = 'MINED'
            if DEBUGGING_MODE:
                pygame.draw.polygon(screen, Colours.MAHOGANY, grid[randX][randY].poly)
                pygame.draw.polygon(screen, Colours.BLACK, grid[randX][randY].poly, 1)
            count -= 1
    return grid


def generateValues(screen, grid, limX, limY):
    for i in range(limX):
        for j in range(limY):
            if grid[i][j].value == -1:
                continue
            else:
                grid[i][j].value = countNeighbours(grid, i, j, limX, limY)
                if grid[i][j].value == 0 and DEBUGGING_MODE:
                    pygame.draw.polygon(screen, Colours.EMERALD, grid[i][j].poly)
                    pygame.draw.polygon(screen, Colours.BLACK, grid[i][j].poly, 1)
                elif grid[i][j].value == 1 and DEBUGGING_MODE:
                    pygame.draw.polygon(screen, Colours.NAVY_BLUE, grid[i][j].poly)
                    pygame.draw.polygon(screen, Colours.BLACK, grid[i][j].poly, 1)


def countNeighbours(grid, blockX, blockY, limX, limY):
    n = 0
    for i in range(-1, 2):
        if not (-1 < blockX + i < limX):
            continue
        for j in range(-1, 2):
            if not (-1 < blockY + j < limY):
                continue
            if grid[blockX + i][blockY + j].isBomb:
                n += 1
    return n


def revealBlocks(screen, image, grid, blockX, blockY, limX, limY):
    block = grid[blockX][blockY]
    if block.value != -1 and block.state != 'WARN':
        block.isClicked = True
        block.colour = Colours.GOLD
        block.state = 'SAFE'
        screen.blit(image, (block.spriteX, block.spriteY))
        pygame.draw.aalines(screen, (0, 0, 0), 1, block.poly)  # контур
        if block.value > 0:
            text_to_screen(screen, block.value, block.centerX, block.centerY)
        else:
            for i in range(-1, 2):
                if not (-1 < blockX + i < limX):
                    continue
                for j in range(-1, 2):
                    if not (-1 < blockY + j < limY):
                        continue
                    if grid[blockX + i][blockY + j].state == 'UNKNOWN':
                        grid[blockX + i][blockY + j].state = 'SAFE'
                        revealBlocks(screen, image, grid, blockX + i, blockY + j, limX, limY)


def text_to_screen(screen, text, x, y, size=10, colour=None, font_type=None):
    if colour is None:
        colour = Colours.Colourlist[text]
    text = str(text)
    if font_type is None:
        font = pygame.font.SysFont('Arial', size, True)
    else:
        font = font_type
    text_width, text_height = font.size(text)
    text = font.render(text, True, colour)
    tRect = screen.blit(text, (x - (text_width / 2), y - (text_height / 2)))
    return tRect


def findRange(screen, grid, blockX, blockY, limX, limY, TileSpriteList):
    # выделение сетки 3х3, можно использовать алгоритм получше
    global GameOver
    flags = 0
    correct_bombs = 0
    bombs = 0
    blocks_in_range = []
    for i in range(-1, 2):
        if -1 < blockX + i < limX:
            for j in range(-1, 2):
                if -1 < blockY + j < limY:
                    blocks_in_range.append((grid[blockX + i][blockY + j], blockX + i, blockY + j))
                    if grid[blockX + i][blockY + j].state == 'WARN':
                        flags += 1
                    if grid[blockX + i][blockY + j].isBomb:
                        bombs += 1
                    if grid[blockX + i][blockY + j].isBomb and grid[blockX + i][blockY + j].state == 'WARN':
                        correct_bombs += 1

    for blocks in blocks_in_range:
        screen.blit(TileSpriteList['SELECT'], blocks[0].spritePOS)
        if flags != correct_bombs and flags > 0:
            drawBombs(screen, grid, limX, TileSpriteList['BOMB'])
            GameOver = True
            break
        if correct_bombs == bombs and blocks[0].state == 'UNKNOWN':
            revealBlocks(screen, TileSpriteList['SAFE'], grid, blocks[1], blocks[2], limX, limY)
            blocks_in_range.remove(blocks)
    return blocks_in_range


def drawBombs(screen, grid, limX, Tile_BOMB, delay=10):
    BOMB = pygame.Surface(Tile_BOMB.get_size()).convert_alpha()
    BOMB.fill(Colours.MAHOGANY)
    Tile_BOMB.blit(BOMB, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    bombList = []
    for i in range(limX):
        for Tile in grid[i]:
            if Tile.isBomb and not Tile.isClicked and Tile.state != 'WARN':
                bombList.append(Tile)

    tempClock = pygame.time.Clock()
    startTicks = 0
    listLength = len(bombList)
    while bombList:  # запускать пока список бомб не опустеет, анимация взрыва бомб (раскрытие случайных бомб)
        for event in pygame.event.get():  # зависает и вылетает без обработки событий
            if event.type == pygame.QUIT:
                break
                pygame.quit()
                sys.exit()

        if startTicks == 0:
            startTicks = pygame.time.get_ticks()

        ticks = (pygame.time.get_ticks() - startTicks)

        if (ticks % delay) == 0:
            randIndex = random.randint(0, listLength - 1)
            screen.blit(Tile_BOMB, bombList[randIndex].spritePOS)  # спрайт бомб
            pygame.draw.aalines(screen, Colours.BLACK, 0, bombList[randIndex].poly)  # отрисовка контура
            bombList.remove(bombList[randIndex])
            listLength = len(bombList)
            delay -= 1.5 if delay > 1.5 else 0  # ускорение процесса
            pygame.display.flip()

        tempClock.tick(60)


def ui_drawRRect(screen, x, y, colour, width, height, radius, outline=0):  # рисует прямоугольник со скругленными углами

    widthVert = width - 2 * radius
    heightHori = height - 2 * radius
    rectVert = pygame.rect.Rect((x + radius), y, widthVert, height)
    rectHori = pygame.rect.Rect(x, (y + radius), width, heightHori)
    pygame.draw.rect(screen, colour, rectVert, outline)
    pygame.draw.rect(screen, colour, rectHori, outline)
    pygame.draw.circle(screen, colour, ((x + radius), (y + radius)), radius, outline)  # верхний левый угол
    pygame.draw.circle(screen, colour, ((x + (width - radius)), (y + radius)), radius, outline)  # верхний правый угол
    pygame.draw.circle(screen, colour, ((x + radius), (y + (height - radius))), radius, outline)  # нижний левый угол
    pygame.draw.circle(screen, colour, ((x + (width - radius)), (y + (height - radius))), radius,
                       outline)  # нижний правый угол

    rect = pygame.rect.Rect(x, y, width, height)

    return rect


def drawHUD(screen, res):
    HUD = pygame.rect.Rect(0, 0, res[0], res[1] // 8 - 2)
    pygame.draw.rect(screen, Colours.BLACK, HUD)
    pygame.draw.line(screen, Colours.DARK_SALMON, (0, HUD.height), (HUD.width, HUD.height))
    button1 = ui_drawRRect(screen, res[0] // 25, res[1] // 100, Colours.MYRTLE, 120, 30, 2)
    button2 = ui_drawRRect(screen, res[0] // 25, res[1] // 15, Colours.MYRTLE, 120, 30, 2)

    return HUD, button1, button2


def maskRect(screen, maskX, maskY, maskWidth, maskHeight, maskColour):
    # рисует прямоугольник чтобы очистить часто обновляемую часть
    t_rect = pygame.rect.Rect(maskX, maskY, maskWidth, maskHeight)
    pygame.draw.rect(screen, maskColour, t_rect)
    return t_rect


def drawTimer(screen, HUD, tick):
    # всегда сохраняется формат ХХХ
    if tick < 10:
        tick = "00" + str(tick)
    elif 100 > tick > 9:
        tick = "0" + str(tick)
    else:
        tick = str(tick)
    timeFont = pygame.font.Font("data/SevenSegment.ttf", 70)
    x = HUD.centerx - HUD.width // 16  # такой Х, чтобы таймер был в центре
    y = HUD.height // 6
    rect = pygame.rect.Rect(x, y, HUD.width // 8.3, HUD.height // 1.5)
    pygame.draw.rect(screen, Colours.MYRTLE, rect)
    text_to_screen(screen, tick, rect.centerx, rect.centery, rect.width * 0.8, Colours.RAINEE, timeFont)


def drawDebug(screen, res, TileSpriteList):
    if DEBUGGING_MODE:
        for i, j in enumerate(TileSpriteList):
            screen.blit(TileSpriteList[j], (i * 40, res[1] // 7.5))
        text_to_screen(screen, "Режим отладки", 50, res[1] // 5, colour=Colours.WHITE, size=10)
    else:
        return


def resetGame(res, screen, bomb_count):
    game(res, screen, bomb_count, DEBUGGING_MODE)


def goMainMenu():
    from Menu import mainMenu
    mainMenu()


def gameOverDialogue(screen, res, score, remaining_bombs):
    bodyWidth = 200
    bodyHeight = 250
    body = pygame.rect.Rect(res[0] // 2 - bodyWidth // 2, res[1] // 2 - bodyHeight // 4, bodyWidth, bodyHeight)
    buttonWidth = int(bodyWidth - bodyWidth * 0.1)
    buttonheight = int(bodyHeight * 0.15)
    buttonX = int(body.x + body.width * 0.05)
    pygame.draw.rect(screen, Colours.BLACK, body)
    pygame.draw.rect(screen, Colours.DARK_SALMON, body, 1)

    if not remaining_bombs:
        text_to_screen(screen, "Победа!", body.centerx, body.y + body.height * 0.1, size=40, colour=Colours.RAINEE)
    else:
        text_to_screen(screen, "Поражение", body.centerx, body.y + body.height * 0.1, size=35, colour=Colours.RAINEE)

    text_to_screen(screen, "Счет: ", body.centerx - body.width * 0.3 + 5, body.y + body.height * 0.3, size=20,
                   colour=Colours.RAINEE)
    text_to_screen(screen, int(score), body.centerx + body.width * 0.3 + 10, body.y + body.height * 0.3, size=20,
                   colour=Colours.RAINEE)

    button_reset = ui_drawRRect(screen, buttonX, body.y + int(body.height * 0.4), Colours.MYRTLE, buttonWidth,
                                buttonheight,
                                2)
    button_quit = ui_drawRRect(screen, buttonX, body.y + int(body.height * 0.8), Colours.MYRTLE, buttonWidth,
                               buttonheight,
                               2)
    button_Menu = ui_drawRRect(screen, buttonX, body.y + int(body.height * 0.6), Colours.MYRTLE, buttonWidth,
                               buttonheight,
                               2)
    return body, button_reset, button_quit, button_Menu


def game(res, screen, bomb_count, debug=False):
    global DEBUGGING_MODE, score, GameOver
    DEBUGGING_MODE = debug

    # типа спрайты
    Tile_GRASS = pygame.image.load("data/Grass.png").convert_alpha()
    Tile_DIRT = pygame.image.load("data/Dirt.png").convert_alpha()
    Tile_FLAG = pygame.image.load("data/Flag.png").convert_alpha()
    Tile_SELECT = pygame.image.load("data/Select.png").convert_alpha()
    Tile_BOMB = pygame.image.load("data/Mine.png").convert_alpha()
    Tile_EDGE = pygame.image.load("data/Edge.png").convert_alpha()
    TileSpriteList = {'WARN': Tile_FLAG,
                      'SAFE': Tile_DIRT,
                      'UNKNOWN': Tile_GRASS,
                      'MINED': Tile_GRASS,
                      'SELECT': Tile_SELECT,
                      'EDGE': Tile_EDGE,
                      'BOMB': Tile_BOMB,
                      }
    # свойства поля
    TileWidth = 32
    TileHeight = 16
    centerX = 512
    centerY = 75
    rows = 33
    columns = 33
    pList = createGrid(rows, columns, TileWidth, TileHeight, centerX, centerY)
    highlighted_Tile = pList[0][0]
    limX = rows - 1  # одна строка и столбец для висящих краев
    limY = columns - 1
    score = 0

    # Свойства игры
    running = True
    blockX = 0
    blockY = 0
    firstClick = True
    bomb_count_approx = bomb_count
    clock = pygame.time.Clock()
    FPS = 60
    MMB = False  # проверка нажатия скм
    MMB2 = False  # проверка, что скм больше не нажата
    blit_cache = []
    startTicks = 0
    prevtick = -1

    # отрисовка
    screen.fill(Colours.BLUE_STONE)
    HUD, button_reset, button_menu = drawHUD(screen, res)
    drawTimer(screen, HUD, 0)
    text_to_screen(screen, "Меню", button_menu.centerx, button_menu.centery, 15, Colours.RAINEE)
    text_to_screen(screen, "Заново", button_reset.centerx, button_reset.centery, 15, Colours.RAINEE)

    drawDebug(screen, res, TileSpriteList)

    for x in range(len(pList) - 1):  # отрисовка основной сетки
        for Tile in pList[x]:
            screen.blit(Tile_GRASS, (Tile.spriteX, Tile.spriteY))
            pygame.draw.aalines(screen, (0, 0, 0), 1, Tile.poly, 1)

    for x in range(rows):  # отрисовка висящих краев
        screen.blit(Tile_EDGE, pList[rows - 1][x].spritePOS)
        screen.blit(Tile_EDGE, pList[x][columns - 1].spritePOS)

    while running:  # основной цикл
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                MMB = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                MMB2 = True

        clock.tick(FPS)
        mousex, mousey = pygame.mouse.get_pos()
        if not GameOver:  # заморозка обработки если проигрыш

            isoMouseX = (2 * (mousey - centerY) + (mousex - centerX))  # (2 * mousePositionY + mousePositionX)
            isoMouseY = (2 * (mousey - centerY) - (mousex - centerX)) / 2  # (2 * mousePositionY - mousePositionX)
            blockX = math.floor(isoMouseX / TileWidth) if -1 < math.floor(isoMouseX / TileWidth) < limX else blockX
            blockY = math.floor(isoMouseY / TileHeight) if -1 < math.floor(
                isoMouseY / TileHeight) < limY else blockY
            TileHover = pList[blockX][blockY]

            if not firstClick:  # таймер запускается после первого щелчка
                if startTicks == 0:
                    startTicks = pygame.time.get_ticks()
                current_ticks = (pygame.time.get_ticks() - startTicks) // 1000
                if prevtick != current_ticks:  # предотвращает вызов этой функции чаще одного раза в секунду
                    prevtick = current_ticks
                    drawTimer(screen, HUD, prevtick)

            # --------------------------Handling Mouse Clicks--------------------------#
            if pygame.mouse.get_pressed()[0] and not HUD.collidepoint(mousex,
                                                                      mousey) and TileHover.state != 'WARN':  #
                # обработка нажатия лкм
                pygame.time.wait(60)
                TileHover.isClicked = True
                if firstClick:  # генерация бомб в сетке, также значений, и открытие первой части безопасных плиток
                    pList = populate(screen, pList, bomb_count, blockX, blockY, limX, limY)
                    generateValues(screen, pList, limX, limY)
                    revealBlocks(screen, Tile_DIRT, pList, blockX, blockY, limX, limY)
                    firstClick = False

                if TileHover.value == 0:  # показать кусок безопасных плиток, если поблизости нет мин
                    revealBlocks(screen, Tile_DIRT, pList, blockX, blockY, limX, limY)

                    # показывать только одну плитку, если поблизости есть мины
                elif not TileHover.isBomb and TileHover.state != 'WARN' and TileHover.state != 'SAFE':
                    TileHover.colour = Colours.GOLD
                    TileHover.state = 'SAFE'
                    screen.blit(Tile_DIRT, (TileHover.spriteX, TileHover.spriteY))
                    pygame.draw.aalines(screen, (0, 0, 0), 1, TileHover.poly)  # контур
                    text_to_screen(screen, TileHover.value, TileHover.centerX, TileHover.centerY)

                elif TileHover.isBomb and TileHover.state != 'WARN':  # конец игры при нажатии бомбы
                    TileHover.isClicked = True
                    screen.blit(Tile_BOMB, TileHover.spritePOS)
                    pygame.draw.aalines(screen, (0, 0, 0), 1, TileHover.poly)  # контур
                    drawBombs(screen, pList, limX, Tile_BOMB)
                    GameOver = True

            if pygame.mouse.get_pressed()[2] and not HUD.collidepoint(mousex, mousey):  # пкм
                pygame.time.wait(100)
                if TileHover.state != 'WARN' and not TileHover.isClicked:  # ставится флажок, если плитка не
                    # отмечена или не нажата
                    TileHover.state = 'WARN'
                    TileHover.colour = Colours.GRAY
                    bomb_count_approx -= 1
                    if TileHover.isBomb:
                        score += (bomb_count * 0.1 + 5)
                    screen.blit(Tile_FLAG, TileHover.spritePOS)
                    pygame.draw.aalines(screen, (0, 0, 0), 1, TileHover.poly)  # контур

                elif TileHover.state == 'WARN' and not TileHover.isClicked:  # убрать флажок если плитка не
                    # нажата или отмечена
                    TileHover.state = 'UNKNOWN'
                    TileHover.colour = TileHover.defaultColour
                    bomb_count_approx += 1
                    if TileHover.isBomb:
                        score -= (bomb_count * 0.1 + 5)
                    screen.blit(Tile_GRASS, (TileHover.spriteX, TileHover.spriteY))
                    pygame.draw.aalines(screen, (0, 0, 0), 1, TileHover.poly)

            if MMB and not firstClick:
                # Действие скм. Не работает пока не сделан первый клик, можно улучшить в будущем алгоритм
                pygame.time.wait(70)
                blit_cache = findRange(screen, pList, blockX, blockY, limX, limY, TileSpriteList)
            elif MMB2:  # как только скм не нажата
                for items in blit_cache:
                    screen.blit(TileSpriteList[items[0].state], items[0].spritePOS)
                    if items[0].value > 0 and items[0].state == 'SAFE':
                        text_to_screen(screen, items[0].value, items[0].centerX, items[0].centerY)
                    pygame.draw.aalines(screen, (0, 0, 0), 1, items[0].poly)
                blit_cache = []

            # Обработка щелчков мыши

            if button_menu.collidepoint(mousex, mousey) and pygame.mouse.get_pressed()[0]:  # возврат в меню при нажатии
                pygame.time.wait(60)
                pList = []
                goMainMenu()

            if button_reset.collidepoint(mousex, mousey) and pygame.mouse.get_pressed()[0]:
                pygame.time.wait(60)
                highlighted_Tile = None
                pList = []
                resetGame(res, screen, bomb_count)

            # очистка предыдущей выбранной клетки и отрисовка старого спрайта
            if pList != [] and highlighted_Tile != TileHover and not DEBUGGING_MODE:
                screen.blit(TileSpriteList[highlighted_Tile.state], highlighted_Tile.spritePOS)
                pygame.draw.aalines(screen, (0, 0, 0), 1, highlighted_Tile.poly)

                # отрисовка выделенного спрайта над данной плиткой
                if highlighted_Tile.value > 0 and highlighted_Tile.state == 'SAFE':
                    text_to_screen(screen, highlighted_Tile.value, highlighted_Tile.centerX, highlighted_Tile.centerY)

                highlighted_Tile = TileHover
                screen.blit(Tile_SELECT, highlighted_Tile.spritePOS)
                pygame.draw.aalines(screen, (0, 0, 0), 1, highlighted_Tile.poly)

            # утилиты
            if bomb_count_approx == 0:  # достигнута победа
                GameOver = True

            if DEBUGGING_MODE:  # обновлять каждый раз счет
                maskRect(screen, 30, 140, 100, 20, Colours.BLUE_STONE)
                text_to_screen(screen, "Счёт:", 50, 150, colour=Colours.MAHOGANY, size=15)
                text_to_screen(screen, int(score), 100, 150, colour=Colours.MAHOGANY, size=20)

        # Обработка событий после окончания игры
        else:
            highlighted_Tile = None
            pList = []
            p_body, p_reset, p_quit, p_menu = gameOverDialogue(screen, res, score, bomb_count_approx)
            text_to_screen(screen, "Заново", p_reset.centerx, p_reset.centery, 18, colour=Colours.RAINEE)
            text_to_screen(screen, "Меню", p_menu.centerx, p_menu.centery, 18, colour=Colours.RAINEE)
            text_to_screen(screen, "Выход", p_quit.centerx, p_quit.centery, 18, colour=Colours.RAINEE)

            if pygame.mouse.get_pressed()[0]:

                if p_reset.collidepoint(mousex, mousey):
                    GameOver = False
                    pygame.time.wait(100)
                    resetGame(res, screen, bomb_count)

                elif p_menu.collidepoint(mousex, mousey):
                    GameOver = False
                    pygame.time.wait(100)
                    goMainMenu()

                elif p_quit.collidepoint(mousex, mousey):
                    pygame.quit()
                    sys.exit()

        MMB = False
        MMB2 = False
        pygame.display.flip()
