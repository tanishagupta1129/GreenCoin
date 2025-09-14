from django import forms
from .models import SubmitProof
from django.core.exceptions import ValidationError

class SubmitProofForm(forms.ModelForm):
    class Meta:
        model = SubmitProof
        fields = [
            'activity_type',
            'proof_image',
            'description',
            'image_action',
            'image_after_planting',
        ]
        widgets = {
            'activity_type': forms.Select(attrs={'id': 'activity'}),
            'proof_image': forms.ClearableFileInput(attrs={'id': 'file'}),
            'description': forms.Textarea(attrs={'id': 'description', 'rows': 4}),
        }


    def clean_proof_image(self):
        file = self.cleaned_data.get('proof_image')
        if file:
            # Check file size (max 2MB)
            if file.size > 2 * 1024 * 1024:
                raise ValidationError("File too large. Maximum size allowed is 2MB.")

            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
            if file.content_type not in allowed_types:
                raise ValidationError("Invalid file type. Only JPEG, PNG, or PDF files are allowed.")

        return file
