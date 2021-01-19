import os
import sys

import pygame

import Minesweeper as ms
import Colours
from Minesweeper import text_to_screen as tts

if sys.platform in ["win32", "win64"]:
    os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()
res = (1024, 600)
screen = pygame.display.set_mode(res)
DEBUGGING_MODE = False
bgColour = None
bomb_count = 50

pygame.display.set_caption("Сапёр")


def options(screen):
    global bomb_count, DEBUGGING_MODE
    running = True
    click = False
    BUTTON_WIDTH = res[0] * 0.3
    BUTTON_HEIGHT = res[1] * 0.06
    window_rect = pygame.Surface.get_rect(screen)
    optionsClock = pygame.time.Clock()

    # элементы интерфейса
    sliderBox = pygame.rect.Rect(window_rect.right // 1.3 - 20, window_rect.centery + window_rect.centery // 3 + 4,
                                 window_rect.width // 5, BUTTON_HEIGHT)
    sliderBall = pygame.rect.Rect(sliderBox.x, sliderBox.y + BUTTON_HEIGHT // 3, 15, 15)
    sliderLine = pygame.rect.Rect(window_rect.right // 1.3 - 20, sliderBall.centery, window_rect.width // 5, 2)
    toggleBox = pygame.rect.Rect(sliderBox.x, sliderBox.y + BUTTON_HEIGHT * 1.5, BUTTON_WIDTH // 2, BUTTON_HEIGHT)
    toggleRect = pygame.rect.Rect(sliderBox.x + ((BUTTON_WIDTH // 4) * DEBUGGING_MODE),
                                  sliderBox.y + BUTTON_HEIGHT * 1.5, BUTTON_WIDTH // 4, BUTTON_HEIGHT)

    # кнопки
    BACK = pygame.rect.Rect(res[0] // 2.7, res[1] * 0.9, BUTTON_WIDTH, BUTTON_HEIGHT)
    mouseHold = False
    sliderBall.centerx = sliderBox.x + bomb_count - 58

    # отрисовка интерфейса
    screen.fill(bgColour)
    drawTitle(screen)
    while running:
        optionsClock.tick(60)
        ms.maskRect(screen, 0, res[1] // 2, res[0], res[1] // 2, bgColour)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                click = True

        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] == 1 and not click:  # проверка удерживания мыши
            mouseHold = True

        if sliderBox.collidepoint(mx, my) and mouseHold:  # взаимодействие с ползунком
            if sliderBall.centerx != (mx + sliderBall.width // 2):
                sliderBall.centerx += (mx - sliderBall.centerx) * 0.25
                bomb_count = (sliderBall.x - sliderBox.x) + 57

        if BACK.collidepoint(mx, my):  # возвращение в меню
            pygame.draw.rect(screen, Colours.BROWN, BACK)
            if click:
                return
        else:
            pygame.draw.rect(screen, Colours.AFGAN_TAN, BACK)

        if toggleBox.collidepoint(mx, my) and click:  # взаимодействие с переключателем режима отладки
            DEBUGGING_MODE = not DEBUGGING_MODE
            if DEBUGGING_MODE:
                toggleRect.x = toggleRect.x + toggleRect.width * DEBUGGING_MODE
            else:
                toggleRect.x = toggleBox.x

        if DEBUGGING_MODE:
            pygame.draw.rect(screen, Colours.WHITE, sliderBox, 1)

        pygame.draw.rect(screen, Colours.WHITE, sliderLine)
        pygame.draw.ellipse(screen, Colours.RED, sliderBall)
        tts(screen, bomb_count, sliderBall.centerx, sliderBall.centery - sliderBall.width // 1.5, colour=Colours.WHITE)

        tts(screen, "Количество мин:", sliderLine.x - res[0] // 2, sliderLine.y, 20, Colours.WHITE)
        tts(screen, " Назад ", BACK.centerx, BACK.centery, 20, Colours.WHITE)
        tts(screen, "Режим отладки", toggleBox.x - res[0] // 2, toggleBox.centery, 20, Colours.WHITE)

        tts(screen, "   ВКЛ                  ВЫКЛ", toggleBox.centerx, toggleBox.centery, 10, colour=Colours.WHITE)
        pygame.draw.rect(screen, Colours.AFGAN_TAN, toggleBox, 1)
        pygame.draw.rect(screen, Colours.CRIMSON, toggleRect)

        mouseHold = False
        click = False
        pygame.display.flip()


def button_action(screen, text):
    text = text.lower()
    if text == 'новая игра':
        ms.game(res, screen, bomb_count, DEBUGGING_MODE)
        mainMenu()
    elif text == 'выход':
        sys.exit()
    elif text == 'настройки':
        options(screen)
        mainMenu()
    else:
        print('ошибка')


def drawTitle(screen):
    rect_border = pygame.rect.Rect(res[0] // 6 - 29, res[1] // 5 - 21, 725, 100)
    pygame.draw.rect(screen, Colours.MAHOGANY, rect_border)
    pygame.draw.rect(screen, Colours.GOLD, rect_border, 1)
    # эмуляция эффекта 3D тени путем создания копий текста с небольшим смещением в черный цвет
    tts(screen, "САПЁР", res[0] // 2 + 7, res[1] // 4 - 5, 60, Colours.BLACK)
    tts(screen, "САПЁР", res[0] // 2 + 6, res[1] // 4 - 3, 60, Colours.BLACK)
    tts(screen, "САПЁР", res[0] // 2 + 5, res[1] // 4 - 1, 60, Colours.BLACK)
    tts(screen, "САПЁР", res[0] // 2 + 4, res[1] // 4 + 1, 60, Colours.BLACK)
    tts(screen, "САПЁР", res[0] // 2 + 3, res[1] // 4 + 2, 60, Colours.BLACK)
    tts(screen, "САПЁР", res[0] // 2 + 2, res[1] // 4 + 4, 60, Colours.BLACK)
    tts(screen, "САПЁР", res[0] // 2 + 1, res[1] // 4 + 6, 60, Colours.BLACK)
    tts(screen, "САПЁР", res[0] // 2, res[1] // 4 + 8, 60, Colours.GOLD)


def mainMenu():
    global bgColour
    global bomb_count
    running = True
    window_rect = pygame.Surface.get_rect(screen)
    mainClock = pygame.time.Clock()
    BUTTON_WIDTH = res[0] * 0.3
    BUTTON_HEIGHT = res[1] * 0.06

    # кнопки
    NEW_GAME = pygame.rect.Rect(window_rect.centerx - (BUTTON_WIDTH / 2),
                                window_rect.centery + BUTTON_HEIGHT * 1.5,
                                BUTTON_WIDTH, BUTTON_HEIGHT)

    OPTIONS = pygame.rect.Rect(window_rect.centerx - (BUTTON_WIDTH / 2),
                               window_rect.centery + BUTTON_HEIGHT * 3.0,
                               BUTTON_WIDTH, BUTTON_HEIGHT)

    EXIT = pygame.rect.Rect(window_rect.centerx - (BUTTON_WIDTH / 2),
                            window_rect.centery + BUTTON_HEIGHT * 4.5,
                            BUTTON_WIDTH, BUTTON_HEIGHT)

    buttons = {"Новая игра": NEW_GAME, "Настройки": OPTIONS, "Выход": EXIT}

    click = False

    bgColour = Colours.BLUE_STONE
    screen.fill(bgColour)
    drawTitle(screen)

    for button in buttons:
        pygame.draw.rect(screen, Colours.AFGAN_TAN, buttons[button])
        tts(screen, button, buttons[button].centerx, buttons[button].centery, 20, colour=Colours.WHITE)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                click = True

        mx, my = pygame.mouse.get_pos()

        for button in buttons:
            if buttons[button].collidepoint(mx, my):
                pygame.draw.rect(screen, Colours.BROWN, buttons[button])
                if click:
                    button_action(screen, button)
                    # восстановить экран
                    screen.fill(bgColour)
                    drawTitle(screen)
            else:
                pygame.draw.rect(screen, Colours.AFGAN_TAN, buttons[button])
            tts(screen, button, buttons[button].centerx, buttons[button].centery, 20, colour=Colours.WHITE)

        click = False
        mainClock.tick(60)
        pygame.display.flip()


mainMenu()
