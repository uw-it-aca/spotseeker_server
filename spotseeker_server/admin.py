from django.contrib import admin
from spotseeker_server.models import *


class SpotAdmin(admin.ModelAdmin):
    exclude = ('etag',)
admin.site.register(Spot, SpotAdmin)



class SpotImageAdmin(admin.ModelAdmin):
    exclude = ('content_type', 'width', 'height', 'etag',)
admin.site.register(SpotImage, SpotImageAdmin)


admin.site.register(SpotAvailableHours)
admin.site.register(SpotExtendedInfo)
