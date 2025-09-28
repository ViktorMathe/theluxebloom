from django.contrib import admin
from django.utils.html import format_html
from .models import ConsentTemplate, ConsentSubmission, Client


@admin.register(ConsentTemplate)
class ConsentTemplateAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "created", "updated")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone")


@admin.register(ConsentSubmission)
class ConsentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "template",
        "treatment_type",
        "treatment_date",
        "created",
    )
    readonly_fields = (
        "signature_preview",
        "pdf_link",
        "answers_pretty",
        "created",
        "signed_at",
    )
    fields = (
        "template",
        "client",
        "full_name",
        "email",
        "phone",
        "treatment_date",
        "treatment_type",
        "consent_given",
        "typed_signature",
        "signature_preview",
        "answers_pretty",
        "pdf_link",
        "created",
    )

    def signature_preview(self, obj):
        if obj.signature_image:
            return format_html(
                '<img src="{}" style="max-width:300px; height:auto;"/>',
                obj.signature_image.url,
            )
        return "(no signature)"
    signature_preview.short_description = "Signature"

    def pdf_link(self, obj):
        if obj.pdf:
            return format_html(
                '<a href="{}" target="_blank">Download PDF</a>', obj.pdf.url
            )
        return "(no PDF)"
    pdf_link.short_description = "PDF"

    def answers_pretty(self, obj):
        """Show health question answers nicely formatted."""
        if not obj.answers:
            return "(no health answers)"
        return format_html(
            "<ul>{}</ul>",
            "".join(
                f"<li><b>{k.replace('_',' ').title()}:</b> {v}</li>"
                for k, v in obj.answers.items()
            ),
        )
    answers_pretty.short_description = "Health Answers"
