from gtkmvc.view import View

class MainView (View):

    def __init__ (self):
        super(MainView, self).__init__(builder='gui.glade')
        return
