from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class CSRFExemptMixin(object):
    """
    Mixin for do not use csrf_token.
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Using csrf_exempt on dispatch.
        """
        return super(CSRFExemptMixin, self).dispatch(request, *args, **kwargs)
