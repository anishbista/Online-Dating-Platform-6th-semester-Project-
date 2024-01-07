from django.shortcuts import redirect


def profile_update_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.profile.phone is None:
            return redirect("update_profile", pk=request.user.profile.id)
        else:
            return view_func(request, *args, **kwargs)

    return wrap
