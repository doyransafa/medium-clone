class SetAuthorMixin:
    def create(self, request, *args, **kwargs):
        request.data['author'] = request.user.id
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data['author'] = request.user.id
        return super().update(request, *args, **kwargs)

