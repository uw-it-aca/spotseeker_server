import django.dispatch

spot_pre_build = django.dispatch.Signal(providing_args=['request', 'json_values', 'spot', 'stash', 'partial_update'])
spot_pre_save = django.dispatch.Signal(providing_args=['request', 'json_values', 'spot', 'stash', 'partial_update'])
spot_post_build = django.dispatch.Signal(providing_args=['request', 'response', 'spot', 'stash', 'partial_update'])
spot_post_save = django.dispatch.Signal(providing_args=['request', 'spot', 'stash', 'partial_update'])
