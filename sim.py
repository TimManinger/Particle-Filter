"""
The simulator itself will handle iterating through timesteps and remembering
state information at each one. It will instatiate the objects and ordering
the steps at each loop.

***CLOSE WITH ESCAPE NOT WITH WINDOW X***

window x will strand the program, opencv has no method of avoiding this and
I am not learning Qt or GTK just for that.
"""
import map_class as m
import robot_class as r
import numpy as np
import cv2

# the state probability function that will be passed to the robot
# probability based on Euclidean distance
def euclidean(origMap, ref, p):
    # it randomly fails to retrieve the subImages, I haven't
    # found a reason or pattern, so I'm just making it not crash
    try:
        bM,gM,rM = cv2.split(origMap)
    except:
        #print("bad particle")
        return 0
    try:
        bR,gR,rR = cv2.split(ref)
    except:
        #print("bad agent")
        return p
    vM = np.array((np.mean(bM), np.mean(gM), np.mean(rM)))
    vR = np.array((np.mean(bR), np.mean(gR), np.mean(rR)))
    return (1/np.linalg.norm(vM-vR)+.001)*20

# looks at blue channel histograms
def histogram(origMap, ref, p):
    try:
        histOrig = cv2.calcHist([origMap],[0],None,[256],[0,256])
    except:
        #print("bad particle")
        return 0
    try:
        histRef = cv2.calcHist([ref],[0],None,[256],[0,256])
    except:
        #print("bad agent")
        return p
    return abs((max(histOrig) - max(histRef)))/255

# instantiate map and robot
M = m.Map("MarioMap.png")
R = r.Robot(M.img, num = (M.xMax//5) + (M.yMax//5))
R.particleScatter(M.xMax, M.yMax)
frame = 0
k = 0

# generate starting position
X, Y = M.randPos(R.sight)
M.drawGrid()
M.drawText("True Pos:" + str(X) + "," + str(Y) + " Frame:" + str(frame))
for p in R.particles:
    if p[2] == "bad particle":
        R.particles.remove(p)
    elif M.inBounds((p[0]), (p[1]), R.sight+10):
        if p[2] > 1:
            p[2] = 1
        M.drawCircle(p[0], p[1], (255,0,255), p[2] * 100, -1)
    else:
        R.particles.remove(p)
        #print("out of bounds particle")
M.drawCircle(X, Y)
frame += 1

# configure window
cv2.namedWindow("Display", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Display", 1000, 1000)
cv2.namedWindow("Sub", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Sub", 500, 500)
cv2.imshow("Display", M.img)
xRef, yRef = M.mapToCV(X, Y)
pqr = R.ref(xRef, yRef)
cv2.imshow("Sub", pqr)
k = cv2.waitKey(0)

# core loop
while k != 27:
    # blank the map
    M.imgReset()

    # movement
    dX, dY = M.randMovVec(X, Y, R.sight, R.speed)
    dXn, dYn = M.addNoise(dX, dY, R.varX, R.varY)
    if not M.inBounds((X+dXn), (Y+dYn), R.sight):
        while not M.inBounds((X+dXn), (Y+dYn), R.sight):
            dX, dY = M.randMovVec(X, Y, R.sight, R.speed)
            dXn, dYn = M.addNoise(dX, dY, R.varX, R.varY)
    X += dXn
    Y += dYn

    # particle filter
    # IMPORTANT: in order to simulate the robot "seeing" its surroundings
    #            I am using its ref() on the real coords from out here.
    #            This way it never "knows" the real coords.
    # xRef, yRef = M.mapToCV(X, Y)
    R.localize(dX, dY, R.ref(X,Y), euclidean)

    # create and store image
    M.drawGrid()
    M.drawText("True Pos:" + str(X) + "," + str(Y) + " Frame:" + str(frame))
    for p in R.particles:
        if p[2] == "bad particle":
            R.particles.remove(p)
        elif M.inBounds((p[0]+dXn), (p[1]+dYn), R.sight+10):
            if p[2] > 1:
                p[2] = 1
            M.drawCircle(p[0], p[1], (255,0,255), p[2] * 100, -1)
        else:
            R.particles.remove(p)
            #print("out of bounds particle")
    M.drawCircle(X, Y)

    # show image
    cv2.imshow("Display", M.img)
    xRef, yRef = M.mapToCV(X, Y)
    pqr = R.ref(xRef, yRef)
    cv2.imshow("Sub", pqr)

    # Enter for next, '" for prev, Esc to close
    # Enter is 13, '" is 39, Esc is 27
    k = 0
    while k != 27 and k != 13:
        k = cv2.waitKey(0)
    if k == 27:
        cv2.destroyAllWindows()
    elif k == 13:
        frame += 1
