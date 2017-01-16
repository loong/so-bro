import os
import sys

from select import select
from subprocess import Popen, PIPE

import rpyc

if __name__ == "__main__":
    conn = rpyc.connect("localhost", 18861)
    command = ['python']

    if len(sys.argv) > 1:
        command = ['python'] + sys.argv[1:]

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

                # is stdout
                if fd == p.stderr.fileno():
                        
                    datastr = str(data, 'utf8')
                    if datastr == '>>> ':
                        continue

                    if 'Type "help", "copyright", "credits" or "license" for more information.' in datastr:
                        continue
                
                    # send to local debug service
                    conn.root.add_err(datastr)
