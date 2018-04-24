from flask_restful import fields


class Num(fields.Raw):

    def format(self, value):
        return value.count()


class EdgeUrl(fields.Raw):

    def __init__(self, endpoint, direction, *args, **kwargs):
        super(EdgeUrl, self).__init__(*args, **kwargs)
        self.endpoint = endpoint
        self.direction = direction

    def output(self, key, obj):
        if self.direction == 0:
            if obj.has_prev:
                return fields.url_for(self.endpoint, page=obj.page - 1, _external=True)

            else:
                return None

        if self.direction == 1:
            if obj.has_next:
                return fields.url_for(self.endpoint, page=obj.page + 1, _external=True)

            else:
                return None


def PaginateUrl(endpoint, name, attr):

    class PaginateUrl(fields.Raw):

        def output(self, key, obj):
            try:
                index = self.index
            except:
                self.index = 0
            try:
                now_obj = obj[self.index]
            except IndexError:
                self.index = 0
                now_obj = obj[self.index]
            key = self.name
            value = now_obj.__getattribute__(self.attr)
            pair = {key: value}
            self.index += 1
            return fields.url_for(self.endpoint, **pair, _external=True)

    PaginateUrl.endpoint = endpoint
    PaginateUrl.name = name
    PaginateUrl.attr = attr

    return PaginateUrl
