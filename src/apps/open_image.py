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
from kivy.uix.image import Image 
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.graphics.vertex_instructions import Rectangle
from kivy.core.image import Image, ImageData
from kivy.graphics.texture import Texture

import pygame

# ----------------------------------------------------
# File selector class
# ----------------------------------------------------
class FilePopup(Popup):
    def __init__(self, **kwargs):
        super(FilePopup, self).__init__(**kwargs)
                
       # View =  FileChooserListView #FileChooserIconView
        
        # create popup layout containing a boxLayout
        content = BoxLayout(orientation='vertical', spacing=5)
        #self.popup = popup = Popup(title=self.title,
        #    content=content, size_hint=(None, None), size=(600, 400))
        
        # first, create the scrollView
        #self.scrollView = scrollView = ScrollView()
        
        # then, create the fileChooser and integrate it in thebscrollView
        
        #if not 'path' in kwargs:
        #    fileChooser = View(size_hint_y=None)
        #else:
        #    fileChooser = View(kwargs['path'], size_hint_y=None)
        #fileChooser.height = 400 # this is a bit ugly...
        #scrollView.add_widget(fileChooser)
        #self.fileChooser = fileChooser
        
        # construct the content, widget are used as a spacer
        #content.add_widget(Widget(size_hint_y=None, height=5))
        #content.add_widget(scrollView)
        #content.add_widget(Widget(size_hint_y=None, height=5))
        
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
       
        self.myfileselection='earth.jpg'
        self.dismiss()
        
def SetImageInWidget(image, widget):
    
    #show the image in kivy
    if image.get_bytesize() == 3:
        fmt = 'rgb'
    elif image.get_bytesize() == 4:
        fmt = 'rgba' 
    data = pygame.image.tostring(image, fmt.upper(), True)
    k_im_data = ImageData(image.get_width(), image.get_height(), fmt, data)
    imageTexture = Texture.create_from_data(k_im_data)
    widget.canvas.clear()
    widget.canvas.add(Rectangle(texture=imageTexture, pos=(0, 0), size=(500, 500)))
    
        
# ----------------------------------------------------
# Main app
# ----------------------------------------------------
class PicturesApp(App):

    def build(self):
	
        try:
        
            # load the image
            mainGrid = GridLayout(rows=2)
            buttonsLayout = BoxLayout(orientation='horizontal',size_hint_y=None, height=100);

            # Variables to be used by callbacks
            rectangleImage1 = Widget()   # where the image is displayed
            self.imageToBeDisplayed = None # the image itself

           
            def OnProcessImage(instance):
                Logger.debug('The process button has been pressed')
                if self.imageToBeDisplayed is None:
                    return
                
                im = self.imageToBeDisplayed
                for row in range(0, im.get_height()):
                    for col in range(0, im.get_width()):
                    #TODO: check that for rgb images simply a is None
                        r,g,b,a = im.get_at((col, row))
                        gs = (r + g + b)/3
                        im.set_at((col, row), (gs, gs, gs, a))
                        
                imageToBeDisplayed = im
                SetImageInWidget(im, rectangleImage1)
           
            def OnImageFileSelected(instance):
                Logger.info('The image we want to load is... <%s>' % instance.myfileselection)
                im = self.imageToBeDisplayed = pygame.image.load(instance.myfileselection)
                SetImageInWidget(im, rectangleImage1)
                
            def OnLoadImage(instance):
                Logger.debug('The load button has been pressed')
                fileselector = FilePopup()
                fileselector.bind(on_dismiss=OnImageFileSelected)
                fileselector.open()

                
            # Create buttons
            loadbutton = Button(text='Load image')
            savebutton = Button(text='Save image')
            processbutton = Button(text='Process image\n (convert to grayscale)')
            
            # Add callbacks to buttons
            loadbutton.bind(on_release=OnLoadImage)
            processbutton.bind(on_release=OnProcessImage)
            
            # Add buttons to buttons container
            buttonsLayout.add_widget(loadbutton);
            buttonsLayout.add_widget(savebutton);
            buttonsLayout.add_widget(processbutton);
            
            # add to the main widget
            mainGrid.add_widget(rectangleImage1)
            mainGrid.add_widget(buttonsLayout)
            return mainGrid
           
        except Exception, e:
            Logger.exception('Pictures: Unable to load <%s>' % filename)

if __name__ == '__main__':
    PicturesApp().run()