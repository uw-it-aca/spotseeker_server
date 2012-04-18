from django.contrib import admin
from spotseeker_server.models import *

class SpotAdmin(admin.ModelAdmin):
    exclude = ('etag',)
admin.site.register(Spot, SpotAdmin)

admin.site.register(SpotAvailableHours)
admin.site.register(SpotExtendedInfo)

class SpotImageAdmin(admin.ModelAdmin):
    exclude = ('content_type', 'width', 'height', 'etag',)
admin.site.register(SpotImage, SpotImageAdmin)
