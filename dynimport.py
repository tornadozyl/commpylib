'''
    this module is used to add module by its string name
    the interface function is dimport, modulename is the filename with out suffix
    e.g if u has a file named test.py, you may use like dlimport("test")
'''

from basicresult import CBasicResult
import imp
import copy
import os

TMP_MODULE_INFO = {"name":None, "module":None, "valid":False, "fstat":None}

class SingleDImport(object):
    _dynimport_dict = {}
    def __init__(self):
        pass
    
    @staticmethod
    def isImported(name):
        return SingleDImport._dynimport_dict.has_key(name)
    
    @staticmethod
    def isModified(name):
        filename = "%s.py"%name.replace(".", "/")
        #print filename
        statinfo = os.stat(filename)
        mfinfo = SingleDImport._dynimport_dict[name]["fstat"]
        if statinfo.st_ctime != mfinfo.st_ctime or statinfo.st_mtime != mfinfo.st_mtime:
            return True
        return False
            
    @staticmethod
    def addImportedModule(modulename):
        filename = "%s.py"%modulename.replace(".", "/")
        if not os.path.exists(filename):
            return CBasicResult(-1, "%s not exist"%filename, -1, "%s not exist"%filename), None
        try:
            statinfo = os.stat(filename)
            m = imp.load_source(modulename, filename)
            minfo = copy.deepcopy(TMP_MODULE_INFO)
            minfo['name'] = modulename
            minfo['module'] = m
            minfo['valid'] = True
            minfo['fstat'] = statinfo
            SingleDImport._dynimport_dict[minfo['name']] = minfo
            return CBasicResult(), m
        except Exception, e:
            return CBasicResult(-1, "addImportedModule failed", -1, e), None
            
    @staticmethod
    def getModule(name):
        if SingleDImport.isImported(name) and not SingleDImport.isModified(name):
            #print "use inited"
            return CBasicResult(), SingleDImport._dynimport_dict[name]['module']
        else:
            #print "use new"
            return SingleDImport.addImportedModule(name)

def dimport(modulename):
    return SingleDImport.getModule(modulename)
    
    
if "__main__" == __name__:
    for i in range(2):
        rst, m = dimport("dymodule.test")
        if 0 != rst._resultcode:
            print rst
            import sys
            sys.exit(-1)
        m.test()
