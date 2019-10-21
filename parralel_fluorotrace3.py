#!/usr/bin/python3

import threading
import fluorotrace3
import lux


def main():
    f = lux.Flag()
    f.busy()
    shapes = ["semicircle","triangle1","angled","rectangle"]
    threads = []
    for shape in shapes:
        print(dict(shape=shape, num_raypoints=1000,num_radials=200, max_steps=10000, zwalls=(0,0.1), step_size=0.4)
                               )
        t = threading.Thread(target=fluorotrace3.external_run,
                            kwargs=dict(shape=shape,
                                num_raypoints=1000,
                                num_radials=200,
                                max_steps=10000,
                                zwalls=(0,0.1),
                                step_size=0.01
                               )
                            )

        threads.append(t)

    for thd in threads:
        thd.start()

    for thd in threads:
        thd.join()

    f.ready()


if __name__ == "__main__":
    main()
