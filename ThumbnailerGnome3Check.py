# -*- coding: utf-8 -*-

#
# check thumbnailer file format violation
# losely based on http://www.ict.griffith.edu.au/anthony/info/X/Thumbnailing.txt
# but that's not really specified formally
#
# in fact, that's just for nautilus, there is a different spec for thunar 
# who use the desktop format, with a extension
# and a different for kde

from Filter import addDetails, printError, printWarning
import AbstractCheck
from ConfigParser import RawConfigParser
import os

STANDARD_BIN_DIRS = ['/bin/','/sbin/','/usr/bin/','/usr/sbin/']

class ThumbnailerGnome3Check(AbstractCheck.AbstractFilesCheck):
    def __init__(self):
        self.cfp = RawConfigParser()
        AbstractCheck.AbstractFilesCheck.__init__(
            self, "ThumbnailerGnome3Check", "/usr/share/thumbnailers/.*\.thumbnailer$")

    # should be moved outside for reuse by other classes
    def check_exec(self, section, root):
        # TODO should check TryExec too
        # TODO should check if there %u in Exec ( else, this may not work as needed )
        binary = self.cfp.get(section,'Exec').split(' ',1)[0]
        found = False
        for i in STANDARD_BIN_DIRS:
            if os.path.exists(root + i + binary):
                        # no need to check if the binary is +x, rpmlint does it
                        # in another place
                        found = True
        return found 

    def check_mimetype(self, pkg, filename, section = 'Thumbnailer Entry'):
        root = pkg.dirName()
        f = root + filename
        cfp = RawConfigParser()
        cfp.read(f)        
        # http://www.iana.org/assignments/media-types
        # http://en.wikipedia.org/wiki/Internet_media_type
        content_type = ['application','audio','example','image',
                        'message','model','multipart','text','video']
        mime_type = cfp.get(section, 'MimeType')

        if mime_type[-1] == ';':
            mime_type = mime_type[:-1]
        else:
            printWarning(pkg, 'missing-comma-mimetype', filename)
    
        for m in mime_type.split(';'):
            c_type, subtype = m.split('/',1)
            if c_type not in content_type:
                printWarning(pkg, 'wrong-mimetype',filename,m)
                
        # TODO finish to check against the subtype


    def check_file(self, pkg, filename):
        root = pkg.dirName()
        f = root + filename
        # check if this is a .ini
        self.cfp.read(f)
        if self.cfp.has_section('Thumbnailer Entry'):
            has_needed_keys = self.cfp.has_option('Thumbnailer Entry','Exec') and \
                              self.cfp.has_option('Thumbnailer Entry','TryExec') and \
                              self.cfp.has_option('Thumbnailer Entry','MimeType')

            if has_needed_keys:
                if not self.check_exec('Thumbnailer Entry',root):
                    printError(pkg, 'thumbnailer-gnome3-missing-binary', filename)

                self.check_mimetype(pkg, filename)
            else:
                printWarning(pkg, 'thumbnailer-gnome3-incorrect-file',filename)
        else:
            printWarning(pkg, 'thumbnailer-gnome3-missing-section', filename)

check = ThumbnailerGnome3Check()
addDetails(
'thumbnailer-gnome3-missing-section',
'''The thumbnailer file is incorrect, there is no Thumbnailer Entry section'''
'thumbnailer-gnome3-missing-binary',
'''The thumbnailer depend on a binary not present in the package'''
'thumbnailer-gnome3-incorrect-file',
'''The thumbnailer file is incorrect''',
'missing-comma-mimetype',
'''The mimetype entry should have a final ;''',
'wrong-mimetype',
'''This mimetype is not registered at IANA''',
)


# Local variables:
# indent-tabs-mode: nil
# py-indent-offset: 4
# End:
# ex: ts=4 sw=4 et
