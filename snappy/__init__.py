from .storage import snappy_dir, storage_dir
from .snapshot import snapshot_dir, ignore_filename

def snappy_init():
    for path in (snappy_dir(), storage_dir(), snapshot_dir()):
        path.mkdir(exist_ok=True)

    ignore_filename().touch()
