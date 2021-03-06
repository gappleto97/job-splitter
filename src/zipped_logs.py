from logging.handlers import RotatingFileHandler
from os import path, remove, rename
from zipfile import ZipFile, ZIP_DEFLATED


class ZippedRotatingFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__closed = False

    def _zip_file(self, name, mode='w'):
        return ZipFile(name, mode, compression=ZIP_DEFLATED, compresslevel=9, allowZip64=True)

    def rotation_filename(self, string):
        return string + '.zip'

    def close(self):
        super().close()
        if not self.__closed:
            with self._zip_file(self.baseFilename + '.zip') as dest:
                basename = path.basename(self.baseFilename)
                with open(self.baseFilename, 'rb') as f:
                    dest.writestr(basename, f.read())
                remove(self.baseFilename)
                max_digits = len(str(self.backupCount))
                for i in range(1, self.backupCount):
                    fn = "%s.%d.zip" % (self.baseFilename, i)
                    if not path.exists(fn):
                        break
                    with self._zip_file(fn, 'r') as src:
                        dest.writestr(path.basename(basename + '.' + str(i).zfill(max_digits)), src.read(basename))
                    remove(fn)
        self.__closed = True

    def rotator(self, source, dest):
        """Rotate files by placing them into a zip file."""
        if source == self.baseFilename:
            with open(source, "rb") as sf:
                with self._zip_file(dest) as z:
                    z.writestr(path.basename(self.baseFilename), sf.read())
            remove(source)
        else:
            rename(source, dest)
