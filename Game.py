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
        self.position = numpy.add(self.position, numpy.multiply(numpy.multiply(movevec,self.speed), deltatime))

class room: #the name room is for ease of access
    def __init__(self, position, size):
        self.position = position
        self.size = size

#some temp vars
rooms.append(room([0,0], [800,800]))
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
    cameraposition = lerp2(cameraposition, plr.position,3 * deltatime)

    renderall()

    pygame.display.flip()

# Done! Time to quit.
pygame.quit()