class Tile:
    """
      Класс плиток для хранения всех точек в многоугольниках в виде плиток, а также некоторых других свойств.
       каждая плитка имеет некоторые свойства, которые сохраняются в каждом экземпляре этого класса,
       каждая плитка также имеет сохраненные состояния и цвета

      STATES =
        'MINED',  : на плитке сейчас есть бомба
        'WARN',   : плитка помечена как потенциальная бомба
        'SAFE',   : плитка раскрыта и безопасна (val> -1)
        'UNKNOWN' : плитка не раскрывается и не отмечается
    """

    def __init__(self, isoX, isoY, tileWidth, tileHeight, colour=(255, 255, 255)):
        self.isoX = isoX
        self.isoY = isoY
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.enQueued = False
        self.colour = colour
        self.defaultColour = (255, 255, 255)
        self.poly = (
            (isoX, isoY),  # вверх
            (isoX - tileWidth / 2, isoY + tileHeight / 2),  # влево
            (isoX, isoY + tileHeight),  # вниз
            (isoX + tileWidth / 2, isoY + tileHeight / 2),  # вправо
        )
        self.spriteX = isoX - (tileWidth // 2)
        self.spriteY = isoY
        self.spritePOS = (self.spriteX, self.spriteY)
        self.centerX = isoX
        self.centerY = isoY + (tileHeight / 2)
        self.isClicked = False
        self.state = 'UNKNOWN'
        self.isBomb = False
        self.value = 0
