import base64
import os
import tempfile
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings
from django.template.loader import render_to_string
from .models import ConsentTemplate, ConsentSubmission, Client
from .forms import ConsentFillForm

# PDF generation helper (WeasyPrint preferred). See below for installation notes.
def generate_pdf_for_submission(submission):
    """
    Generates a PDF from an HTML template and stores it on submission.pdf.
    Uses WeasyPrint if available; otherwise attempts xhtml2pdf fallback.
    """
    html = render_to_string("consents/pdf_template.html", {"submission": submission})
    # Try WeasyPrint first
    try:
        from weasyprint import HTML
        out_fd = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        HTML(string=html, base_url=settings.STATIC_ROOT or settings.BASE_DIR).write_pdf(out_fd.name)
        from django.core.files import File
        with open(out_fd.name, "rb") as f:
            submission.pdf.save(f"consent-{submission.pk}.pdf", File(f), save=True)
        os.unlink(out_fd.name)
        return True
    except Exception as e:
        # fallback to xhtml2pdf (if installed)
        try:
            from xhtml2pdf import pisa
            out_fd = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            with open(out_fd.name, 'wb') as f:
                pisa.CreatePDF(html, dest=f)
            from django.core.files import File
            with open(out_fd.name, "rb") as f:
                submission.pdf.save(f"consent-{submission.pk}.pdf", File(f), save=True)
            os.unlink(out_fd.name)
            return True
        except Exception:
            # If both fail, leave pdf empty but don't crash
            return False

def choose_template(request):
    templates = ConsentTemplate.objects.all()
    return render(request, "consents/choose_template.html", {"templates": templates})

def fill_template(request, slug):
    template = get_object_or_404(ConsentTemplate, slug=slug)

    # Optionally pre-fill client if ?client_id= is provided (you can adapt)
    client = None
    client_id = request.GET.get("client_id")
    if client_id:
        try:
            client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            client = None

    if request.method == "POST":
        form = ConsentFillForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.template = template

            # Store health answers into JSON
            submission.answers = {
                "allergies": form.cleaned_data.get("allergies"),
                "pregnancy": form.cleaned_data.get("pregnancy"),
                "medications": form.cleaned_data.get("medications"),
                "skin_conditions": form.cleaned_data.get("skin_conditions"),
            }
            if client:
                submission.client = client
            # signature handling
            sig_b64 = form.cleaned_data.get('signature_data')
            typed_sig = form.cleaned_data.get('typed_signature') or ""
            submission.typed_signature = typed_sig

            # If drawn signature provided, decode and save
            if sig_b64:
                # expected "data:image/png;base64,...."
                if ";base64," in sig_b64:
                    header, imgstr = sig_b64.split(";base64,")
                else:
                    imgstr = sig_b64
                img_data = base64.b64decode(imgstr)
                filename = f"{template.slug}-{submission.full_name.replace(' ','_')}-{int(submission.signed_at.timestamp()) if submission.signed_at else 0}.png"
                submission.signature_image.save(filename, ContentFile(img_data), save=False)

            # must set consent_given True (form enforces)
            submission.save()

            # generate PDF (best-effort) and attach
            generate_pdf_for_submission(submission)

            return redirect(reverse("consents:thank_you", args=[submission.pk]))
    else:
        initial = {}
        if client:
            initial.update({"full_name": client.full_name, "email": client.email, "phone": client.phone})
        form = ConsentFillForm(initial=initial)

    return render(request, "consents/fill_template.html", {"template": template, "form": form, "client": client})

def thank_you(request, pk):
    submission = get_object_or_404(ConsentSubmission, pk=pk)
    return render(request, "consents/thank_you.html", {"submission": submission})
