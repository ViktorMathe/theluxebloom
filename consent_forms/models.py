from django.db import models
from django.utils import timezone

class ConsentTemplate(models.Model):
    """
    Reusable consent form template (HTML).
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField(help_text="HTML body of the consent form (used to display the terms)")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

class Client(models.Model):
    """
    Optional client record to pre-fill name/email across visits.
    """
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.full_name

class ConsentSubmission(models.Model):
    """
    Each time a client fills a form for a treatment, we create a submission.
    """
    template = models.ForeignKey(ConsentTemplate, on_delete=models.PROTECT, related_name="submissions")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    treatment_date = models.DateField(help_text="Date of the treatment")
    treatment_type = models.CharField(max_length=200, help_text="E.g. Lash lift, Microblading, Facial")
    answers = models.JSONField(blank=True, null=True, help_text="Optional structured answers to questions")
    signature_image = models.ImageField(upload_to='consent_signatures/', blank=True, null=True)
    typed_signature = models.CharField(max_length=255, blank=True, help_text="Client typed name for signature")
    signed_at = models.DateTimeField(default=timezone.now)
    pdf = models.FileField(upload_to='consent_pdfs/', blank=True, null=True)
    consent_given = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.full_name} — {self.template.title} ({self.treatment_date})"
