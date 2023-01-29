import pygame
import numpy
import math
pygame.init()

clock = pygame.time.Clock()

scrsize = [1000,1000]
screen = pygame.display.set_mode(scrsize)
pygame.display.set_caption("Drakomatic")
rooms = []
cameraposition = [0,0]
room_color = (105, 43, 49)

def magnitude(vec):
    return math.sqrt(vec[0]**2 + vec[1]**2)

def getedges(center,size):
    halfsize = numpy.divide(size,2)
    topedge = center[1] + halfsize[1]
    rightedge = center[0] + halfsize[0]
    bottomedge = center[1] - halfsize[1]
    leftedge = center[0] - halfsize[0]
    return (rightedge, bottomedge, leftedge, topedge)

def getinsideroom(pos,size):
    inside = False
    closestedge = None
    closestblock = None
    for box in rooms:
        #get if inside any boxes
        boxpos = box.position
        boxhalfsize = numpy.divide(box.size,2) #we use half size to get from center to edge

        if (pos[0] < (boxpos[0] + boxhalfsize[0] - size) and pos[0] > (boxpos[0] - boxhalfsize[0] + size)):
            if (pos[1] < (boxpos[1] + boxhalfsize[1] - size) and pos[1] > (boxpos[1] - boxhalfsize[1] + size)):
                inside = True
    
    #if not inside then find the closest edge
    lastcompared = None
    if not inside:
        for box in rooms:
            edges = getedges(box.position, box.size)
            for num, edge in enumerate(edges):
                compared = abs(edge - pos[num % 2 and 1 or 0])
                if lastcompared == None or compared < lastcompared:
                    lastcompared = compared
                    closestedge = num
                    closestblock = box

    #return edge and block
    return (inside, closestblock, closestedge)

#setup reusable classes
class player:
    def __init__(self, color):
        self.position = [0,0]
        self.color = color
        self.speed = 320
    def update(self, deltatime):
        pressed = pygame.key.get_pressed()
        leftright = (pressed[pygame.K_d] and 1 or 0) - (pressed[pygame.K_a] and 1 or 0)
        updown = (pressed[pygame.K_s] and 1 or 0) - (pressed[pygame.K_w] and 1 or 0)
        movevec = [leftright, updown]
        if magnitude(movevec) > 1:
            movevec = numpy.divide(movevec, magnitude(movevec))
        #collision is amazing
        inroom, nearroom, nearedge = getinsideroom(self.position,12)
        self.position = numpy.add(self.position, numpy.multiply(numpy.multiply(movevec,self.speed), deltatime))
        if not inroom:
            xory = (nearedge % 2 == 0)
            x = (xory and getedges(nearroom.position, nearroom.size)[nearedge] + (nearedge < 1 and -13 or 13) or self.position[0])
            y = (xory and self.position[1] or getedges(nearroom.position, nearroom.size)[nearedge] + (nearedge > 1 and -13 or 13))
            self.position = [x,y]


class projectile:
    def __init__(self, vel, pos, fromplr, damage):
        self.position = pos
        self.velocity = vel
        self.damage = damage
        self.isfromplayer = fromplr

class room: #the name room is for ease of access
    def __init__(self, position, size):
        self.position = position
        self.size = size

#some temp vars
rooms.append(room([0,0], [800,800]))
rooms.append(room([500,0], [400,200]))
plr = player((252, 254, 248))

def lerp(a,b,f):
    return (a * (1-f)) + (b * f)

def lerp2(a,b,f):
    x = lerp(a[0],b[0],f)
    y = lerp(a[1],b[1],f)
    return [x,y]

def convertposition(pos):
    global cameraposition, scrsize
    return numpy.subtract(numpy.add(pos,numpy.divide(scrsize,2)), cameraposition)

def renderall():
    global rooms, plr, screen, room_color
    screen.fill((42, 24, 38))

    #render all rooms (order shouldn't matter because they are all the same color)
    for rom in rooms:
        newrect = pygame.rect.Rect(0,0,rom.size[0],rom.size[1])
        newrect.center = convertposition(rom.position)
        pygame.draw.rect(screen, room_color, newrect)
    
    #render player on top of everything
    pygame.draw.circle(screen, plr.color, convertposition(plr.position),12)


#main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    deltatime = clock.tick(clock.get_fps())/1000

    plr.update(deltatime)

    #update the camera pos towards the player pos
    centeredmousepos = numpy.subtract(pygame.mouse.get_pos(),numpy.divide(scrsize,2))
    cameraposition = lerp2(cameraposition, lerp2(plr.position, numpy.add(centeredmousepos, plr.position),0.2),6 * deltatime)

    renderall()

    pygame.display.flip()

pygame.quit()