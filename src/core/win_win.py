from pywinauto import Application

def activate(res):
    running_app = Application().connect(process=res[1])
    running_app.top_window().set_focus()
