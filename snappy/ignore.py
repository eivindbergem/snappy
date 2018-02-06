from fnmatch import fnmatch

def parse_lines(lines):
    for line in lines:
        line = line.strip()

        pos = line.find("#")
        if pos > 0:
            line = line[:pos]

        if line:
            yield line

class IgnoreList(object):
    def __init__(self, filename):
        try:
            with open(filename) as fd:
                self.patterns = [line for line in parse_lines(fd)]
        except FileNotFoundError:
            self.patterns = []

    def match(self, path):
        for pattern in self.patterns:
            if fnmatch(path, pattern):
                return True

    def add_pattern(self, pattern):
        self.patterns.append(pattern)
