'''Classes used for parsing text.'''


class ReprParser(object):
    '''Class for parsing strings to appear as __repr__ output.'''

    def __init__(self, other):
        self.other = other

    def parse(self, str_kwargs):
        class_name = self.other.__class__.__name__
        head = '{}('.format(class_name)
        tail = ')'
        return head + ', '.join(str_kwargs) + tail
