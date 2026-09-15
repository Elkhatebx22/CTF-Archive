from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import FileResponse, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context, Template, TemplateSyntaxError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST

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


MAX_NOTE_BODY_LENGTH = 4000
MAX_NOTES_PER_OBJECT_PER_USER = 25
MAX_PENDING_VISITS_PER_PROJECT = 3
VISIT_REQUEST_INTERVAL = timedelta(seconds=15)


class TicketTemplateTarget:
    def __init__(self, ticket):
        self.id = ticket.id
        self.deskrecord_set = ticket.deskrecord_set


def visible_project_or_404(request, slug):
    if request.user.is_staff:
        return get_object_or_404(Project, slug=slug)
    return get_object_or_404(Project, slug=slug, owner=request.user)


def review_ticket_notes(ticket):
    return GenericNote.objects.filter(
        content_type=ContentType.objects.get_for_model(ReviewTicket),
        object_id=ticket.id,
        owner=ticket.project.owner,
    ).order_by("created_at")


def rendered_ticket_notes(ticket, request):
    rendered_notes = []
    for note in review_ticket_notes(ticket):
        try:
            rendered = Template(note.body).render(
                Context(
                    {
                        "target": TicketTemplateTarget(note.content_object),
                        "request": request,
                    }
                )
            )
        except TemplateSyntaxError:
            rendered = "template rejected"
        rendered_notes.append((note, rendered))
    return rendered_notes


def host_name(value):
    return value.split(":")[0].lower()


def is_project_subdomain(value):
    name = host_name(value)
    return name.endswith(".cat26.local") and name != settings.APP_BASE_HOST


def ensure_desk_record(ticket):
    reviewer = User.objects.filter(username=settings.ADMIN_USERNAME).first()
    if reviewer is None:
        reviewer = User.objects.create_superuser(
            settings.ADMIN_USERNAME,
            "reviewer@cat26.local",
            settings.ADMIN_PASSWORD or get_random_string(48),
        )
    if DeskRecord.objects.filter(ticket=ticket).exists():
        return
    secret = DispatchSecret.objects.create(
        reference=f"rk-{get_random_string(32)}",
        checksum=get_random_string(16),
    )
    envelope = RoutingEnvelope.objects.create(
        secret=secret,
        label=f"routing-{get_random_string(8)}",
    )
    DeskRecord.objects.create(
        ticket=ticket,
        reviewer=reviewer,
        private_body="release desk record: use the paired routing material only in signed reviews",
        envelope=envelope,
    )


def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            projects = Project.objects.order_by("-created_at")[:20]
        else:
            projects = Project.objects.filter(owner=request.user).order_by("-created_at")[:20]
    else:
        projects = Project.objects.none()
    return render(request, "core/index.html", {"projects": projects})


def brand_banner(request):
    return FileResponse(open(settings.BASE_DIR / "core" / "assets" / "django-unchained-banner.png", "rb"), content_type="image/png")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            return render(request, "core/register.html", {"error": "missing fields"})
        if User.objects.filter(username=username).exists():
            return render(request, "core/register.html", {"error": "name unavailable"})
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("index")
    return render(request, "core/register.html")


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if user is None:
            return render(request, "core/login.html", {"error": "invalid login"})
        login(request, user)
        return redirect("index")
    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def project_new(request):
    if request.method == "POST":
        slug = request.POST.get("slug", "").strip().lower()
        name = request.POST.get("name", "").strip()
        if not slug or not slug.replace("-", "").isalnum() or not name:
            return render(request, "core/project_new.html", {"error": "invalid project"})
        if Project.objects.filter(slug=slug).exists():
            return render(request, "core/project_new.html", {"error": "slug unavailable"})
        project = Project.objects.create(
            owner=request.user,
            slug=slug,
            name=name,
            summary=request.POST.get("summary", ""),
        )
        DeliveryRecord.objects.create(project=project, payload=settings.FLAG)
        AssetTag.objects.bulk_create(
            [
                AssetTag(project=project, label="triage", color="blue"),
                AssetTag(project=project, label="handoff", color="gray"),
            ]
        )
        ContactCard.objects.create(
            project=project,
            display_name=f"{project.name} Desk",
            mailbox=f"{project.slug}@cat26.local",
        )
        AuditLine.objects.create(project=project, event="submission opened", reference=get_random_string(10))
        NotificationDraft.objects.create(
            project=project,
            subject=f"{project.name} launch notice",
            body="Your launch desk entry is waiting for review.",
        )
        ticket = ReviewTicket.objects.create(
            project=project,
            title=f"Initial review for {project.name}",
            preview_token=get_random_string(48),
        )
        ensure_desk_record(ticket)
        return redirect("project_detail", slug=project.slug)
    return render(request, "core/project_new.html")


@login_required
def project_detail(request, slug):
    project = visible_project_or_404(request, slug)
    tickets = project.reviewticket_set.order_by("-created_at")
    return render(request, "core/project_detail.html", {"project": project, "tickets": tickets})


@login_required
def project_vault(request, slug):
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    record = get_object_or_404(DeliveryRecord, project=project)
    if not project.approved or not record.released:
        return HttpResponseForbidden("vault sealed")
    return HttpResponse(record.payload, content_type="text/plain")


@login_required
def note_new(request):
    if request.method == "POST":
        content_type_id = request.POST.get("content_type", "")
        object_id = request.POST.get("object_id", "")
        body = request.POST.get("body", "")
        if len(body) > MAX_NOTE_BODY_LENGTH:
            return render(request, "core/note_new.html", {"error": "note too large"})
        try:
            ct = ContentType.objects.get(id=content_type_id)
            obj = ct.get_object_for_this_type(id=object_id)
        except Exception:
            return render(request, "core/note_new.html", {"error": "object unavailable"})

        if ct.model == "deliveryrecord":
            return render(request, "core/note_new.html", {"error": "object unavailable"})

        note_count = GenericNote.objects.filter(owner=request.user, content_type=ct, object_id=obj.id).count()
        if note_count >= MAX_NOTES_PER_OBJECT_PER_USER:
            return render(request, "core/note_new.html", {"error": "note limit reached"})

        GenericNote.objects.create(
            owner=request.user,
            content_type=ct,
            object_id=obj.id,
            body=body,
        )
        return redirect("index")
    return render(request, "core/note_new.html")


@login_required
def review_request(request, slug):
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    ticket = project.reviewticket_set.order_by("-created_at").first()
    if ticket is None:
        ticket = ReviewTicket.objects.create(
            project=project,
            title=f"Follow-up review for {project.name}",
            preview_token=get_random_string(48),
        )
    ensure_desk_record(ticket)
    host = request.META.get("HTTP_HOST", settings.APP_BASE_HOST)
    if host_name(host) == settings.APP_BASE_HOST:
        preview_url = f"http://{host}/review/{ticket.preview_token}/"
    elif is_project_subdomain(host):
        preview_url = f"http://{host}/subdomain/?preview={ticket.preview_token}"
    else:
        preview_url = f"http://{settings.APP_BASE_HOST}/review/{ticket.preview_token}/"
    pending_count = DeskVisit.objects.filter(project=project, claimed=False).count()
    recent_visit = DeskVisit.objects.filter(
        owner=request.user,
        created_at__gt=timezone.now() - VISIT_REQUEST_INTERVAL,
    ).exists()
    queued = False
    if pending_count < MAX_PENDING_VISITS_PER_PROJECT and not recent_visit:
        DeskVisit.objects.create(url=preview_url, project=project, owner=request.user)
        queued = True
    return render(request, "core/review_requested.html", {"ticket": ticket, "queued": queued})


@login_required
def review_preview(request, token):
    if not request.user.is_staff:
        return HttpResponseForbidden("reviewers only")
    ticket = get_object_or_404(ReviewTicket, preview_token=token)
    rendered_notes = rendered_ticket_notes(ticket, request)
    return render(
        request,
        "core/review_preview.html",
        {"ticket": ticket, "project": ticket.project, "rendered_notes": rendered_notes},
    )


@login_required
@require_POST
def review_approve(request, ticket_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("reviewers only")
    ticket = get_object_or_404(ReviewTicket, id=ticket_id)
    record = DeskRecord.objects.filter(ticket=ticket).order_by("id").first()
    if record is None or request.POST.get("reference") != record.envelope.secret.reference:
        return HttpResponseForbidden("bad reference")
    ticket.state = "approved"
    ticket.save(update_fields=["state"])
    ticket.project.approved = True
    ticket.project.save(update_fields=["approved"])
    DeliveryRecord.objects.filter(project=ticket.project).update(released=True)
    return HttpResponse("approved", content_type="text/plain")


def subdomain_landing(request):
    host = request.META.get("HTTP_HOST", "")
    if not is_project_subdomain(host):
        return HttpResponseNotFound("unknown site")
    slug = host_name(host).split(".")[0]
    project = Project.objects.filter(slug=slug).first()
    if project is None:
        return HttpResponseNotFound("unknown site")
    token = request.GET.get("preview", "")
    rendered_notes = []
    ticket = None
    if token:
        ticket = ReviewTicket.objects.filter(project=project, preview_token=token).first()
        if ticket is not None:
            rendered_notes = rendered_ticket_notes(ticket, request)
    return render(
        request,
        "core/subdomain.html",
        {"project": project, "ticket": ticket, "rendered_notes": rendered_notes},
    )


def bot_next(request):
    if request.headers.get("X-Bot-Token") != settings.BOT_TOKEN:
        return HttpResponseForbidden("no")
    visit = DeskVisit.objects.filter(claimed=False).order_by("created_at").first()
    if visit is None:
        return HttpResponse("", content_type="text/plain")
    visit.claimed = True
    visit.save(update_fields=["claimed"])
    return HttpResponse(visit.url, content_type="text/plain")


@login_required
def project_assets(request, slug):
    project = visible_project_or_404(request, slug)
    rows = AssetTag.objects.filter(project=project).order_by("label")
    return render(request, "core/decoy_list.html", {"project": project, "title": "Asset tags", "rows": rows})


@login_required
def project_contacts(request, slug):
    project = visible_project_or_404(request, slug)
    rows = ContactCard.objects.filter(project=project, public=True).order_by("display_name")
    return render(request, "core/decoy_list.html", {"project": project, "title": "Contacts", "rows": rows})


@login_required
def project_audit(request, slug):
    project = visible_project_or_404(request, slug)
    rows = AuditLine.objects.filter(project=project).order_by("-created_at")[:10]
    return render(request, "core/decoy_list.html", {"project": project, "title": "Audit", "rows": rows})


@login_required
def project_notifications(request, slug):
    project = visible_project_or_404(request, slug)
    rows = NotificationDraft.objects.filter(project=project).order_by("subject")
    return render(request, "core/decoy_list.html", {"project": project, "title": "Notifications", "rows": rows})
