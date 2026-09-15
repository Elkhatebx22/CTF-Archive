from django.urls import path

from . import views


urlpatterns = [
    path("brand/banner.png", views.brand_banner, name="brand_banner"),
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("projects/new/", views.project_new, name="project_new"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("projects/<slug:slug>/assets/", views.project_assets, name="project_assets"),
    path("projects/<slug:slug>/contacts/", views.project_contacts, name="project_contacts"),
    path("projects/<slug:slug>/audit/", views.project_audit, name="project_audit"),
    path("projects/<slug:slug>/notifications/", views.project_notifications, name="project_notifications"),
    path("projects/<slug:slug>/vault/", views.project_vault, name="project_vault"),
    path("notes/new/", views.note_new, name="note_new"),
    path("review/request/<slug:slug>/", views.review_request, name="review_request"),
    path("review/<str:token>/", views.review_preview, name="review_preview"),
    path("review/approve/<int:ticket_id>/", views.review_approve, name="review_approve"),
    path("bot/next/", views.bot_next, name="bot_next"),
    path("subdomain/", views.subdomain_landing, name="subdomain_landing"),
]
