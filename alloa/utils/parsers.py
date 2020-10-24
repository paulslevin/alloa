"""Functions used for parsing text."""


def parse_repr(cls_instance, str_kwargs):
    class_name = cls_instance.__class__.__name__
    return f'{class_name}({", ".join(str_kwargs)})'
