import pygame
import numpy
import math
from random import *
pygame.init()

clock = pygame.time.Clock()

scrsize = [1600,900]
screen = pygame.display.set_mode(scrsize)
pygame.display.set_caption("Drakomatic")
rooms = []
cameraposition = [0,0]
room_color = (105, 43, 49)
allprojs = []
allenims = []
boxsizes = (400,800)



def magnitude(vec):
    return math.sqrt(abs(vec[0]**2 + vec[1]**2))

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
class weapon:
    def __init__(self, firerate, projectiles, bulletspeed, playerowned, damage):
        self.firerate = firerate
        self.projectilecount = projectiles
        self.bulletspeed = bulletspeed
        self.nextfiretick = 0
        self.playerowned = playerowned
        self.damage = damage
    def update(self, deltatime):
        global clock, allprojs, plr, scrsize
        mbuttons = pygame.mouse.get_pressed(3)
        if mbuttons[0] and self.nextfiretick <= (pygame.time.get_ticks()/1000):
            self.nextfiretick = (pygame.time.get_ticks()/1000) + (60/self.firerate)
            mousetoplayer = numpy.subtract(pygame.mouse.get_pos(),numpy.divide(scrsize,2))
            computespeed = numpy.multiply(numpy.divide(mousetoplayer,magnitude(mousetoplayer)),self.bulletspeed)
            allprojs.append(projectile(computespeed, plr.position, self.playerowned, self.damage))

class player:
    def __init__(self, color, weapon):
        self.position = [0,0]
        self.color = color
        self.speed = 320
        self.wep = weapon
    def update(self, deltatime):
        pressed = pygame.key.get_pressed()
        leftright = (pressed[pygame.K_d] and 1 or 0) - (pressed[pygame.K_a] and 1 or 0)
        updown = (pressed[pygame.K_s] and 1 or 0) - (pressed[pygame.K_w] and 1 or 0)
        movevec = [leftright, updown]
        if magnitude(movevec) > 1:
            movevec = numpy.divide(movevec, magnitude(movevec))
        self.wep.update(deltatime)
        #collision is amazing
        inroom, nearroom, nearedge = getinsideroom(self.position,12)
        self.position = numpy.add(self.position, numpy.multiply(numpy.multiply(movevec,self.speed), deltatime))
        if not inroom:
            xory = (nearedge % 2 == 0)
            x = (xory and getedges(nearroom.position, nearroom.size)[nearedge] + (nearedge < 1 and -12.1 or 12.1) or self.position[0])
            y = (xory and self.position[1] or getedges(nearroom.position, nearroom.size)[nearedge] + (nearedge > 1 and -12.1 or 12.1))
            self.position = [x,y]


class projectile:
    def __init__(self, vel, pos, fromplr, damage):
        self.position = pos
        self.velocity = vel
        self.damage = damage
        self.isfromplayer = fromplr
    def update(self, deltatime):
        self.position = numpy.add(self.position, numpy.multiply(self.velocity, deltatime))

class enemy():
    def __init__(self, position, speed, aitype, health, weapon):
        self.position = position
        self.speed = speed
        self.type = aitype
        self.health = health
        self.weapon = weapon
        self.radius = 18
    def update(self,deltatime):
        #check if bullet is collided
        global allprojs
        for i, bull in enumerate(allprojs):
            if magnitude(numpy.subtract(bull.position, self.position)) <= self.radius:
                self.health -= bull.damage
                allprojs.pop(i)


class room: #the name room is for ease of access
    def __init__(self, position, size):
        self.position = position
        self.size = size

#some temp vars
initroom = rooms.append(room([0,0], [randint(boxsizes[0], boxsizes[1]),randint(boxsizes[0], boxsizes[1])]))
plr = player((252, 254, 248),weapon(600,1,600,True,4))

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
    global rooms, plr, screen, room_color, allprojs, allenims
    screen.fill((42, 24, 38))

    #render all rooms (order shouldn't matter because they are all the same color)
    for rom in rooms:
        newrect = pygame.rect.Rect(0,0,rom.size[0],rom.size[1])
        newrect.center = convertposition(rom.position)
        pygame.draw.rect(screen, room_color, newrect)
    
    for bullet in allprojs:
        pygame.draw.circle(screen, (255,188,22), convertposition(bullet.position),4)

    for enem in allenims:
        pygame.draw.circle(screen, (255,0,0), convertposition(enem.position),enem.radius)

    #render player on top of everything
    pygame.draw.circle(screen, plr.color, convertposition(plr.position),12)

for i in range(randint(5,20)):
    prevroom = rooms[len(rooms)-1]
    updown = randint(0,20) % 2 == 0
    xsize = len(rooms) % 2 == 0 and randint(boxsizes[0], boxsizes[1]) or (updown and 200 or 300)
    ysize = len(rooms) % 2 == 0 and randint(boxsizes[0], boxsizes[1]) or (not updown and 200 or 300)
    ypos = (updown and prevroom.position[1] + prevroom.size[1]/2 + ysize/2 - 100 or prevroom.position[1])
    xpos = (not updown and prevroom.position[0] + prevroom.size[0]/2 + xsize/2 - 100 or prevroom.position[0])
    if updown:
        for i in range(randint(2,5)):
            allenims.append(enemy([randint(int(xsize/-2),int(xsize/2)) + xpos,randint(int(ysize/-2),int(ysize/2)) + ypos],120,None,20,weapon(120,1,300,False,12)))

    newroom = room([xpos, ypos], [xsize, ysize])
    rooms.append(newroom)

#main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    deltatime = clock.tick(clock.get_fps())/1000

    plr.update(deltatime)
    for i, pro in enumerate(allprojs):
        pro.update(deltatime)
        isin, nearroom, nearedge = getinsideroom(pro.position,4)
        if not isin:
            allprojs.pop(i)

    for i, enem in enumerate(allenims):
        enem.update(deltatime)
        if enem.health <= 0:
            allenims.pop(i)


    #update the camera pos towards the player pos
    centeredmousepos = numpy.subtract(pygame.mouse.get_pos(),numpy.divide(scrsize,2))
    cameraposition = lerp2(cameraposition, lerp2(plr.position, numpy.add(centeredmousepos, plr.position),0.2),6 * deltatime)

    renderall()

    pygame.display.flip()

pygame.quit()
