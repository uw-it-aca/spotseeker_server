"""
Support for Organization search filters. This allows you to hook into
views/search
"""
from django.conf import settings
from django.utils.importlib import import_module

class Filter(object):
    """
    A search filter base class. Implementers should subclass this and
    redefine the methods they're interested in.

    A new instance of this class is created for each search request.
    
    Instance Variables:
        request: The HTTP request.
        has_valid_search_param: If, in filter_query, we encountered a
            search parameter that will limit the query.
            Default: False.
    """

    keys = set()

    def __init__(self, request):
        self.request = request
        self.has_valid_search_param = False

    def filter_query(self, query):
        """
        Filters the model query before it is actualized. Set
        self.has_valid_search_param to True if you add a parameter
        that limits the query.

        Return a query object (QuerySet), whether you modify it or
        not.
        """
        return query

    def filter_results(self, spots):
        """
        Filters the spots actualized from the query. Remove or add
        spots based on non-database conditions.

        Return the modified set of spots, or the original set if
        no modification occurred.
        """
        return spots

class FilterChain(object):
    """
    A collection of filters to run on a spot search. A new instance
    of this class is created for each search.

    Instance Variables:
        request: The HTTP request.
        has_valid_search_param: If any filter in the query has a
            search parameter that will limit the query.
            Default: False.
        filters: array of filter instances.
    """

    filters = []
    keys = set()

    @staticmethod
    def _load_filters():
        """Loads the filters and their modules"""
        if hasattr(settings, 'SPOTSEEKER_SEARCH_FILTERS'):
            for filtername in settings.SPOTSEEKER_SEARCH_FILTERS:
                modname, attrname = filtername.rsplit('.', 1)
                try:
                    mod = import_module(modname)
                except ImportError, e:
                    raise ImproperlyConfigured(
                        'Error importing module %s: "%s"' %
                        (modname, e)
                        )

                try:
                    attr = getattr(mod, attrname)
                except AttributeError:
                    raise ImproperlyConfigured(
                        'Module "%s" does not define "%s".' %
                        (modname, attrname))

                FilterChain.filters.append(attr)
                FilterChain.keys.update(attr.keys)
    _load_filters()

    def __init__(self, request):
        self.request = request
        self.has_valid_search_param = False

        self.filters = []
        for fclass in FilterChain.filters:
            self.filters.append(fclass(request))

    def filter_query(self, query):
        """Calls filter_query for each defined filter."""
        for f in self.filters:
            query = f.filter_query(query)
            if f.has_valid_search_param:
                self.has_valid_search_param = True
        return query

    def filter_results(self, spots):
        """Calls filter_results for each defined filter."""
        for f in self.filters:
            spots = f.filter_results(spots)
        return spots

    def filters_key(self, key):
        return key in FilterChain.keys

