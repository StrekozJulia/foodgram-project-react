from rest_framework import mixins, viewsets


class UserMixin(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    pass


class ReadOnlyMixin(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    pass


class ListMixin(mixins.ListModelMixin,
                viewsets.GenericViewSet):
    pass


class CreateDestroyMixin(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass
