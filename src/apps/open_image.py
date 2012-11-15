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
    
    #Modify size and offset to avoid image distortion
    orig_h = image.get_height()
    orig_w = image.get_width()
    wid_h = widget.size[1]
    wid_w = widget.size[0]
    s_size = (0,0)
    offset = (0,0)
    orig_ratio = float(orig_w)/orig_h
    wid_ratio = float(wid_w)/wid_h

    if wid_ratio > orig_ratio: #fix height
        s_size =  (wid_h*orig_ratio, wid_h)
        offset = ((wid_w - s_size[0])/2, 0)
    else: #fix width
        s_size =  (wid_w, wid_w/orig_ratio)
        offset = (0, (wid_h - s_size[1])/2)

    widget.canvas.add(Rectangle(texture=imageTexture, pos = (widget.pos[0] + offset[0],widget.pos[1]+offset[1]),
                                 size=s_size))

 
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
                    SetImageInWidget(im, rectangleImage1)
                    
            def OnImageToSaveFileSelected(instance):
                Logger.info('The image we want to save is... <%s>' % instance.myfileselection)
                if instance.myfileselection is not None:
                    pygame.image.save(self.imageToBeDisplayed, instance.myfileselection)
            
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
                
                im = self.imageToBeDisplayed
                for row in range(0, im.get_height()):
                    for col in range(0, im.get_width()):
                    #TODO: check that for rgb images simply a is None
                        r,g,b,a = im.get_at((col, row))
                        gs = (r + g + b)/3
                        im.set_at((col, row), (gs, gs, gs, a))
                        
                imageToBeDisplayed = im
                SetImageInWidget(im, rectangleImage1)
        
            # load the image
            mainGrid = GridLayout(rows=2)
            buttonsLayout = BoxLayout(orientation='horizontal',size_hint_y=None, height=100);

            # Variables to be used by callbacks
            rectangleImage1 = Widget()   # where the image is displayed
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
            mainGrid.add_widget(rectangleImage1)
            mainGrid.add_widget(buttonsLayout)
            return mainGrid
           
        except Exception, e:
            Logger.exception('There was an error: %s' % e)

if __name__ == '__main__':
    PicturesApp().run()