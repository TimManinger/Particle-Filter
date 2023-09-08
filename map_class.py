"""
The map class holds the original image for the robot to reference, an
edited copy for displaying, and the methods necessary to interact
with the map using coordinates where the origin is at the center.
The map also holds the true position of the robot and generates the
displacement vectors and starting positions.
"""
import numpy as np
import cv2

class Map(object):

    # map initializer, sets all member variables to defaults and loads image
    def __init__(self, filename):
        # cv2 reads in the image in BGR not RGB
        # this copy will change and be displayed
        self.img = np.array(cv2.imread(filename, 1))

        # this copy will stay the same so the robot can reference it
        self.orig = np.array(cv2.imread(filename, 1))

        # generate bounds (mins assumed 0 for now)
        self.xMax = len(self.img)
        self.yMax = len(self.img[0])
        self.xMapMax, self.yMapMax = self.cvToMap(self.xMax, self.yMax)

    # return RGB version of img for requirement of RGB
    def imgRGB(self):
        b,g,r = cv2.split(self.img)
        return cv2.merge([r,g,b])

    # reset img to reference for each frame
    def imgReset(self):
        self.img = self.orig.copy() # NOT by reference

    # compensating to put origin in the center by converting cv2 coords
    def cvToMap(self, x, y):
        x = x - (len(self.img) // 2)
        y = (len(self.img[0]) // 2) - y
        return (int(x), int(y))

    # ability to convert back in order to interac with the map directly
    def mapToCV(self, x, y):
        x = x + (len(self.img) // 2)
        y = (len(self.img[0]) // 2) - y
        return (int(x), int(y))

    # generate random x,y position in range (all cv2 coords)
    def randPos(self, border):
        posX = 0
        posY = 0
        posX = int(np.random.uniform(self.xMax-border, border, 1))
        posY = int(np.random.uniform(self.yMax-border, border, 1))
        posX, posY = self.cvToMap(posX, posY)
        return (posX, posY)

    # generate random movement vector curX and curY are center origin coords.
    # considered putting in robot class,
    # needs access to true position and motion for validation though
    # so I put it here instead.
    # **THIS VECTOR DOES NOT HAVE NOISE ADDED**
    def randMovVec(self, curX, curY, border = 100, speed = 50):
        curX, curY = self.mapToCV(curX, curY)
        # generate fractional values for x and y components
        dX = float(np.random.uniform(0, 1, 1))
        dY = float(((1 - (dX**2))**.5))
        # randomize direction
        p = np.random.randint(1, 6, 1)
        if p == 1:
            dX *= -1
        elif p == 2:
            dX *= -1
            dY *= -1
        elif p == 3:
            dY *= -1
        # apply speed
        dX *= speed
        dY *= speed
        dX = int(dX)
        dY = int(dY)
        return (int(dX), int(dY))

    # for adding noise to movement vector, supports per axis noise
    def addNoise(self, x, y, varX, varY):
        x += (x * np.random.randn() * varX)
        y += (y * np.random.randn() * varY)
        return (int(x), int(y))

    def inBounds(self, x, y, buf):
        if (x > (self.xMapMax - buf)) or (x < (-1*(self.xMapMax + buf))):
            #print("X", x, self.xMapMax)
            return False
        if (y < (self.yMapMax + buf)) or (y > ((-1*self.yMapMax) - buf)):
            #print("Y", y, self.yMapMax)
            return False
        return True

    # draw a circle centered on the 50x50 region the point is in
    # x and y are map coords (origin at center)
    def drawCircle(self, x, y, color = (255,255,255), radius = 20, line = -1, outline = True):
        x, y = self.mapToCV(x, y)
        if outline:
            self.img = cv2.circle(self.img, (x, y), int(radius) + 5, (0,0,0), line)
        self.img = cv2.circle(self.img, (x, y), int(radius) + 1, color, line)

    # draw a black grid over an image with a certain spacing
    def drawGrid(self, spacing = 50, line = 2, color = (0,0,0)):
        x = 0
        y = 0
        while x < len(self.img):
            self.img = cv2.line(self.img, (x, 0), (x, len(self.img[0])), color, line)
            x += spacing
        while y < len(self.img[0]):
            self.img = cv2.line(self.img, (0, y), (len(self.img), y), color, line)
            y += spacing
        self.img = cv2.line(self.img, (0, len(self.img[0])//2), (len(self.img), len(self.img[0])//2), (255,255,255), line)
        self.img = cv2.line(self.img, (len(self.img)//2, 0), (len(self.img)//2, len(self.img[0])), (255,255,255), line)

    def drawText(self, text = 'OpenCV', tX = 0, tY = 100, color = (255,255,255)):
        # draw text with cv2
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(self.img, text, (tX,tY), font, 4, (0,0,0), 15, cv2.LINE_AA)
        cv2.putText(self.img, text, (tX,tY), font, 4, color, 3, cv2.LINE_AA)
