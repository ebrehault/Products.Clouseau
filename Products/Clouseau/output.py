from xml.dom.minidom import getDOMImplementation
import time
import sys

impl = getDOMImplementation()

class wrapper:
    version = 0.1

    def __init__(self):
        self.start = time.time()
        self.xml = impl.createDocument(None, "response", None)
        self.top = self.xml.documentElement
        self.add_info()

    def add_info(self):
        info = self.xml.createElement("info")
        info.setAttribute("start", time.ctime())
        info.setAttribute("version", "0.1")
        info.setAttribute("author", "Clouseau")
        self.add(info)

    def add_error(self):
        error = self.xml.createElement("error")
        type, value = sys.exc_info()[:2]
        error.setAttribute("type", str(type))
        error.setAttribute("value", str(value))
        self.add(error)

    def get_info(self):
        return self.top.getElementsByTagName("info")[0]

    def add(self, node):
        self.top.appendChild(node)

    def __str__(self):
        info = self.get_info()
        info.setAttribute("end", time.ctime())
        info.setAttribute("length", str(time.time() - self.start))
        return self.xml.toxml()