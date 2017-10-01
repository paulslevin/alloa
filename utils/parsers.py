'''Objects used for parsing text.'''


def parse_repr(cls_instance, str_kwargs):
    class_name = cls_instance.__class__.__name__
    head = '{}('.format(class_name)
    tail = ')'
    return head + ', '.join(str_kwargs) + tail
