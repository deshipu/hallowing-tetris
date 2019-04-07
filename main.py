import board
import audioio
import touchio
import random
import displayio
import time


class Brick:
    BRICKS = b'ftqr\xf0'
    ROTATIONS = [
        (1, 0, 0, 1, -1, -1),
        (0, 1, -1, 0, -1, 0),
        (-1, 0, 0, -1, -2, 0),
        (0, -1, 1, 0, -2, -1),
    ]

    def __init__(self, kind):
        self.x = 7
        self.y = 4
        self.color = kind % 5 + 1
        self.rotation = 0
        self.kind = kind

    def draw(self, image, color=None):
        if color is None:
            color = self.color
        data = self.BRICKS[self.kind]
        rot = self.ROTATIONS[self.rotation]
        mask = 0x01
        for y in range(2):
            y += rot[5]
            for x in range(4):
                x += rot[4]
                if data & mask:
                    try:
                        image[self.x + x * rot[0] + y * rot[1],
                              self.y + x * rot[2] + y * rot[3]] = color
                    except IndexError:
                        pass
                mask <<= 1

    def hit(self, image, dx=0, dy=0, dr=0):
        data = self.BRICKS[self.kind]
        rot = self.ROTATIONS[(self.rotation + dr) % 4]
        mask = 0x01
        for y in range(2):
            y += rot[5]
            for x in range(4):
                x += rot[4]
                if data & mask:
                    try:
                        if image[self.x + dx + x * rot[0] + y * rot[1],
                                 self.y + dy + x * rot[2] + y * rot[3]]:
                            return True
                    except IndexError:
                        return True
                mask <<= 1
        return False


palette = displayio.Palette(6)
palette[0] = 0x111111
palette[1] = 0xaa0099
palette[2] = 0x22aa00
palette[3] = 0xee00bb
palette[4] = 0xbbee00
palette[5] = 0xbb00ee
screen = displayio.Bitmap(16, 20, 6)
grid = displayio.TileGrid(screen, pixel_shader=palette, x=0, y=-4)
root = displayio.Group(scale=8)
root.append(grid)
board.DISPLAY.show(root)
left = touchio.TouchIn(board.A5)
inner_left = touchio.TouchIn(board.A4)
inner_right = touchio.TouchIn(board.A3)
right = touchio.TouchIn(board.A2)
audio = audioio.AudioOut(board.SPEAKER)
music = open("tetris.wav", "rb")
audio.play(audioio.WaveFile(music), loop=True)

brick = Brick(random.randint(0, 4))
tick = time.monotonic()
while True:
    board.DISPLAY.refresh_soon()
    move_left = False
    move_right = False
    rotate_left = False
    rotate_right = False
    tick += 0.5
    while True:
        time.sleep(0.075)
        move_left= move_left or left.value
        move_right = move_right or right.value
        rotate_left = rotate_left or inner_left.value
        rotate_right = rotate_right or inner_right.value
        if tick <= time.monotonic():
            break
    brick.draw(screen, 0)
    if brick.hit(screen, 0, 1):
        brick.draw(screen)
        brick = Brick(random.randint(0, 4))
        if brick.hit(screen, 0, 0):
            break
    else:
        brick.y += 1
    if move_right and not brick.hit(screen, 1, 0):
        brick.x += 1
    if move_left and not brick.hit(screen, -1, 0):
        brick.x -= 1
    if rotate_right and not brick.hit(screen, 0, 0, 1):
        brick.rotation = (brick.rotation + 1) % 4
    if rotate_left and not brick.hit(screen, 0, 0, -1):
        brick.rotation = (brick.rotation - 1) % 4

    brick.draw(screen)
