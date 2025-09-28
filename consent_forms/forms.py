from django import forms
from .models import ConsentSubmission

class ConsentFillForm(forms.ModelForm):
    # Hidden field for base64 signature image
    signature_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    typed_signature = forms.CharField(required=False, label="Type your full name (as signature)")
    consent_given = forms.BooleanField(required=True, label="I confirm I have read and agree to the above")

    # Example health questions (Yes/No or text)
    allergies = forms.ChoiceField(
        choices=[("no", "No"), ("yes", "Yes")],
        required=True,
        label="Do you have any allergies?"
    )
    pregnancy = forms.ChoiceField(
        choices=[("no", "No"), ("yes", "Yes")],
        required=True,
        label="Are you pregnant or breastfeeding?"
    )
    medications = forms.CharField(
        required=False,
        label="List any medications you are currently taking"
    )
    skin_conditions = forms.CharField(
        required=False,
        label="Do you have any skin conditions we should know about?"
    )

    class Meta:
        model = ConsentSubmission
        fields = [
            "full_name", "email", "phone",
            "treatment_date", "treatment_type",
            "typed_signature", "consent_given"
        ]

    def clean(self):
        cleaned = super().clean()
        sig = cleaned.get("signature_data")
        typed = cleaned.get("typed_signature")
        if not sig and not typed:
            raise forms.ValidationError("Please provide either a drawn or typed signature.")
        return cleaned
