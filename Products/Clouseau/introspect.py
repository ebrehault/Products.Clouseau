import inspect 
from Products.Clouseau import ClouseauMessageFactory as _

docfinder = False
try:
    from Products import DocFinderTab
    docfinder = True
except ImportError:
    pass

# Some of this code is completely ripped with minor to no changes
# from the PyCrust project, Patrick O'Brien and Robin Dunn
# credit to them, blame to me. Some of these functions are
# line for line copies.

def getMethodTip(object):
    name = ""
    try:
        name = object.__name__
    except AttributeError:
        pass
    argspec = _(u"No arguments")

    if inspect.isbuiltin(object):
        # Builtin functions don't have an argspec that we can get.
        argspec = _(u"Not available for a bultin in function")
    else:
        # tip1 is a string like: "getCallTip(command='', locals=None)"
        argspec = apply(inspect.formatargspec, inspect.getargspec(object))
        temp = argspec.split(',')
        if len(temp) == 1:  # No other arguments.
            argspec = '()'
        elif temp[0][:2] == '(*': # first param is like *args, not self
            pass 
        else:  # Drop the first argument.
            argspec = '(' + ','.join(temp[1:]).lstrip()
        argspec = argspec[1:-1] # strip ( and )
        
    doc = None
    if callable(object):
        try:
            doc = inspect.getdoc(object)
        except:
            pass
    if not doc:
        doc = _(u"Not available")
            

    calltip = (
        [_(u"Name"), name],
        [_(u"Arguments"), argspec],
        [_(u"Documentation"), doc],
        )
    return calltip

def getZopeTip(code):
    calltip = []
    if hasattr(code, "objectIds"):
        ids = code.objectIds()
        if ids:
            objects = [_(u"Objects"), ", ".join(ids)]
            calltip.append(objects)
    if hasattr(code, "Schema"):
        fields = code.Schema().fields()
        fieldsIds = [ field.getName() for field in fields ]
        calltip.append([_(u"Schema"), ", ".join(fieldsIds)])
    if docfinder:
        if hasattr(code, "analyseDocumentation"):
            docf = code.analyseDocumentation(code)
            callables = []
            non_callables = []
            notes = []
            # show the first 5 classes, excluding item
            k = 0
            # need to change docf to support slices
            for item in docf:
                if k == 0:
                    k += 1
                    continue
                for element in item:
                    if element.Type() == "function":
                        callables.append(element.Name())
                    else:
                        non_callables.append(element.Name())
                k += 1

            # lower cased sort please
            calltip.append([ _(u"Callable"), ", ".join(lowerSort(callables))],)
            calltip.append([ _(u"Attributes"), ", ".join(lowerSort(non_callables))],)
            if notes:
                calltip.append([ _(u"Notes"), "\n".join(notes)],)

    return calltip

def lowerSort(classes):
    klasses = [ (c.lower(), c) for c in classes ]
    klasses.sort()
    return [ c[1] for c in klasses ]
    
def getObjectTip(code):
    calltip = []
    # 99% of the time the __roles__ are useless
    drs = [ c for c in dir(code) if not c.endswith('__roles__') ]
    dirres = [_(u"Methods and attributes"), ", ".join(drs)]
    calltip.append(dirres)
    return calltip

def getDirResults(code):
    calltip = []
    dirres = [_(u"Namespace"), ", ".join(code)]
    calltip.append(dirres)
    return calltip

def lookup(code, text):
    # figure out what to do
    if text.lstrip().startswith("dir("):
        return getDirResults(code)

    if hasattr(code, "aq_inner"):
        # we have a zope object
        return getZopeTip(code)
    else:
        try:
            # need better check
            return getMethodTip(code)
        except:
            return getObjectTip(code)

if __name__=='__main__':
    def foo(a, b=1):
        """ A sample """
        pass

    class bar:
        def poo(a, c=None):
            """ Pass """
            pass

    def poo(a, x=1, y=2):
        # return some stuff
        return x+y * a
        
    def tooltip(thing):
        evald = eval(thing)
        return lookup(evald, thing)

    b = bar()
    tests = [
    #    foo,
   #     "poo",
  #      "b.poo",
 #       "'a'.lower",
#        "dict",
        "x == 'a'.lower",
        ]

    for test in tests:
        print "*" * 40
        print "*", test
        print 
        print tooltip(test)
