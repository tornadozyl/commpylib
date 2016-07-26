#!/usr/bin/env python

from basicresult import CBasicResult
import os
import sys
import copy
import globalins_ex
import ConfigParser
MAIL_CFG_TEMPLATE = {'sender':None, 'receivers':'', 'cc':'', 'subject':''}

class CSendMail(object):
    _mailinfo = {}
    
    def __init__(self):
        pass
    
    @staticmethod
    def SendFileMail(sender, receivers, cc, subject, mailfile, accessoryfile='', htmloption = False, passwd = None, log = None):
        cmd = "sendmail2 '%s' '%s' '%s' '%s' %s "%(sender, receivers, cc, subject, mailfile)

	if len(accessoryfile) > 0:
            cmd = cmd + " "
            cmd = cmd + accessoryfile    


        if htmloption:
            cmd = cmd + " --html"
        
        if None != passwd:
            passwdinfo = "--pass=%s"%passwd
            cmd = cmd + passwdinfo
        
        if None != log:
            log.info(cmd)
        else:
            print cmd
        
        ret = os.system(cmd)
        if 0 != ret:
            return CBasicResult(-1, "SendMail %s failed"%subject, -1, cmd)
        
        return CBasicResult()
    
    @staticmethod
    def SendStringMail(sender, receivers, cc, subject, mailstring, accessoryfile = '', htmloption = False, passwd = None, log = None):
        mailfile = ".CSendMail.tmpfile"
        f = open(mailfile, 'w')
        f.write(mailstring)
        f.close()
        
        return CSendMail.SendFileMail(sender, receivers, cc, subject, mailfile, accessoryfile, htmloption, passwd, log)
        
    @staticmethod
    def SendCfgFileMail(cfg_sec_name, mailfile, accessoryfile = '', htmloption = False, \
                        passwd = None, log = None, refresh = False, subject_suffix=''):
        #use cfg_sec_name(config section name) as key, before use this method you need to use globalins_ex to init
        if not CSendMail._mailinfo.has_key(cfg_sec_name):
            rst, cfg = globalins_ex.GlobalIns.getCfgInstance(refresh)
            if 0 != rst._resultcode:
                return rst
            
            try:
                mail_cfg = copy.deepcopy(MAIL_CFG_TEMPLATE)
                mail_cfg['sender'] = cfg.get(cfg_sec_name, 'sender')
                mail_cfg['receivers'] = cfg.get(cfg_sec_name, 'receivers')
                mail_cfg['cc'] = cfg.get(cfg_sec_name, 'cc')
                subject = cfg.get(cfg_sec_name, 'subject') + subject_suffix
                mail_cfg['subject'] = subject
                CSendMail._mailinfo[cfg_sec_name] = mail_cfg
            
            except ConfigParser.NoSectionError, e:
                return CBasicResult(-1, e, -1, e)
            
        mailconfig = CSendMail._mailinfo[cfg_sec_name]
        
        return CSendMail.SendFileMail(mailconfig['sender'], mailconfig['receivers'], mailconfig['cc'], mail_cfg['subject'], \
                            mailfile, accessoryfile, htmloption, passwd, log)
        
    @staticmethod
    def SendCfgStringMail(cfg_sec_name, mailstring, accessoryfile = '', htmloption = False, \
                        passwd = None, log = None, refresh = False, subject_suffix=''):
        mailfile = ".CSendMail.tmpfile"
        f = open(mailfile, 'w')
        f.write(mailstring)
        f.close()
        
        return CSendMail.SendCfgFileMail(cfg_sec_name, mailfile, accessoryfile, htmloption, passwd, log, refresh, subject_suffix)
    
    
def demo():
   # rst = CSendMail.SendStringMail("hillzhang", "hillzhang", "", "test", "this is a test")
   # if 0 != rst._resultcode:
   #     print rst
   #     sys.exit(-1)

    rst = globalins_ex.GlobalIns.setConfigPath("globalins_demo_config.ini")
    if 0 != rst._resultcode:
        return rst

    rst = CSendMail.SendCfgStringMail('mail_demo', 'this is a cfg mail test', 'test.py')
    if 0 != rst._resultcode:
        print rst
        sys.exit(-1)
    print "success"
    
    
if "__main__" == __name__:
    demo()
