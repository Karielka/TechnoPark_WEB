class SimplePaginator:
    def __init__(self, total_pages: int):
        self.num_pages = total_pages
        self.page_range = range(1, total_pages + 1)


class SimplePage:
    def __init__(self, objects, number, total_pages):
        self.object_list = objects
        self.number = number
        self.paginator = SimplePaginator(total_pages)

    @property
    def has_next(self):
        return self.number < self.paginator.num_pages

    @property
    def has_previous(self):
        return self.number > 1

    def next_page_number(self):
        return min(self.number + 1, self.paginator.num_pages)

    def previous_page_number(self):
        return max(self.number - 1, 1)


def paginate(objects, page_number, total_pages):
    page_number = max(1, min(page_number, total_pages or 1))
    return SimplePage(objects, page_number, total_pages or 1)
