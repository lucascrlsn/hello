import concurrent.futures
import time
import speedtest
from colorama import Fore, Style, init
init()

start = time.perf_counter()
session_count = 0
session_limit = 2
last_test = int()
download_capacity = int()


def check_speed(seconds):
    # Checks Upload/Download Speeds
    global download_capacity
    global session_count
    global last_test
    if session_count == 0:
        print('No previous sessions detected, measuring download speed...')
        speedtester = speedtest.Speedtest()
        speedtester.get_best_server()
        speedtester.upload(pre_allocate=False)
        download_bytes = round(speedtester.download(), 2)
        download_capacity = round(download_bytes / 1048576, 2)
        last_test = round(download_bytes / 1048576, 2)
        print(Fore.RED + f'Download speed: {download_capacity}MB per second' + Style.RESET_ALL)
        session_count = session_count + 1
        print(f'Sleeping {seconds} second(s)...')
        time.sleep(seconds)
    else:
        print('Initiating...')
        speedtester = speedtest.Speedtest()
        speedtester.get_best_server()
        speedtester.upload(pre_allocate=False)
        download_bytes = round(speedtester.download(), 2)
        download_capacity = int(download_bytes / 1048576)
        download_capacity = round(download_capacity, 2)
        difference = round(abs(download_capacity-last_test), 2)
        print(Fore.RED + f'Download speed: {download_capacity}MB per second, this is a difference of {difference}MB per second' + Style.RESET_ALL)
        last_test = round(download_capacity, 2)
        session_count = session_count + 1
        print(f'Sleeping {seconds} second(s)...')
        time.sleep(seconds)


def run_thread():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Live Version will be set to 120 seconds
        f1 = executor.submit(check_speed, 10)
        print(f1.result())
        global session_limit
        if session_count < session_limit:
            run_thread()
        else:
            end_session()
        # prompt = input('Would you like to check the speed again (y/n): ')
        # if prompt == 'y':
        #     run_thread()
        # else:
        #     end_session()


def end_session():
    # Completely ends the program, user will not be passed to additional checks in the active session
    url = 'https://github.com/lucascrlsn'
    print(f'You have met the session limit count! Please follow me on Github: {url}')
    print('Have a good day!')
    print(f'Finished in {round(finish - start, 2)} second(s)')


finish = time.perf_counter()
run_thread()

