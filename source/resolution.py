# this script will be used to detect the screen resolution, to which a dictionary of window sizes will be used for all windoes in this app.

#keyword constants
WINDOW = "window"
X = "x"
Y = "y"
FONT = "f"

WIDTH = 0
HEIGHT = 0

# the whole program was built using a HD monitor (1920x1080)
# so all window sizes will be based on the users' monitor resolution and this reference resolution.

STANDARD_X = 1920
STANDARD_Y = 1080

def SetScreenResolution(x, y):
    global WIDTH, HEIGHT, windowSizes
    WIDTH = x
    HEIGHT = y
    windowSizes = {(WINDOW, X): 0.7 * WIDTH, (WINDOW, Y): 0.75 * HEIGHT}

def GetScaledWidth(): return (WIDTH / STANDARD_X)
def GetScaledHeight(): return (HEIGHT / STANDARD_Y)

def sx(x): return int(x * GetScaledWidth())
def sy(y): return int(y * GetScaledHeight())