from functools import wraps
import hashlib
import random
import time

def update_etag(func):
    """Any model with an ETag can decorate an instance method with
    this to have a new ETag automatically generated. It's up to the
    wrapped function, however, to call save()."""
    def _newETag(self, *args, **kwargs):
        self.etag = hashlib.sha1("{0} - {1}".format(random.random(),
                                 time.time()).encode('utf-8')).hexdigest()
        return func(self, *args, **kwargs)
    return wraps(func)(_newETag)