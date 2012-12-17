# TID EMC2 group: Multimedia Applications and Terminals
#
# Project to load an image, process it and save it
#
import kivy
kivy.require('1.3.0')
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image 
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.graphics.vertex_instructions import Rectangle
from kivy.core.image import Image, ImageData
from kivy.graphics.texture import Texture
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Line, Fbo
from kivy.graphics.opengl import glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE
import sys
import time
#from kivy.core.gl import glReadBuffer, glReadPixels, GL_RGB, \
#                                GL_UNSIGNED_BYTE, GL_FRONT
#glReadBuffer(GL_FRONT)
#data = glReadPixels(0, 0, win.width, win.height, GL_RGB, GL_UNSIGNED_BYTE)

import pygame

# ----------------------------------------------------
# File selector class
# ----------------------------------------------------
class FilePopup(Popup):
    def __init__(self, **kwargs):
        super(FilePopup, self).__init__(**kwargs)
        #self.myfileselection = 'earth.jpg' #default image 
        self.myfileselection = None #default image 
        self.title = "Load Image"     
       
        View =  FileChooserListView #FileChooserIconView
        
        # create popup layout containing a boxLayout
        content = BoxLayout(orientation='vertical', spacing=5)

        # first, create the scrollView
        self.scrollView = scrollView = ScrollView()
        
        # then, create the fileChooser and integrate it in thebscrollView
        
        if not 'path' in kwargs:
            fileChooser = View(size_hint_y=None)
        else:
            fileChooser = View(kwargs['path'], size_hint_y=None)
        fileChooser.height = 400 # this is a bit ugly...
        scrollView.add_widget(fileChooser)
        self.fileChooser = fileChooser
        
        # construct the content, widget are used as a spacer
        content.add_widget(Widget(size_hint_y=None, height=5))
        content.add_widget(scrollView)
        content.add_widget(Widget(size_hint_y=None, height=5))
        
        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        okbutton = Button(text='Ok')
        okbutton.bind(on_release=self._validate)
        btnlayout.add_widget(okbutton)
        
        cancelbutton = Button(text='Cancel')
        cancelbutton.bind(on_release=self.dismiss)
        btnlayout.add_widget(cancelbutton)
        content.add_widget(btnlayout)
        
        # Add all the stuff to the popup 
        self.content=content
                
    def _validate(self, instance):
        if len(self.fileChooser.selection) > 0:
            self.myfileselection = self.fileChooser.selection[0]
        self.dismiss()


class MainImageWidget(Widget):
    
    def __init__(self):
        Widget.__init__(self)
        self.fbo = None
        self.fbo_pos = None
        self.fbo_size = None
        self.fbo_real_size = None
        self.fbo_scale = None
        
    def _init_fbo(self):
        if self.fbo_pos is None:
            self.fbo_pos = self.pos
            self.fbo_size = self.size
            self.fbo_real_size = self.size
            self.fbo_scale = 1
        with self.canvas:
            #self.fbo = Fbo(size=self.fbo_size)
            self.fbo = Fbo(size=self.fbo_real_size)            
#            Rectangle(size=self.fbo_size, texture=self.fbo.texture, pos=self.fbo_pos)
            Rectangle(size=self.fbo_size, texture=self.fbo.texture, 
                      pos=(self.fbo_pos[0],
                           self.fbo_pos[1]))

             
    def on_touch_down(self, touch):
        if self.fbo is None:
            self._init_fbo()
        #touch position must be corrected with widget postion in order to draw in the fbo
        touch.x -= self.fbo_pos[0]
        touch.x *= self.fbo_scale
        touch.y -= self.fbo_pos[1]
        touch.y *= self.fbo_scale

        with self.fbo:
            Color(1, 1, 0)
            d = 10.
            Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))  
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=10) #in fbo kivy uses gl_line so with is always 1
    
    def on_touch_move(self, touch):
        #touch position must be corrected with widget postion in order to draw in the fbo
        touch.x -= self.fbo_pos[0]
        touch.x *= self.fbo_scale
        touch.y -= self.fbo_pos[1]
        touch.y *= self.fbo_scale
        touch.ud['line'].points += [touch.x, touch.y]
        
    def read_draw_layer(self, raw=True):
        self.fbo.bind()
        #pixels = glReadPixels(self.fbo_pos[0], self.fbo_pos[1], self.fbo.size[0], self.fbo.size[1], GL_RGBA, GL_UNSIGNED_BYTE)
        pixels = glReadPixels(0, 0, self.fbo.size[0], self.fbo.size[1], GL_RGBA, GL_UNSIGNED_BYTE)
        self.fbo.release()
        if not raw:
            #get ints
            pixels = [ord(pixel) for pixel in pixels]        
            #convert to tuple format
            pixels = zip(pixels[0::4], pixels[1::4],pixels[2::4], pixels[3::4])            
        return pixels
                
    def SetImageInWidget(self, image):
        
        if self.fbo is None:
            self._init_fbo()
        #show the image in kivy
        if image.get_bytesize() == 3:
            fmt = 'rgb'
        elif image.get_bytesize() == 4:
            fmt = 'rgba' 
        data = pygame.image.tostring(image, fmt.upper(), True)
        k_im_data = ImageData(image.get_width(), image.get_height(), fmt, data)
        imageTexture = Texture.create_from_data(k_im_data)
        self.canvas.clear()
        
        #Modify size and offset to avoid image distortion
        orig_h = image.get_height()
        orig_w = image.get_width()
        wid_h = self.size[1]
        wid_w = self.size[0]
        print self.size
        s_size = (0,0)
        offset = (0,0)
        orig_ratio = float(orig_w)/orig_h
        wid_ratio = float(wid_w)/wid_h
    
        if wid_ratio > orig_ratio: #fix height
            s_size =  (int(wid_h*orig_ratio), wid_h)
            offset = ((wid_w - s_size[0])/2, 0)
            self.fbo_scale = float(orig_h)/wid_h #scale factor to recover the original image size
        else: #fix width
            s_size =  (wid_w, int(wid_w/orig_ratio))
            offset = (0, (wid_h - s_size[1])/2)
            self.fbo_scale = float(orig_w)/wid_w #scale factor to recover the original image size
    
        self.fbo_pos = (self.pos[0] + offset[0], self.pos[1] + offset[1])
        #self.fbo_pos = (self.pos[0] + offset[0]*self.fbo_scale, self.pos[1] + offset[1]*self.fbo_scale)
        self.fbo_size = s_size
        self.fbo_real_size = (orig_w, orig_h)
   
        #self.canvas.add(Rectangle(texture=imageTexture, pos = self.fbo_pos,
        #                             size=self.fbo_size))
        self._init_fbo() #reload the fbo
        #here we are drawing the sketches directly over the background image
        #TODO: (tomas) I'm not sure why this happens, but scaling the widget does not keep the background
        with self.fbo:
            #Rectangle(texture=imageTexture, pos = (0,0) ,size=self.fbo_size)
            Rectangle(texture=imageTexture, pos = (0,0) ,size=self.fbo_real_size)


 
class DestinationPopup(Popup):
    
    def __init__(self, **kwargs): 
        self.imageToSave = None
        super(DestinationPopup, self).__init__(**kwargs)
        self.title = "Save Image" 
        
        # create popup layout containing a boxLayout
        text_input = TextInput(text='./DestFileName.jpg') 
        self.text_input = text_input
        content = FloatLayout()
        
        text_and_buttons_layout = BoxLayout(orientation='vertical',size_hint=(.6, .3),pos_hint={'x':.2, 'y':.5})
        text_and_buttons_layout.add_widget(text_input)
        text_and_buttons_layout.add_widget(Widget(size_hint_y=None, size_hint=(1, .2)))
        
        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        okbutton = Button(text='Ok')
        okbutton.bind(on_release=self._validate)
        btnlayout.add_widget(okbutton)
        
        cancelbutton = Button(text='Cancel')
        cancelbutton.bind(on_release=self.cancel)
        btnlayout.add_widget(cancelbutton)
        
        text_and_buttons_layout.add_widget(btnlayout)
        
        content.add_widget(text_and_buttons_layout)
        
        self.content = content
        
    def _validate(self, instance):
        #import ipdb; ipdb.set_trace()
        if len(self.text_input.text) > 0:
            self.myfileselection = self.text_input.text
        self.dismiss()
    
    def cancel(self, instance):
        self.myfileselection = None
        self.dismiss()
 
        
# ----------------------------------------------------
# Main app
# ----------------------------------------------------
class PicturesApp(App):

    def build(self):
	
        try:

        
# Callbacks from file name selection
            def OnImageToLoadFileSelected(instance):
                Logger.info('The image we want to load is... <%s>' % instance.myfileselection)
                if instance.myfileselection is not None:
                    im = self.imageToBeDisplayed = pygame.image.load(instance.myfileselection)
                    self.rectangleImage1.SetImageInWidget(im)
                    
            def OnImageToSaveFileSelected(instance):
                Logger.info('The image we want to save is... <%s>' % instance.myfileselection)
                if instance.myfileselection is not None:
                    #we should copy the fbo and scale it to match original image size
                    #get the fbo and do some processing
                    sketch_data = self.rectangleImage1.read_draw_layer()
                    size = self.rectangleImage1.fbo_real_size
                
                    #the image is flipped upside-down (raster scan start row) -> flip = true 
                    sketch_surf = pygame.image.fromstring(sketch_data, size, 'RGBA', True)
                    pygame.image.save(sketch_surf, instance.myfileselection)
                    
                    ##old stuff when we used the widget size for the fbo (instead of the image size)
                    #here we are keeping the fbo source image as reference instead of the original one, but we keep the
                    #original size
                    #sketch_surf = pygame.transform.scale(sketch_surf, (round(size[0]*scale), round(size[1]*scale)) ) 
                    #size = self.rectangleImage1.fbo_size
                    #scale = self.rectangleImage1.fbo_scale
                    #image_to_save = pygame.transform.smoothscale(self.imageToBeDisplayed, (round(size[0]*scale), round(size[1]*scale))) #color average / bilinear
                    #pygame.image.save(image_to_save, instance.myfileselection)
            
# Callback for buttons            
            def OnLoadImageButtonPressed(instance):
                Logger.debug('The load button has been pressed')
                self.fileLoader.open()
            
            def OnSaveImageButtonPressed(instance):
                Logger.debug('The Save button has been pressed')
                if self.imageToBeDisplayed is None:
                    return
                self.fileSaver.open()
                
            def OnProcessImageButtonPressed(instance):
                Logger.debug('The process button has been pressed')
                if self.imageToBeDisplayed is None:
                    return
                #get the fbo and do some processing
                sketch_data = self.rectangleImage1.read_draw_layer()
                size = self.rectangleImage1.fbo_real_size
                #the image is flipped upside-down (raster scan start row) -> flip = true 
                sketch_surf = pygame.image.fromstring(sketch_data, size, 'RGBA', True)
                sketch_pix_arr = pygame.PixelArray(sketch_surf)
                #here we do a very simple image processing in python (very slow)
                for i in xrange(size[0]):
                    for j in xrange(size[1]):
                        color = sketch_pix_arr[i][j]
                        gray = ((color & 0xFF000000)>>24) + ((color & 0x00FF0000)>>16) + ((color & 0x0000FF00)>>8)
                        gray /= 3
                        sketch_pix_arr[i][j]=(gray, gray, gray, 255)
                self.imageToBeDisplayed = sketch_surf  
                self.rectangleImage1.SetImageInWidget(sketch_surf)
                
            # load the image
            mainGrid = GridLayout(rows=2)
            buttonsLayout = BoxLayout(orientation='horizontal',size_hint_y=None, height=100);

            # Variables to be used by callbacks
            self.rectangleImage1 = MainImageWidget()   # where the image is displayed
            self.imageToBeDisplayed = None # the image itself

            # Dialogs to open and save images
            self.fileLoader = FilePopup()
            self.fileLoader.bind(on_dismiss=OnImageToLoadFileSelected)
            self.fileSaver = DestinationPopup()
            self.fileSaver.bind(on_dismiss=OnImageToSaveFileSelected)
                
            # Create buttons
            loadbutton = Button(text='Load image')
            savebutton = Button(text='Save image')
            processbutton = Button(text='Process image\n (convert to grayscale)')
            
            # Add callbacks to buttons
            loadbutton.bind(on_release=OnLoadImageButtonPressed)
            processbutton.bind(on_release=OnProcessImageButtonPressed)
            savebutton.bind(on_release=OnSaveImageButtonPressed)
            
            # Add buttons to buttons container
            buttonsLayout.add_widget(loadbutton);
            buttonsLayout.add_widget(savebutton);
            buttonsLayout.add_widget(processbutton);
            
            # add to the main widget
            mainGrid.add_widget(self.rectangleImage1)
            mainGrid.add_widget(buttonsLayout)
            return mainGrid
           
        except Exception, e:
            Logger.exception('There was an error: %s' % e)

if __name__ in ( '__main__', '__android__'):
    # disable multitouch emulation for mouse (to avoid leaving "traces")
    kivy.config.Config.set ( 'input', 'mouse', 'mouse,disable_multitouch' )
    PicturesApp().run()
