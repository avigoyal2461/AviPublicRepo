import asyncio
import time 
#This does NOT run concurrently.

import threading

class basic_async():
    def __init__(self):
        self.var = None

    async def hello_world(self):
        print('Hello ...')
        await self.something()
        print('... World!')

    async def bye_program(self):
        print("Goodbye")
        # await asyncio.sleep(1)
        print("moonman")

    async def something(self):
        time.sleep(10)
        print("something")

class inter_async():
    def __init__(self):
        self.var = None

    async def run(self):
        a = basic_async()
        await a.hello_world()
        await a.bye_program()
        # asyncio.create_task(a.hello_world())
        # asyncio.create_task(a.bye_program())
        # await asyncio.run(a.hello_world())
        # await asyncio.run(a.bye_program())

#this does work concurrently.
class python_threading():
    #the server being called is hosted in : pythoncode/FlaskPage2.py
    #the server is running through threading methods, and seems to take all requests

    import requests
    def threading_test(self, thread, input, some_thread=None):
            """
            Testing how Threading works with python
            """

            print(some_thread)
            if some_thread:
                some_thread.start()
            sleep_time = [5,3,1]
            print(f"Starting Thread : {thread}")
            resp = requests.get(f'http://192.168.0.221:105/boxGet/{sleep_time[input]}')
            # if thread == 1:
            #     self.random(thread, input, sleep_time[input])
            # else:
            #     time.sleep(sleep_time[input])
            print(f"Finished Thread {thread}, {resp.json()}")


    def random(self, thread, input, sleep_time):
        time.sleep(sleep_time)
        thread4 = threading.Thread(target=self.new_thread)
        thread4.start()
        print(f"testing a new method.. {thread * input}")

    def new_thread(self):
        time.sleep(2)
        print("started thread in a thread")

if __name__ == "__main__":
    import requests

    # a = basic_async()
    # a = inter_async()
    # asyncio.run(a.run())
    a = python_threading()
    # resp = requests.get('http://192.168.0.221:105/boxGet')
    # print(resp)
    # print(resp.json())
    thread1 = threading.Thread(target=a.threading_test, args=(1, 0))
    thread2 = threading.Thread(target=a.threading_test, args=(2, 1))
    thread3 = threading.Thread(target=a.threading_test, args=(3, 2))

    thread1.start()
    thread2.start()
    thread3.start()


    # a.run()
    # asyncio.run(a.hello_world())
    # asyncio.run(a.bye_program())