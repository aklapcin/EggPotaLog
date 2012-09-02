import sys
import os
#sys.path.extend(['lib'])


def path_to_local_libs():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'lib')


def pypath():
    """ Setup the environment and python path for django and for dev_appserver.
    """

    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    # Set up the python path using dev_appserver
    if 'django' in sys.modules and sys.modules['django'].VERSION < (1, 4):
        for k in [k for k in sys.modules
            if k.startswith('django.') or k == 'django']:
                del sys.modules[k]

    # django 1.3 at top of path to obscure hobbled version
    lib_path = path_to_local_libs()
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
