from django.contrib import admin
from apiApp.models import White_IPs

class whiteIPAdmin(admin.ModelAdmin):
    model = White_IPs
    date_hierarchy = 'created_at'
    ordering = ['created_at']
    search_fields = ['ip']

admin.site.register(White_IPs, whiteIPAdmin)



