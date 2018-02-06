import os
import stat
import json
import shutil

from pathlib import Path

from .storage import add_file, snappy_dir, get_string_hash, get_object_path
from .ignore import IgnoreList

SNAPSHOTS = "snapshots"
IGNORE = "ignore"

def snapshot_dir():
    path = snappy_dir() / "snapshots"

    return path

def split_path(path):
    parts = path.parts

    return parts[0], Path(*parts[1:])

class NoSuchFile(Exception):
    pass

class Directory(object):
    def __init__(self):
        self.children = {}

    def get_child(self, name):
        try:
            return self.children[name]
        except KeyError:
            raise NoSuchFile()

    def add_child(self, name, child):
        self.children[name] = child

    def lookup(self, path):
        name, rest = split_path(path)

        return self.get_child(name).lookup(rest)

    def add_file(self, path, file_):
        name, rest = split_path(path)

        if rest != Path():
            if not name in self.children:
                self.add_child(name, Directory())

            child = self.get_child(name)
            child.add_file(rest, file_)
        else:
            self.add_child(name, file_)

    def __str__(self):
        s = ""
        indent = 2

        for name, item in self.children.items():
            s += "{}\n".format(name)

            if isinstance(item, Directory):
                for line in str(item).splitlines():
                    s += " "*indent + line + "\n"

        return s

    def leaves(self):
        for child in self.children.values():
            if isinstance(child, File):
                yield child
            else:
                yield from child.leaves()

    @classmethod
    def from_dict(cls, d):
        directory = cls()

        for key, item in d.items():
            if isinstance(item, dict):
                child = cls.from_dict(item)
            else:
                st_mtime, file_hash = item

                child = File(st_mtime, file_hash)

            directory.add_child(key, child)

        return directory

    def as_dict(self):
        d = {}

        for key, item in self.children.items():
            if isinstance(item, Directory):
                d[key] = item.as_dict()
            else:
                d[key] = (item.st_mtime, item.file_hash)

        return d

    def save(self):
        dump = json.dumps(self.as_dict(), sort_keys=True)

        snapshot_hash = get_string_hash(dump.encode("utf-8"))

        with open(snapshot_dir() / snapshot_hash, "w") as fd:
            fd.write(dump)

        return snapshot_hash

    @classmethod
    def load(cls, path):
        with open(path) as fd:
            d = json.load(fd)

        return cls.from_dict(d)

    def link(self, path):
        path.mkdir()

        for name, item in self.children.items():
            item.link(path / name)

    def checkout(self, dst=None, unlink=True):
        if not dst:
            dst = Path.cwd()

        dst.mkdir(exist_ok=True)

        if unlink:
            for path, _ in changes(self):
                path.unlink()

        for name, item in self.children.items():
            item.checkout(dst / name, False)

class File(object):
    def __init__(self, st_mtime, file_hash):
        self.st_mtime = st_mtime
        self.file_hash = file_hash

    def lookup(self, path):
        if len(path.parts) > 0:
            raise NoSuchFile
        else:
            return self

    def link(self, path):
        obj_path = get_object_path(self.file_hash).resolve()

        path.symlink_to(obj_path)

    def remove_object(self):
        remove_object(self.file_hash)

    def checkout(self, dst, unlink=None):
        shutil.copy2(get_object_path(self.file_hash),
                     dst)

def ignore_filename():
    return snappy_dir() / IGNORE

def walk(path):
    ignore = IgnoreList(ignore_filename())
    ignore.add_pattern(str(snappy_dir()))

    for name in (Path(item) for item in os.scandir(path)):
        if ignore.match(name):
            continue

        statinfo = os.stat(name)
        mode = statinfo.st_mode

        if stat.S_ISDIR(mode):
            yield from walk(name)
        elif stat.S_ISREG(mode) or stat.S_ISLNK(mode):
            yield name, statinfo

def list_snapshots():
    snapshots = []

    for item in os.scandir(snapshot_dir()):
        statinfo = os.stat(item)

        snapshots.append((statinfo.st_mtime, Path(item)))

    return sorted(snapshots)

def get_last_snapshot():
    snapshots = list_snapshots()

    if snapshots:
        _, path = snapshots[-1]
        return Directory.load(path)

def changes(snapshot=None):
    if not snapshot:
        snapshot = get_last_snapshot()

    for path, statinfo in walk(Path(".")):
        state = None

        st_mtime = statinfo.st_mtime

        if snapshot:
            try:
                prev = snapshot.lookup(path)

                if st_mtime > prev.st_mtime:
                    state = "modified"
            except NoSuchFile:
                state = "new"
        else:
            state = "new"

        if state:
            yield path, state

def create_snapshot():
    last_snapshot = get_last_snapshot()
    snapshot = Directory()

    for path, statinfo in walk(Path(".")):
        modified = True
        st_mtime = statinfo.st_mtime

        if last_snapshot:
            try:
                prev = last_snapshot.lookup(path)

                if st_mtime > prev.st_mtime:
                    modified = True
                else:
                    modified = False
            except NoSuchFile:
                modified = True

        if modified:
            file_hash = add_file(path)
            file_ = File(st_mtime, file_hash)
        else:
            file_hash = prev.file_hash
            file_ = prev

        snapshot.add_file(path, file_)

    return snapshot.save()

def remove_snapshot(snapshot):
    os.remove(snapshot_dir() / snapshot)

def load_snapshot(snapshot):
    return Directory.load(snapshot_dir() / snapshot)

def referenced_objects():
    objs = set([])

    for _, snapshot in list_snapshots():
        tree = Directory.load(snapshot)

        for f in tree.leaves():
            objs.add(f.file_hash)

    return objs
