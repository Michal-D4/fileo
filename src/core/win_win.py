def activate(res):
    from pywinauto import Application
    running_app = Application().connect(process=res[1])
    running_app.top_window().set_focus()
