#!/bin/env -S python
import os
import subprocess
import sys

"""
os.environ["parent_pid"]=str(os.getpid())

do_continue = True
def restart(signum, frame):
    os.kill(pop.pid, signal.SIGTERM)
    os.kill(pop.pid, signal.SIGTERM)

def stop(signum, frame):
    global do_continue
    do_continue=False
    os.kill(pop.pid, signal.SIGTERM)
    os.kill(pop.pid, signal.SIGTERM)


signal.signal(signal.SIGUSR1, restart)
signal.signal(signal.SIGUSR2, stop)
while do_continue:
    pop = subprocess.call(["/bin/env", "python3", "manage.py", "runserver"],
                          stderr=sys.stderr, stdin=sys.stdin, stdout=sys.stdout)
    pop.wait()"""

from manage import main
first = True

class A:

    def __init__(self):
        print(self.__class__.__name__)

    @classmethod
    def instanciate(cls):
        return cls()


class B(A):

    pass


if __name__=="__main__":
    #subprocess.call(["/bin/env",  "python3", "manage.py", "runserver", *sys.argv[1:]])
    print(A.instanciate())
    print(B.instanciate())





