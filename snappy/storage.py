# Copyright 2018 Eivind Alexander Bergem <eivind.bergem@gmail.com>
# This file is part of snappy.

# snappy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# snappy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with snappy.  If not, see <http://www.gnu.org/licenses/>.

import hashlib
import shutil
import os

from stat import S_IWUSR, S_IWGRP, S_IWOTH
from pathlib import Path

SNAPPY_DIR = ".snappy"
STORAGE = "storage"

def snappy_dir():
    return Path(SNAPPY_DIR)

def storage_dir():
    return snappy_dir() / STORAGE

def get_file_hash(filename, blocksize=2**20):
    m = hashlib.sha256()

    with filename.open("rb", buffering=0) as fd:
        while True:
            data = fd.read(blocksize)

            if not data:
                break

            m.update(data)

    return m.hexdigest()

def get_string_hash(s):
    m = hashlib.sha256()

    m.update(s)

    return m.hexdigest()

def split_hash(h, n=2):
    return h[:n], h[n:]

def addmod(filename, perm):
    mode = filename.stat().st_mode

    os.chmod(filename, mode|perm)

def rmmod(filename, perm):
    mode = filename.stat().st_mode

    os.chmod(filename, mode&~perm)

def read_only(filename):
    rmmod(filename, S_IWUSR|S_IWGRP|S_IWOTH)

def user_write(filename):
    addmod(filename, S_IWUSR)

def add_file(filename):
    file_hash = get_file_hash(filename)
    pre, rest = split_hash(file_hash)

    dst = storage_dir() / pre / rest
    if not dst.exists():
        dst.parent.mkdir(exist_ok=True)

        shutil.copy2(str(filename), str(dst))
        read_only(dst)

    return file_hash

def copy_object(obj, dst):
    shutil.copy2(get_object_path(obj), dst)
    user_write(dst)

def get_object_path(obj):
    pre, rest = split_hash(obj)

    return storage_dir() / pre / rest

def list_objects():
    for pre in storage_dir().iterdir():
        for rest in pre.iterdir():
            yield str(pre.name) + str(rest.name)

def is_empty(path):
    for child in path.iterdir():
        return False

    return True

def remove_object(obj):
    pre, rest = split_hash(obj)

    path = storage_dir() / pre

    user_write(path / rest)
    (path / rest).unlink()

    if is_empty(path):
        (storage_dir() / pre).rmdir()
