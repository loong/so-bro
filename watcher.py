import os
import sys

from select import select
from subprocess import Popen, PIPE

import rpyc

err = ""
def handleInterpreter(conn, fd, data):
    global err
    
    if fd == p.stderr.fileno():
        datastr = str(data, 'utf8')

        if datastr == '>>> ':
            return
        
        if 'Type "help", "copyright", "credits" or "license" for more information.' in datastr:
            return

        err += datastr

        # errors seem to always end with >>>
        if '>>> ' in datastr:
            conn.root.add_err(err)
            err = ""

def handleScript(conn, fd, data):
    if fd == p.stderr.fileno():
        # send to local debug service
        conn.root.add_err(str(data, 'utf8'))

def handle(conn, fd, data, mode):
    if mode == 'interpreter':
        handleInterpreter(conn, fd, data)
    else:
        handleScript(conn, fd, data)


if __name__ == "__main__":
    conn = rpyc.connect("localhost", 18861)
    command = ['python']
    mode = 'interpreter'

    if len(sys.argv) > 1:
        command = ['python'] + sys.argv[1:]
        mode = 'script'

    with Popen(command, stdout=PIPE, stderr=PIPE) as p:
        readable = {
            p.stdout.fileno(): sys.stdout.buffer,
            p.stderr.fileno(): sys.stderr.buffer,
        }

        while readable:
            for fd in select(readable, [], [])[0]:
                data = os.read(fd, 1024) # read available
                
                if not data: # EOF
                    del readable[fd]
                    continue

                readable[fd].write(data)
                readable[fd].flush()

                handle(conn, fd, data, mode)
