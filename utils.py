
import sys
import signal
from importlib import import_module


_signames = dict((getattr(signal, signame), signame)
                 for signame in dir(signal)
                 if signame.startswith('SIG') and '_' not in signame)


def signal_name(signum):
    try:
        if sys.version_info[:2] >= (3, 5):
            return signal.Signals(signum).name
        else:
            return _signames[signum]

    except KeyError:
        return 'SIG_UNKNOWN'
    except ValueError:
        return 'SIG_UNKNOWN'


def load_object(path):
    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj
    
# 下载IP对应的地理信息(国家, 地区)
def update_geoip_db():
    print('The update in progress, please waite for a while...')
    filename = 'GeoLite2-City.tar.gz'
    local_file = os.path.join(DATA_DIR, filename)
    city_db = os.path.join(DATA_DIR, 'GeoLite2-City.mmdb')
    url = 'http://geolite.maxmind.com/download/geoip/database/%s' % filename

    urllib.request.urlretrieve(url, local_file)

    tmp_dir = tempfile.gettempdir()
    with tarfile.open(name=local_file, mode='r:gz') as tf:
        for tar_info in tf.getmembers():
            if tar_info.name.endswith('.mmdb'):
                tf.extract(tar_info, tmp_dir)
                tmp_path = os.path.join(tmp_dir, tar_info.name)
    shutil.move(tmp_path, city_db)
    os.remove(local_file)

    if os.path.exists(city_db):
        print(
            'The GeoLite2-City DB successfully downloaded and now you '
            'have access to detailed geolocation information of the proxy.'
        )
    else:
        print('Something went wrong, please try again later.')

