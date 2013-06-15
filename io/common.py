# common methods used by loaders

def get_file_read_handle(f):
    """
    Checks if f is a file name or file-like object
    @returns a file-like object
    """
    if hasattr(f, 'readline'):
        return f, True
    else: #XXX: more checks??
        return open(f), False

def get_file_write_handle(f):
    """
    Checks if f is a file name or file-like object
    @returns a file-like object
    """
    if hasattr(f, 'write'):
        return f, True
    else: #XXX: more checks??
        return open(f,'w'), False
