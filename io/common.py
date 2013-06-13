# common methods used by loaders

def get_file_handle(f):
    """
    Checks if f is a file name or file-like object
    @returns a file-like object
    """
    if hasattr(f, readline):
        return f
    else: #XXX: more checks??
        return open(f)
