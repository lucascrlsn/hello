""" Used to check if the libraries exist on the OS and are ready for use."""

# https://stackoverflow.com/questions/3131217/error-handling-when-importing-modules

from importlib import import_module

# Youtube Libraries
libnames = ['tkinter', 'datetime', 'time', 'moviepy.editor', 'os', 'pydub', 'speech_recognition', 'json', 're',
            'urllib3', 'urllib.request', 'pytube', 'pprint', 'PIL', 'webview']

for libname in libnames:
    try:
        lib = import_module(libname)
    except:
        sys = sys.exc_info()
        print(sys)
    else:
        globals()[libname] = lib
