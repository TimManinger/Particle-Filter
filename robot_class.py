"""
The robot class holds all the information about the robot and its
capabilities. It will get information only from the reference version
of the map. The particles and related processes will also exist
within the robot. The robot does not have access to the actual position
or movement vectors.
"""
import numpy as np
import cv2

class Robot(object):

    # robot initializer, sets all member variables to defaults or passed values
    def __init__(self, map, num, speed = 50, varX = .1, varY = .1, sight = 200):
        self.speed = speed
        self.varX = varX
        self.varY = varY
        self.particles = list()
        self.sight = sight
        self.map = map.copy() # because of course reference is default
        self.num = num

    # get an mxm reference image for a certain point
    # cv2 stores things the opposite way it represents them
    # thanks cv2. I didn't want that hour of my life anyway
    def ref(self, x, y):
        m = self.sight//4
        sX = x - m
        eX = x + m
        subImage = list()
        iY = y - m
        while iY < (y + m):
            try:
                subImage.append(self.map[iY][sX:eX])
                iY += 1
            except:
                #print(iY,sX,eX)
                break
                #return "invalid index"
        subImage = np.array(subImage)
        return subImage

    # scatters initial number of particles within a range
    # rX, rY are in absolute pixels (distance across image)
    # weight == radius of circle
    def particleScatter(self, rX, rY, weight = 1):
        rX -= self.sight
        rY -= self.sight
        pX = 0
        pY = 0
        for p in range(self.num):
            pX = int(np.random.uniform(rX//2, -rY//2, 1))
            pY = int(np.random.uniform(rY//2, -rY//2, 1))
            p = int(np.random.uniform(5, 1, 1))
            self.particles.append([pX, pY, weight])

    def mapToCV(self, x, y):
        x = x + (len(self.map) // 2)
        y = (len(self.map[0]) // 2) - y
        return (int(x), int(y))

    # uses intended motion vector and observations to update particles
    # obs is list of inputs of form [x, y, variance]
    # ref is sub-image of map based on sight range
    # PofZ is a function that returns a probability given two images
    # dX and dY should have no noise applied
    def localize(self, dX, dY, sensor, PofZ):
        for p in self.particles:
            if abs(p[0]) > 1400 or abs(p[1]) > 1400:
                self.particles.remove(p)
        weights = list()
        # sensor update: apply PofZ and inflate/deflate weights
        for p in self.particles:
            refX, refY = self.mapToCV(p[0],p[1])
            p[2] = PofZ(self.ref(refX,refY), sensor, p[2])
            weights.append(p[2])

        # resample
        tWeight = sum(weights)
        relProb = list()
        intervals = list()

        for p in self.particles:
            relProb.append((p[2]/tWeight))
        #print(relProb)

        for i in range(len(relProb)):
            if i > self.num/10:
                intervals.append(sum(relProb[:i+1])+.1)
            else:
                intervals.append(0)
        #print(intervals)

        newParticles = list()
        pset = set()
        for n in range(self.num):
            r = np.random.random_sample()
            for i in range(len(self.particles)):
                if r <= intervals[i]:
                    newParticles.append(self.particles[i])
                    pset.add(str(self.particles[i]))
                    break
        self.particles = newParticles.copy()

        #print(pset)
        # motion update
        #print("particles:", len(self.particles))
        for p in self.particles:
            p[0] += dX
            p[1] += dY
