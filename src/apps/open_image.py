from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics.vertex_instructions import Rectangle
from kivy.graphics.context_instructions import Color
import sys

class FilePopup(Popup):
    def __init__(self, **kwargs):
        super(FilePopup, self).__init__(**kwargs)
        
        #self.parent = parent
        View = FileChooserIconView #FileChooserListView
        # create popup layout containing a boxLayout
        content = BoxLayout(orientation='vertical', spacing=5)
        self.popup = popup = Popup(title=self.title,
            content=content, size_hint=(None, None), size=(600, 400))
        
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
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        
        btn = Button(text='Cancel')
        btn.bind(on_release=popup.dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)
        
        # all done, open the popup !
        #popup.open()

    def _validate(self, instance):
        print self.fileChooser.selection # selected file
        self.popup.dismiss()
#        self.popup = None
#        value = self.fileChooser.path # selection path
#        # if the value was empty, don't change anything.
#        if value == '':
#            # do what you would do if the user didn't select any file
#            return
#
#        # do what you would do if the user selected a file.
#        print 'choosen file: %s' % value
        
        image_file = ''
        if len(self.fileChooser.selection) > 0:
            image_file = self.fileChooser.selection[0]
        change_canvas(self.parent, image_file)


def change_canvas(widget, image_file):
    try:
        widget.canvas.add( Rectangle(source=str(image_file), pos=widget.pos, size=widget.size))
#        with widget.canvas:
#            Rectangle(source=str(image_file), pos=widget.pos, size=widget.size)
        #import ipdb; ipdb.set_trace()
        for elem in widget.children:
            elem.canvas.ask_update() #seems not work
    except Exception,e:
        print "Error: %s" % e

class FileChooserApp(App):

    def build(self):
        parent = Widget()
        parent.canvas.add(Color(1., 1., 0))
        parent.canvas.add( Rectangle(pos=parent.pos, size=parent.size))
        file_pop = FilePopup()     
        parent.add_widget(file_pop)
        
        browse_btn = Button(text=' Choose \n an image \n file', halighn = 'center')
        parent.add_widget(browse_btn)
        
#        parent.canvas.add(Color(1., 0, 0))
#        parent.canvas.add( Rectangle(pos=parent.pos, size=parent.size))
        
        def launch_browser(obj):
            print 'lauch browser is called'
            file_pop.popup.open()
            

        browse_btn.bind(on_release=launch_browser)
    
        return parent

FileChooserApp().run()