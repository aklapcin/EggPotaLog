import uuid
from google.appengine.api import memcache


def create_paginator(request=None, query=None, default_per_page=10,\
        possible_ordering=[]):
    if query is None or request is None or query is None:
        return

    try:
        per_page = int(request.GET.get('per_page', default_per_page))
    except ValueError:
        per_page = default_per_page
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    paginator_id = request.GET.get('paginator_id')
    order_by = request.GET.get('order_by')
    if order_by is not None:
        test_order = order_by if order_by[0] != "-" else order_by[1:]
        if test_order in possible_ordering:
            query = query.order(order_by)
        else:
            order_by = None

    paginator = GAEPaginator(query=query, page=page, paginator_id=paginator_id,\
        per_page=per_page, order_by=order_by)

    return paginator


class GAEPaginator(object):
    '''Special GAE paginator, using only cursors, to minimize
    database reads.
    Parameters:
        -query - paginated query
        -page_size - number of objects by page, default to 50
        -page - which page should be retrived
        -paginator_id - as results are stored we need that
    '''

    def __init__(self, *args, **kwargs):

        self.query = kwargs.get('query')

        self.paginator_id = kwargs.get('paginator_id')

        #check paramteres given by user
        new_per_page = kwargs.get('per_page')
        new_order_by = kwargs.get('order_by')
        new_page = kwargs.get('page')

        #check if paginator id should be changed

        change_paginator_id = self.check_if_paginator_changed(new_per_page, new_order_by, new_page)
        #need id to get cursors from memcache
        if change_paginator_id:
            if self.paginator_id is not None:
                self.clean_memcache()
            self.paginator_id = uuid.uuid1().hex
            self.page_number = 1
            self.order_by = new_order_by
            self.per_page = new_per_page
            self.last_page = 0
            self.save_to_memcache()
            self.end = False
        else:
            self.page_number = new_page
            self.last_page = self.get_from_memcache("last")
            self.end = self.get_from_memcache("end_reached")

        self.fetch_objects()

    def check_if_paginator_changed(self, new_per_page, new_order_by, new_page):

        if self.paginator_id is None:
            return True
        if new_page is None or new_page < 0:
            return True

        change_paginator_id = False

        self.per_page = memcache.get(self.get_key("per_page"))
        self.order_by = memcache.get(self.get_key("order_by"))
        self.last_page = memcache.get(self.get_key("last"))

        if self.per_page != new_per_page or new_per_page < 0:
            change_paginator_id = True
        if self.order_by != new_order_by:
            change_paginator_id = True
        if self.last_page is None:
            change_paginator_id = True
        return change_paginator_id

    def clean_memcache(self):
        for i in range(self.last_page + 1):
            self.delete_from_memcache(i + 1)
        self.delete_from_memcache('last')
        self.delete_from_memcache('order_by')
        self.delete_from_memcache('per_page')
        self.delete_from_memcache('end_reached')

    def save_to_memcache(self):
        self.set_to_memcache('last', self.last_page)
        self.set_to_memcache('order_by', self.order_by)
        self.set_to_memcache('per_page', self.per_page)
        self.set_to_memcache('end_reached', False)

    def set_to_memcache(self, key, value):
        new_key = self.get_key(key)
        memcache.set(new_key, time=60 * 60 * 24, value=value)

    def delete_from_memcache(self, key):
        memcache.delete(self.get_key(key))

    def get_from_memcache(self, key):
        return memcache.get(self.get_key(key))

    def get_cursor(self):
        #if it is first page, there is no page in memcached
        if self.page_number == 1:
            return

        #if somebody wants to get last page, he will get only
        #the last page we know
        if self.page_number > (self.last_page + 1):
            self.page_number = self.last_page + 1
        #now, when we know that cursor is in memcache
        if self.page_number <= (self.last_page + 1):
            self.cursor = self.get_from_memcache(self.page_number - 1)
            #but if we only thouth, we do...
            if self.cursor is None:
                self.clean_memcache()
                self.page_number = 1
                self.last_page = 0
                return
            else:
                return self.cursor

    def fetch_objects(self):

        self.cursor = self.get_cursor()
        if self.cursor is None:
            self.objects = self.query.fetch(self.per_page)

        else:
            self.objects = self.query.with_cursor(start_cursor=self.cursor).\
                fetch(self.per_page)
        self.update_memcache_state()
        self.count_help_values()

    def update_memcache_state(self):
        #if we just retrived new page
        #increment last page in memcache
        if self.page_number > self.last_page:
            self.set_to_memcache("last", self.page_number)
            self.last_page = self.page_number

        #get cursor of new query
        self.new_cursor = self.query.cursor()
        if self.end == False:
            self.end = (len(self.objects) < self.per_page)
        #if it does not point to the end of query
        #store it
        if not self.end:
            self.set_to_memcache(self.page_number, self.new_cursor)
        else:
            self.set_to_memcache("end_reached", True)

    def count_help_values(self):

        self.has_next = not self.end
        self.has_previous = (self.page_number != 1)
        if self.has_previous:
            self.previous_page = self.page_number - 1
        else:
            self.previous_page = None
        if self.has_next:
            self.next_page = self.page_number + 1
        else:
            self.next_page = None
        self.current_page = self.page_number
        self.start = (self.current_page - 1) * self.per_page

    def get_key(self, val):
        return "cursor_%s_%s" % (self.paginator_id, val)
