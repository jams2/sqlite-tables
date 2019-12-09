import re
from string import Template


class SQLiteTemplate(Template):
    '''Overrides the substitute method to replace multiple occurences
    of whitespace with one.
    '''
    ws_pattern = re.compile(r'(?<=\s)\s+|\s+$|\s+(?=\)$)|(?<=\s)\s+(?=\))')

    def substitute(self, *args, **kwargs):
        return self.ws_pattern.sub('', super().substitute(*args, **kwargs))
