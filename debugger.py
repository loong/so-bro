import threading
import time
import getpass
    
import rpyc
import urwid

# TODO global scope variable are evil
screen = None

class Service(rpyc.Service):
    
    def on_connect(self):
        global screen
        if not screen:
            return
        
        screen.addSysMessage("Watcher connected")

    def on_disconnect(self):
        global screen
        if not screen:
            return
        
        screen.addSysMessage("Watcher disconnected")

    def add_err(self, obj):
        global screen
        screen.addSysMessage("Error Detected:")
        screen.addPlainMessage(obj)
        
    def exposed_add_err(self, err):
        self.add_err(err)

class ChatInput(urwid.Edit):
    ''' Custom edit for chat-like input field '''
    _metaclass_ = urwid.signals.MetaSignals  
    signals = ['done']

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'done', self, self.get_edit_text())
            super(ChatInput, self).set_edit_text('')
        elif key == 'esc':
            super(ChatInput, self).set_edit_text('')
        else:
            urwid.Edit.keypress(self, size, key)


class Screen():
    palette = [
        ('sysmsg', 'black', 'light gray', 'standout,underline', 'black,underline', '#88a')
    ]

    listWalker = urwid.SimpleFocusListWalker([])
    loop = None

    def __init__(self, username):
        self.user = username
    
    def run(self):
        listBox = urwid.ListBox(self.listWalker)

        textEdit = ChatInput(self.user + ' > ')
        urwid.connect_signal(textEdit, 'done', self.onSubmit)

        frame = urwid.Frame(
            urwid.AttrWrap(listBox, 'body'),
            header=urwid.BoxAdapter(urwid.ListBox([
                urwid.Text('SO-bro'),
                urwid.Divider('-')
            ]), 2),
            footer=urwid.BoxAdapter(urwid.ListBox([
                urwid.Divider('-'),
                textEdit
            ]), 5)
        )

        self.loop = urwid.MainLoop(urwid.Padding(frame, left=2, right=2), self.palette)
        self.loop.run()
        
    def addUserMessage(self, user, msg):
        self.listWalker.append(urwid.Text(user + ' > ' + msg))
        self.loop.draw_screen()

    def addSysMessage(self, msg):
        self.listWalker.append(urwid.Text(('sysmsg', 'sys > ' + msg)))
        self.loop.draw_screen()

    def addPlainMessage(self, msg):
        self.listWalker.append(urwid.Text(msg))
        self.loop.draw_screen()
        
    def onSubmit(self, widget, text):
        self.addUserMessage(self.user, text)


if __name__ == "__main__":
    global selector
    from rpyc.utils.server import ThreadedServer

    t = ThreadedServer(Service, port = 18861)
    th = threading.Thread(target=t.start)
    th.start()

    global screen
    username = getpass.getuser()
    screen = Screen(username)
    
    screen.run()
