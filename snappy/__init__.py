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

from .storage import snappy_dir, storage_dir
from .snapshot import snapshot_dir, ignore_filename

def snappy_init():
    for path in (snappy_dir(), storage_dir(), snapshot_dir()):
        path.mkdir(exist_ok=True)

    ignore_filename().touch()
