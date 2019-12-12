#!/usr/bin/python3

import os
import multiprocessing
import time
import fluorotrace3
import lux
from termcolor import colored



NUM_WORKERS=os.cpu_count()
print(NUM_WORKERS,"workers found".upper(),"\n"+"="*20+"\n"*3)
#SHAPES = ["semicircle","triangle1","angled","rectangle","x"]
SHAPES = ["tmp"+str(i) for i in range(100)]


def welcome():
    ft3 = """      ________                     ______                    _____
     / ____/ /_  ______  _________/_  __/________ _________ |__  /
    / /_  / / / / / __ \/ ___/ __ \/ / / ___/ __ `/ ___/ _ \ /_ < 
   / __/ / / /_/ / /_/ / /  / /_/ / / / /  / /_/ / /__/  __/__/ / 
  /_/   /_/\__,_/\____/_/   \____/_/ /_/   \__,_/\___/\___/____/  """
    print(" "* 30 + colored("Welcome to","blue"))
    print(colored(ft3,"red"))
    print("\n"*2)
    print(" "* 29 + colored("Version 0.10","green"))
    print("\n"*4)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def wait_for_slot(jobs):
    all_alive = True
    while all_alive:
        for job in jobs:
            if not job.is_alive():
                job.handled = True
                all_alive = False
        time.sleep(0.05)
    return [t for t in jobs if not t.handled]


def main():
    welcome()
    f = lux.Flag()
    f.busy()

    if len(SHAPES) > NUM_WORKERS-1:
        print("Too many geometries! Not enough workers.")
        print("Splitting List...")

    jobs = []
    for i, shape in enumerate(SHAPES):
        if i >= NUM_WORKERS-1:
            jobs = wait_for_slot(jobs)
        else:
            pass

        job = multiprocessing.Process(target=fluorotrace3.external_run,
                            kwargs=dict(shape=shape,
                                num_raypoints=1000,
                                num_radials=200,
                                max_steps=10000,
                                zwalls=(0,0.1),
                                step_size=0.01
                               )
                            )
        job.handled = False
        job.start()
        jobs.append(job)

    for job_ in jobs:
        job_.join()

    f.ready()


if __name__ == "__main__":
    main()
