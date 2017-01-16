import rpyc

class MyService(rpyc.Service):
    def on_connect(self):
        print("Connected!")

    def on_disconnect(self):
        print("DISCONNECTED")

    def add_err(self, obj):
        print(obj)

    def exposed_add_err(self, err):
        self.add_err(err)

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port = 18861)
    t.start()
