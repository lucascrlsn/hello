from punctuator import Punctuator
import datetime
import time

filename = '****************'
PCL = '****************'


def punctuate():
    global filename
    global PCL
    t = open('****************', 'r')
    file = t.read()
    source = file
    # Punctuate
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    print(f'{timestamp} | Punctuating chunk')
    p = Punctuator('****************')
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    print(f'{timestamp} | Saving your file')
    t.write(p.punctuate(source))
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    print(f'{timestamp} | Punctuation complete')


punctuate()

