from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ReviewTicket(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    preview_token = models.CharField(max_length=64, unique=True)
    state = models.CharField(max_length=32, default="queued")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DispatchSecret(models.Model):
    reference = models.CharField(max_length=80)
    checksum = models.CharField(max_length=24)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.checksum


class RoutingEnvelope(models.Model):
    secret = models.OneToOneField(DispatchSecret, on_delete=models.CASCADE)
    label = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label


class DeskRecord(models.Model):
    ticket = models.ForeignKey(ReviewTicket, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    private_body = models.TextField()
    envelope = models.OneToOneField(RoutingEnvelope, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"desk:{self.ticket_id}"


class GenericNote(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["content_type", "object_id"], name="core_generi_content_8b36a9_idx")]

    def __str__(self):
        return f"note:{self.owner_id}:{self.content_type_id}:{self.object_id}"


class DeliveryRecord(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    payload = models.TextField()
    released = models.BooleanField(default=False)

    def __str__(self):
        return f"delivery:{self.project.slug}"


class DeskVisit(models.Model):
    url = models.URLField(max_length=500)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url


class AssetTag(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    color = models.CharField(max_length=24, default="slate")

    def __str__(self):
        return self.label


class ContactCard(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=120)
    mailbox = models.EmailField()
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class AuditLine(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    event = models.CharField(max_length=160)
    reference = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event


class NotificationDraft(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    subject = models.CharField(max_length=160)
    body = models.TextField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
