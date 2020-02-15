# Adopted from Corey Schafer @ https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/MultiProcessing
# https://www.youtube.com/watch?v=fKl2JW_qrso

import concurrent.futures
import time
import dask

start = time.perf_counter()

if _name_ == '__main__':
    with concurrent.futures.ProcessPoolExecutor() as executor:
        secs = [3, 3, 3, 3, 3]
        results = executor.map(do_something, secs)


def do_something(seconds):
    print(f'Sleeping {seconds} second(s)...')
    time.sleep(seconds)
    return f'Done Sleeping...{seconds}'



    #
    # for result in results:
    #     print(result)

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')