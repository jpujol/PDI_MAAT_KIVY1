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
import math
import random


# The Accent8 paletter from the Brewer qualitative color schemes
Accent8 = [
    [127,201,127],
    [190,174,212],
    [253,192,134],
    [255,255,153],
    [56,108,176],
    [240,2,127],
    [191,91,23],
    [102,102,102] ]


class Vector2D:
    def __init__(self, x, y):
        self.x=float(x)
        self.y=float(y)
    def __add__(self, other):
        return Vector2D(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x-other.x, self.y-other.y)
        
    def __div__(self, other):
        return Vector2D(self.x/other, self.y/other)
        
    def __mul__(self, other):
        return Vector2D(self.x * other, self.y * other)
    
    def __rmul__(self, other):
        return self * other
        
    def __neg__(self):
        return Vector2D(-self.x, -self.y)
        
    def __str__(self):
        return "x:%s, y:%s" % (self.x,self.y)
        
    
    
class Particle:
    def __init__(self, mass, pos, vel):
        self.mass=mass
        self.pos=pos
        self.vel=vel
        self.radius=5

    def __str__(self):
        return "Mass:%s, pos:%s, vel:%s" % (self.mass,str(self.pos), str(self.vel))
    
    
class ParticleSystem(Widget):
    def __init__(self,  **kwargs):
        super(ParticleSystem, self).__init__(**kwargs)
        self.iteration=1
        self.delta_time=0.01;
        self.particleList=[]
        # This will be the radius for the most massive particle in the list
        # All others will be relative to it, depending on their mass ratio
        self.max_radius = 20
        # The flattening applied to particles (considered as ellipsoids)
        self.flattening = 1.0/15.0      # flattening of Jupiter
        # Define the colors we'll user for the particles
        self.colors = Accent8
        for n,c in enumerate(self.colors):
            self.colors[n] = map( lambda x : x/255.0, c )

    def update_particles(self):

       # for particle in self.particleList:
       #     Logger.debug(str(particle))
        
        
        
        # Let's make it as real as possible!
#        G=6.674*0.00000000001
        G=2
        
        numberParticles=len(self.particleList)

        # Nomenclature:
        # Note: ru = unit vector
        # vec(x) = x is a vector
        
        # Compute the one to one force for each particle!
        # We are going to use the fact that vec(Fnm) = - vec(Fmn),
        # so we are going to compute a triangle matrix and then replicate the result
        force2dArray =[[ Vector(0,0) for i in range(numberParticles) ] for j in range(numberParticles)]
        for idx1,particle1 in enumerate(self.particleList):
            for idx2, particle2 in enumerate(self.particleList):
                if (idx1 < idx2): # Compute the force
                     distanceVector = particle2.pos - particle1.pos
                     distanceModule2 = (distanceVector.x*distanceVector.x + distanceVector.y*distanceVector.y)
                     if (distanceModule2 == 0):
                         distanceModule2 = 0.0001
                     
                     distanceUnitVector = distanceVector/math.sqrt(distanceModule2)
                     forceVector = G *( particle1.mass*particle2.mass / distanceModule2) * distanceUnitVector
                     
                     force2dArray[idx1][idx2] = forceVector
                     
                
                elif (idx1 > idx2): # Copy the value from [idx2, idx1] and set the opposite
                     force2dArray[idx1][idx2] = -force2dArray[idx2][idx1]
                
                # if (idx1==idx2) Do nothing
        
        # Compute the total force for each particle
        forceList = []
        for particleIdx in range(numberParticles):
                   
            force = Vector2D(0,0)
            # Add all the elements in force2dArray[idx][0..end-1, except idx].
            # But [idx][idx]= (0,0), so sum all :)
            for forceIdx in range(numberParticles):
                force += force2dArray[particleIdx][forceIdx];
                
            forceList.append(force)  
            
        # Compute accel for each particle: F/m = a
        accelerationList = []
        for idx,particle in enumerate(self.particleList):
            accelerationList.append(forceList[idx]/particle.mass)
        
        
        # Update velocity: a= dv/dt -> v_(n+1) = v_n + a * delta_time
        for idx,particle in enumerate(self.particleList):
            particle.vel += self.delta_time * accelerationList[idx]
        
            
        # Update position: v= ds/dt -> s_(n+1) = s_n + v * delta_time
        for particle in self.particleList:
            particle.pos += self.delta_time * particle.vel

    
    def convert_particle_coordinates_to_screen_coordinates(self, particle):
        # Virtual world coords: -10..10 x -10 .. 10
        screen_coord_x=(self.size[0]-0)/(10-(-10))*(particle.pos.x-(-10))+0
        screen_coord_y=(self.size[1]-0)/(10-(-10))*(particle.pos.y-(-10))+0
        return [screen_coord_x, screen_coord_y]
            
    def draw_particles(self):
        self.canvas.clear()
        with self.canvas:
            for i,particle in enumerate(self.particleList):
                screen_coords=self.convert_particle_coordinates_to_screen_coordinates(particle)
                Color( *self.colors[i%8] )
                Ellipse( pos=(screen_coords[0],screen_coords[1]), 
                         size=(particle.radius,
                               particle.radius*(1-self.flattening)) )
           
        self.canvas.ask_update()
        
        
    
    def update(self, *args):
        
        if (self.iteration % 10 == 0):
            Logger.info('Loop' + str(self.iteration))
     
        self.update_particles()
        self.draw_particles()
            
        # Important update! dont remove
        self.iteration+=1

    def recompute_radii(self):
        # Compute particle density so that the particle with the maximum mass
        # has a radius equal to max_radius
        k = 4.0/3.0*math.pi
        mass_max  = max( [ p.mass for p in self.particleList ] )
        density = mass_max/k/(self.max_radius**3.0)
        # Now update all radii so that they reflect the particle mass
        for p in self.particleList:
            radius = math.pow( p.mass/density/k, 1.0/3.0 )
            p.radius = round( max( [radius,1] ) )

        
    def add_particle(self, mass, pos, vel):
        self.particleList.append(Particle(mass, pos, vel))
        self.recompute_radii()
    #    self.canvas.add(Ellipse(pos=(1,1), size=(3,3)))
        
      


class ParticleSystemApp(App):
    def build(self):
        particlesystem = ParticleSystem()
        
        acum_momentum = Vector2D(0,0)
        
        for x in range(0, 4):
            mass=random.randrange(10, 15)
            pos_mod=random.randrange(30,80)/10.0;
            pos_angle=random.randrange(0,360)/180.0*math.pi
            pos=Vector2D(pos_mod*math.cos(pos_angle),pos_mod*math.sin(pos_angle))
            vel = Vector2D(-pos.y, pos.x);
            vel= 5*vel/math.sqrt(vel.x*vel.x+vel.y*vel.y)
            particlesystem.add_particle(mass, pos, vel);
            acum_momentum += mass*vel;
        
        # Add an extra particle to have momentum zero
        mass=80
        particlesystem.add_particle(mass,Vector2D(0,0),acum_momentum/-mass);
        
        
        #particlesystem.add_particle(1,Vector2D(0,0),Vector2D(1,0));
        #particlesystem.add_particle(1,Vector2D(3,0),Vector2D(0,0));
        #particlesystem.add_particle(-1,Vector2D(0,3),Vector2D(0,0));
        #particlesystem.add_particle(5,Vector2D(5,5),Vector2D(-0.5,0));
        Clock.schedule_interval(particlesystem.update, 1.0/60.0)
        #Clock.schedule_interval(particlesystem.update, 1.0)
        return particlesystem

if __name__ in ('__android__', '__main__'):
    ParticleSystemApp().run()
