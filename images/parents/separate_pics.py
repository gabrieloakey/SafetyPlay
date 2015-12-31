from PIL import Image, ImageFilter
import os

def buttons():
    img = Image.open('buttons.png')
    d = {'play' : 0,
           'pause' : 1,
           'rewind' : 2,
           'jump' : 3,
           'stop' : 4,
           'loop' : 5,
           'shuffle' : 6}
    separate(img, d)

def buttons_pressed():
    img = Image.open('buttons_pressed.png')
    d = {'play_pressed' : 0,
           'pause_pressed' : 1,
           'rewind_pressed' : 2,
           'jump_pressed' : 3,
           'stop_pressed' : 4,
           'loop_pressed' : 5,
           'shuffle_pressed' : 6}
    separate(img, d)

def buttons_disabled():
    img = Image.open('buttons_disabled.png')
    d = {'play_disabled' : 0,
           'pause_disabled' : 1,
           'rewind_disabled' : 2,
           'jump_disabled' : 3,
           'stop_disabled' : 4,
           'loop_disabled' : 5,
           'shuffle_disabled' : 6}
    separate(img, d)

def separate(img, d):
    o = 0
    x = img.size[0]
    y = img.size[1]
    keys = list(d.keys())
    values = list(d.values())
    for i in range(0, 14):
        if i in values:
            #L, U, R, D
            c = img.crop([o, 0, o + 48, y])
            for a in range(len(keys)):
                if d[keys[a]] == i:
                    c.save(keys[a] + '.png')
        o += 48

if __name__ == '__main__':
    buttons()
    #buttons_pressed()
    #buttons_disabled()
