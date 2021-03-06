import collections
import contextlib
import os
import platform
with contextlib.suppress(ImportError):
    import psutil
cpu_count = collections.namedtuple('cpu_count', 'phy_core v_core')


class OS:

    @staticmethod
    def is_linux():
        platform_name = OS.uname()[0]
        return 'linux' in platform_name.lower()

    @staticmethod
    def is_windows():
        platform_name = OS.uname()[0]
        return 'windows' in platform_name.lower()

    @staticmethod
    def uname():
        return platform.uname()

    @staticmethod
    def release():
        return platform.release()


class CPU:

    @staticmethod
    def count():
        return cpu_count(psutil.cpu_count(logical=False),
                         psutil.cpu_count(logical=True))

    @staticmethod
    def freq():
        """
        Return like:
            scpufreq(current=1801.0, min=0.0, max=1801.0)
        """
        return psutil.cpu_freq()


class Memory:

    @staticmethod
    def virtual():
        """
        Return like:
            vmem(total=17057947648, available=8627826688,
                percent=49.4, used=8430120960, free=8627826688
        """
        return psutil.virtual_memory()

    @staticmethod
    def swap():
        return psutil.swap_memory()


class Disk:

    @staticmethod
    def partitions():
        return psutil.disk_partitions()

    @staticmethod
    def io_counters():
        return psutil.disk_io_counters()

    @staticmethod
    def usage(path):
        return psutil.disk_usage(path)


class Net:

    @staticmethod
    def if_addrs():
        return psutil.net_if_addrs()

    @staticmethod
    def if_stats():
        return psutil.net_if_stats()()

    @staticmethod
    def io_counters(pernic=False):
        return psutil.net_io_counters(pernic=pernic)


def get_pip_path():
    pip_paths = ['pip', 'pip.ini'] if OS.is_windows() else ['.pip', 'pip.conf']
    return os.path.join(os.path.expanduser('~'), *pip_paths)
