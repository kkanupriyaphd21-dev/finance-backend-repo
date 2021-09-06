from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

# c095 2021-08-06T15:14:58 wire the initial project files

# c102 2021-08-22T10:31:47 fix(business): startup settings

# c109 2021-09-06T10:48:36 tighten bootstrap config
