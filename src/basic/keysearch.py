#_*_encoding:utf-8_*_


class KeySearch:
    def __init__(self, filename):
        self.filename = filename
        self.keyvalues = {}

    def readFile(self):
        try:
            f = open(self.filename, 'r')
            try:
                for line in f.readlines():
                    print line
                    (key, valueStr) = line.split(';', 1)
                    print key, valueStr
                print "\n".join("%s=%s" % (k, v)
                                for (k, v) in self.keyvalues.items())
            finally:
                f.close()
        except IOError:
            #print 'Error reading file: ', self.name
            pass

if __name__ == "__main__":
    keysearch = KeySearch('../data/data.txt')
    keysearch.readFile()
