from .signals import object_viewed_signal


class ObjectViewedMixin(object): # add this to any detailView class you want data on and add the appropriate receiver, see mixin/model app for an example of the sender
    def get_context_data(self, *args, **kwargs):
        context = super(ObjectViewedMixin, self).get_context_data(*args, **kwargs)
        request = self.request
        instance = context.get('object')
        if instance:
            object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return context
