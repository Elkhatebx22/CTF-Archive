from django.contrib import admin

from .models import (
    AssetTag,
    AuditLine,
    ContactCard,
    DeliveryRecord,
    DeskRecord,
    DeskVisit,
    DispatchSecret,
    GenericNote,
    NotificationDraft,
    Project,
    ReviewTicket,
    RoutingEnvelope,
)


admin.site.register(Project)
admin.site.register(ReviewTicket)
admin.site.register(DeskRecord)
admin.site.register(GenericNote)
admin.site.register(DeliveryRecord)
admin.site.register(DeskVisit)
admin.site.register(DispatchSecret)
admin.site.register(RoutingEnvelope)
admin.site.register(AssetTag)
admin.site.register(ContactCard)
admin.site.register(AuditLine)
admin.site.register(NotificationDraft)
