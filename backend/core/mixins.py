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


class RecipeMixin(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    pass