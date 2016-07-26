#!/usr/bin/env python

from basicresult import CBasicResult
import os
import sys
from globalins_ex import GlobalIns
import ConfigParser
#import pdb
class CRsync(object):
    
    _rsync_cfg = {}
    
    def __init__(self):
        pass
    
    @staticmethod
    def Rsync_Pull(ip, port, username, src_path, src_name, dst_path, dst_name, force = False, log = None):
        srcfull = "%s/%s"%(src_path, src_name)
        dstfull = "%s/%s"%(dst_path, dst_name)
        if os.path.exists(dstfull) and not force:	
            return CBasicResult(), dstfull 

        if os.path.exists(dstfull):
            os.remove(dstfull)
            
        cmd = "rsync --port=%s %s@%s::%s %s"%(port, username, ip, srcfull, dst_path)
        
        if None != log:
            log.info(cmd)
            
        print cmd
        
        ret = os.system(cmd)
        if 0 != ret:
            return CBasicResult(-1, "%s failed"%cmd, -1, "%s failed"%cmd), dstfull 
        
        old_name = "%s/%s"%(dst_path, src_name)
        if not os.path.exists(old_name):
            return CBasicResult(-1, "%s failed"%cmd, -1, "%s failed"%cmd), dstfull

        if src_name != dst_name:
            os.rename(old_name, dstfull)
        
        return CBasicResult(), dstfull
    
    @staticmethod
    def CfgRsync_Pull(sec_name, src_name, dst_name, force = False, log = None):
        #you need first init GlobalIns
        rst, cfg = GlobalIns.getCfgInstance()
        
        if 0 != rst._resultcode:
            return rst, None

        if not CRsync._rsync_cfg.has_key(sec_name):
            rsync_cfg = {}
            try:
                rsync_cfg['ip'] = cfg.get(sec_name, 'ip')
                rsync_cfg['port'] = cfg.get(sec_name, 'port')
                rsync_cfg['user'] = cfg.get(sec_name, 'user')
                rsync_cfg['src_path'] = cfg.get(sec_name, 'src_path')
                rsync_cfg['dst_path'] = cfg.get(sec_name, 'dst_path')
            
                CRsync._rsync_cfg[sec_name] = rsync_cfg
            
            except ConfigParser.NoSectionError, e:
                return CBasicResult(-1, e, -1, e) , None
            
        rsync_cfg = CRsync._rsync_cfg[sec_name]
        
        return CRsync.Rsync_Pull(rsync_cfg['ip'], rsync_cfg['port'], rsync_cfg['user'], \
                                 rsync_cfg['src_path'], src_name, rsync_cfg['dst_path'], dst_name, force, log)
        
        
def demo():
    GlobalIns.setConfigPath("globalins_demo_config.ini")
    
    rst, name = CRsync.CfgRsync_Pull('rsync_demo', 't_acct_qqtest_20131218.01006', 'qqtest', True)
    if 0 != rst._resultcode:
        print rst
        sys.exit(-1)
        
    print name
        
if "__main__" == __name__:
    demo()

        
