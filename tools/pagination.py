from math import ceil

from models import objects


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


class Paginator:
    def __init__(self, query, page, page_size=20):
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.page_size = page_size
        #: the total number of items matching the query
        self._count = None
        self.items = self.query.paginate(page, page_size)

    @property
    def count(self):
        if self._count:
            return self._count
        with objects.allow_sync():
            self._count = self.items.count()
        return self._count

    @property
    def pages(self):
        """The total number of pages"""
        return int(ceil(self.count / float(self.page_size)))

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    def prev(self):
        assert self.query is not None
        return self.query.paginate(self.page - 1, self.page_size)

    def next(self):
        assert self.query is not None
        return self.query.paginate(self.page + 1, self.page_size)


class Pagination:
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 100
    page_size = None
    paginator_class = Paginator
    paginator = None

    def get_paginated_response(self, data):
        return (dict([
            ('count', self.paginator.count),
            ('page_num', self.paginator.page),
            ('page_size', self.paginator.page_size),
            ('results', data)
        ]))

    def paginate_queryset(self, query, handler):
        page_size = self.get_page_size(handler)
        if not page_size:
            return None

        page_number = int(handler.get_argument(self.page_query_param, 1))
        self.paginator = self.paginator_class(query, page_number, page_size)
        page = self.paginator.items
        return page

    def get_page_size(self, handler):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    handler.get_argument(self.page_size_query_param, 0),
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

