from django.contrib import admin
from spotseeker_server.models import *


class SpotAdmin(admin.ModelAdmin):
    """ The admin model for a Spot.
    The ETag is excluded because it is generated on Spot save.
    """
    exclude = ('etag',)
admin.site.register(Spot, SpotAdmin)


class SpotImageAdmin(admin.ModelAdmin):
    """ The admin model for a SpotImage.
    Content-type, width, height, and ETag are all filled in by the server on SpotImage save.
    """
    exclude = ('content_type', 'width', 'height', 'etag',)
admin.site.register(SpotImage, SpotImageAdmin)


admin.site.register(SpotAvailableHours)
admin.site.register(SpotExtendedInfo)
admin.site.register(TrustedOAuthClient)
