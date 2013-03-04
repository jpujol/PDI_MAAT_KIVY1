import kivy
kivy.require('1.1.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.graphics import Color, Ellipse
import copy
import math
import random


# The Accent8 paletter from the Brewer qualitative color schemes
Accent8 = [
    [56, 108, 176],
    [253, 192, 134],
    [127, 201, 127],
    [190, 174, 212],
    [255, 255, 153],
    [240, 2, 127],
    [191, 91, 23],
    [102, 102, 102] ]


class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __div__(self, other):
        return Vector2D(self.x / other, self.y / other)

    def __mul__(self, other):
        return Vector2D(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __str__(self):
        return "x:%s, y:%s" % (self.x, self.y)



class Particle:
    def __init__(self, mass, pos, vel):
        self.mass = mass
        self.pos = pos
        self.posNext = pos
        self.vel = vel
        self.density = 1
        #self.radius = math.pow(3*mass/(4*math.pi*self.density),1.0/3.0)
        self.radius = 0.5

    def __str__(self):
        return "Mass:%s, pos:%s, vel:%s, radius:%s, next pos:%s" % (self.mass, str(self.pos), str(self.vel), str(self.radius), str(self.posNext))


class ParticleSystem(Widget):
    def __init__(self, **kwargs):
        super(ParticleSystem, self).__init__(**kwargs)
        self.iteration = 1
        self.delta_time = 0.01;
        self.particleList = []
        self.particle_viewport = [-10.0, 10.0, -10.0, 10.0]; # xmin, xmax, ymin, ymax

                
        # Define the colors we'll user for the particles
        self.pause = False
        self.touch_center = None
        self.old_d = None
        self.colors = Accent8
        for n, c in enumerate(self.colors):
            self.colors[n] = map(lambda x : x / 255.0, c)

    # Collision test for spheres
    # At^2 + B + C' < (r1 + r2)^2
    # At^2 + Bt + C < 0  -> if t = [0,1], then COLLISION
    # C = C' - (r1 + r2)^2
    #
    # C' = (x20 - x10)^2 + (y20 - y10)^2
    # B = 2(x20-x10)(-x20+x21+x10-x11) + 2(y20-y10)(-y20+y21+y10-y11)
    # A = (-x20+x21+x10-x11)^2+(-y20+y21+y10-y11)^2
    # particle.pos = x?0
    # particle.posNext = x?1
    def test_collision(self, particle1, particle2):
       # Logger.debug('particle 1' + str(particle1));
       # Logger.debug('particle 2' + str(particle2));
        Logger.debug("particle1 x=%.3f, xNext=%.3f, radius=%.3f", particle1.pos.x, particle1.posNext.x, particle1.radius)
        Logger.debug("particle2 x=%.3f, xNext=%.3f, radius=%.3f", particle2.pos.x, particle2.posNext.x, particle2.radius)
        Cp = math.pow(particle2.pos.x - particle1.pos.x,2) + math.pow(particle2.pos.y - particle1.pos.y,2);
        B = 2 * (particle2.pos.x - particle1.pos.x)*(-particle2.pos.x+particle2.posNext.x+particle1.pos.x-particle1.posNext.x)\
          + 2 * (particle2.pos.y - particle1.pos.y)*(-particle2.pos.y+particle2.posNext.y+particle1.pos.y-particle1.posNext.y)
        A = math.pow(-particle2.pos.x+particle2.posNext.x+particle1.pos.x-particle1.posNext.x,2) +\
            math.pow(-particle2.pos.y+particle2.posNext.y-particle1.pos.y-particle1.posNext.y,2)
        C = Cp-math.pow(particle1.radius + particle2.radius,2)
        discriminant = B*B-4*A*C
        if (discriminant < 0):
            Logger.debug("Discriminant is negative. No solution and thus, no collision")
            return False
        if (A == 0):
            Logger.debug("Second grade coef is zero")
            Logger.debug("B should be zero, too. B= %.3f", B)
            if (C < 0):
                Logger.debug("Collision")
                return True
            else:
                return False
                
        root1 = (-B + math.sqrt(discriminant))/(2*A)
        root2 = (-B - math.sqrt(discriminant))/(2*A)
        
		# Order root solution: root1 < root2
        if (root1>root2):
            rootTemp = root2
            root2=root1
            root1=rootTemp
            

        	
        Logger.debug("A=%.3f, B=%.3f, C=%.3fs, root1=%.3f, root2=%.3f ", A, B, C, root1, root2)
        # Condition: x E [0,1] && ( ((x>R1) && (x<R2)) || (x<R1) && (x>R2)
		# The second case cannot happen, so the prior condition becomes
        # x E [0,1] && ((x>R1) && (x<R2))
        if ((0 < root1 and 1 > root2) or
            (0 > root1  and 1 < root2) or
            (root1 < 1 < root2) or
            (root1 < 0 < root2)):
            Logger.debug("Collision")
            return True
        else:
            return False
           
		
        return False        
    
    def update_particles(self):

       # for particle in self.particleList:
       #     Logger.debug(str(particle))



        # Let's make it as real as possible!
#        G=6.674*0.00000000001
        G = 2

        numberParticles = len(self.particleList)

        # Nomenclature:
        # Note: ru = unit vector
        # vec(x) = x is a vector

        # Compute the one to one force for each particle!
        # We are going to use the fact that vec(Fnm) = - vec(Fmn),
        # so we are going to compute a triangle matrix and then replicate the result
        force2dArray = [[ Vector(0, 0) for i in range(numberParticles) ] for j in range(numberParticles)]
        for idx1, particle1 in enumerate(self.particleList):
            for idx2, particle2 in enumerate(self.particleList):
                if (idx1 < idx2):  # Compute the force
                     distanceVector = particle2.pos - particle1.pos
                     distanceModule2 = (distanceVector.x * distanceVector.x + distanceVector.y * distanceVector.y)
                     if (distanceModule2 == 0):
                         distanceModule2 = 0.0001

                     distanceUnitVector = distanceVector / math.sqrt(distanceModule2)
                     forceVector = G * (particle1.mass * particle2.mass / distanceModule2) * distanceUnitVector

                     force2dArray[idx1][idx2] = forceVector


                elif (idx1 > idx2):  # Copy the value from [idx2, idx1] and set the opposite
                     force2dArray[idx1][idx2] = -force2dArray[idx2][idx1]

                # if (idx1==idx2) Do nothing

        # Compute the total force for each particle
        forceList = []
        for particleIdx in range(numberParticles):

            force = Vector2D(0, 0)
            # Add all the elements in force2dArray[idx][0..end-1, except idx].
            # But [idx][idx]= (0,0), so sum all :)
            for forceIdx in range(numberParticles):
                force += force2dArray[particleIdx][forceIdx];

            forceList.append(force)

        # Compute accel for each particle: F/m = a
        accelerationList = []
        for idx, particle in enumerate(self.particleList):
            accelerationList.append(forceList[idx] / particle.mass)


        # Update velocity: a= dv/dt -> v_(n+1) = v_n + a * delta_time
        for idx, particle in enumerate(self.particleList):
            particle.vel += self.delta_time * accelerationList[idx]
        

        # Compute possible update for position: dont do it directly, because we have
        # need to test the collition first        
        for particle in self.particleList:
            particle.posNext = particle.pos + self.delta_time * particle.vel

        # COLLITION TEST
        # For circles
        #
        for idx1, particle1 in enumerate(self.particleList):
            for idx2, particle2 in enumerate(self.particleList):
                if (idx1 < idx2):  # Do the test  
                    self.test_collision(particle1, particle2)
                 
        
        
        # DEBUG: DO THIS AFTER PAINTING
        # Update position: v= ds/dt -> s_(n+1) = s_n + v * delta_time
       # for particle in self.particleList:
       #     particle.pos = particle.posNext

    def convert_x_particle_coordinates_to_screen_coordinates(self, x):
        screen_coord_x = float(self.size[0]) * (x - self.particle_viewport[0]) / (self.particle_viewport[1] - self.particle_viewport[0]) 
        return screen_coord_x

    def convert_y_particle_coordinates_to_screen_coordinates(self, y):
        screen_coord_y = float(self.size[1]) * (y - self.particle_viewport[2]) / (self.particle_viewport[3] - self.particle_viewport[2]) 
        return screen_coord_y
			
	
    def convert_particle_coordinates_to_screen_coordinates(self, particle):
        # Virtual world coords: in particle_viewport
        screen_coord_x = self.convert_x_particle_coordinates_to_screen_coordinates(particle.pos.x)
        screen_coord_y = self.convert_y_particle_coordinates_to_screen_coordinates(particle.pos.y)
        screen_zero_x =  self.convert_x_particle_coordinates_to_screen_coordinates(0)
        screen_radius_x =  self.convert_x_particle_coordinates_to_screen_coordinates(particle.radius)
        screen_zero_y =  self.convert_y_particle_coordinates_to_screen_coordinates(0)
        screen_radius_y =  self.convert_y_particle_coordinates_to_screen_coordinates(particle.radius)
        
        return [screen_coord_x, screen_coord_y, screen_radius_x-screen_zero_x, screen_radius_y - screen_zero_y]

    def draw_particles(self):
        self.canvas.clear()
        with self.canvas:
		    # Draw axis
            for i in range(int(self.particle_viewport[0]),int(self.particle_viewport[1])):
                screen_coord_x = self.convert_x_particle_coordinates_to_screen_coordinates(i)
                screen_coord_y = self.convert_y_particle_coordinates_to_screen_coordinates(0)
                Color(*[255,0,0])
                Ellipse(pos=(screen_coord_x, screen_coord_y), size=(2, 2))
            for i in range(int(self.particle_viewport[2]),int(self.particle_viewport[3])):
                screen_coord_x = self.convert_x_particle_coordinates_to_screen_coordinates(0)
                screen_coord_y = self.convert_y_particle_coordinates_to_screen_coordinates(i)
                Color(*[0,255,0])
                Ellipse(pos=(screen_coord_x, screen_coord_y), size=(2, 2))
		
		    # Draw particles
            for i, particle in enumerate(self.particleList):
                screen_coords = self.convert_particle_coordinates_to_screen_coordinates(particle)
                Color(*self.colors[i % 8])
                Ellipse(pos=(screen_coords[0]-screen_coords[2], screen_coords[1]-screen_coords[3]), size=(2*screen_coords[2], 2*screen_coords[3]))
       
        self.canvas.ask_update()



    def update(self, *args):

        if self.pause:
            return

        if (self.iteration % 10 == 0):
            Logger.info('Loop' + str(self.iteration))

        self.update_particles()
        self.draw_particles()
		
		# Temp code! this comes from the update_particles funcion. Here so we can draw the temporal state
		# to debug the collision detection
		# Update position: v= ds/dt -> s_(n+1) = s_n + v * delta_time
        for particle in self.particleList:
            particle.pos = particle.posNext

        # Important update! dont remove
        self.iteration += 1


          


    def add_particle(self, mass, pos, vel):
        self.particleList.append(Particle(mass, pos, vel))

    

class ParticleSystemApp(App):
    def build(self):
        particlesystem = ParticleSystem()

        particlesystem.add_particle(5,Vector2D(-5,0),Vector2D(190,0));
        particlesystem.add_particle(5,Vector2D(5,0),Vector2D(-190,0));
        
        #Clock.schedule_interval(particlesystem.update, 1.0 / 60.0)
        Clock.schedule_interval(particlesystem.update, 5.0)
        return particlesystem


if __name__ in ('__android__', '__main__'):
    ParticleSystemApp().run()
