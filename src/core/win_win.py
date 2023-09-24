def activate(pid):
    from pywinauto import Application

    running_app = Application().connect(process=int(pid))
    running_app.top_window().set_focus()
