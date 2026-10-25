from django import forms
from django.contrib.auth import authenticate
from PIL import Image
from .models import User, Order, Enquiry, Product, Address


class ValidatedProductImageField(forms.ImageField):
    def clean(self, data, initial=None):
        image = super().clean(data, initial)
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file must be 5 MB or smaller.')
            image.seek(0)
            with Image.open(image) as uploaded_image:
                image_format = uploaded_image.format
            image.seek(0)
            if image_format not in {'JPEG', 'PNG', 'WEBP'}:
                raise forms.ValidationError('Upload a JPEG, PNG, or WEBP image.')
        return image


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
        'placeholder': 'Create secure password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
        'placeholder': 'Confirm your password'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': 'name@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': '+1 (555) 000-0000 (Optional)'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'name@example.com',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'Enter your password',
        })
    )


class CheckoutForm(forms.Form):
    # Mortuary Destination
    mortuary_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'e.g., Graceview Memorial Sanctuary'
        })
    )
    mortuary_director = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'e.g., Director Robert Sterling'
        })
    )
    mortuary_phone = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': '+1 (555) 890-1234'
        })
    )

    # Address
    line1 = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'Street Address'
        })
    )
    line2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'Suite, bay, or receiving department'
        })
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'City'
        })
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'State / Province'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'Postal Code',
            'autocomplete': 'postal-code',
        })
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'placeholder': 'Country',
            'autocomplete': 'country-name',
        })
    )

    # Delivery & Ritual Notes
    delivery_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-2.5 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-md',
            'rows': 3,
            'placeholder': 'e.g., Deliver by 9 AM Thursday for Friday service. Loading bay B.'
        })
    )

    # Payment
    payment_method = forms.ChoiceField(
        choices=(
            ('Sandbox Card', 'Simulated Card Payment (Instant Demo)'),
            ('UPI / Bank Transfer', 'Simulated Instant Wire / Direct Transfer'),
        ),
        initial='Sandbox Card',
        widget=forms.RadioSelect(attrs={'class': 'accent-primary mr-2'})
    )

    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code']
        if (
            sum(character.isalnum() for character in postal_code) < 2
            or any(not (character.isalnum() or character in ' -') for character in postal_code)
        ):
            raise forms.ValidationError(
                'Enter a valid postal code using letters, numbers, spaces, or hyphens.'
            )
        return postal_code

    def clean(self):
        cleaned_data = super().clean()
        required_address_fields = {
            'line1': 'Enter the receiving street address.',
            'city': 'Enter the receiving city.',
            'state': 'Enter the receiving state or province.',
            'postal_code': 'Enter the receiving postal code.',
            'country': 'Enter the receiving country.',
        }

        for field, message in required_address_fields.items():
            value = cleaned_data.get(field)
            if field not in self.errors and (not value or not value.strip()):
                self.add_error(field, message)

        return cleaned_data


class ProductImageUploadForm(forms.Form):
    image_file = ValidatedProductImageField(required=False)


class UrgentEnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['name', 'email', 'phone', 'mortuary_location', 'urgency_level', 'custom_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': 'family@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': 'Primary Phone / WhatsApp'
            }),
            'mortuary_location': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'placeholder': 'Destination Mortuary or City'
            }),
            'urgency_level': forms.Select(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md cursor-pointer'
            }, choices=[
                ('<24h', 'Immediate Need — Dispatch within 24 Hours'),
                ('24-48h', 'Urgent — Required within 2 Days'),
                ('Pre-Planning', 'Compassionate Pre-Planning / Future Curation'),
            ]),
            'custom_type': forms.Select(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md cursor-pointer'
            }, choices=[
                ('Immediate Dispatch', 'Expedited Direct Mortuary Dispatch'),
                ('Custom Monogram Carving', 'Custom Monogram or Family Initial Relief'),
                ('Family Crest Carving', 'Hand-Carved Family Crest / Artisan Motif'),
                ('Hand-Carved Scripture Verse', 'Bespoke Epitaph / Scripture Verse Carving'),
                ('Bespoke Dimensions / Oversized', 'Custom Architectural Proportions / Sizing'),
            ]),
            'message': forms.Textarea(attrs={
                'class': 'w-full bg-surface-container-highest text-on-surface px-4 py-3 rounded border border-outline/20 focus:border-primary focus:outline-none font-body-md',
                'rows': 4,
                'placeholder': 'Please specify deceased or family name, planned service date, or any bespoke craftsman instructions...'
            }),
        }


class ProductForm(forms.ModelForm):
    image_file = ValidatedProductImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full text-xs text-on-surface',
            'accept': 'image/jpeg,image/png,image/webp',
        })
    )
    image_url = forms.URLField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm',
            'placeholder': 'https://...'
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'stock', 'material', 'finish',
            'fabric', 'length', 'width', 'height', 'capacity', 'sealing_system',
            'dispatch_type', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'category': forms.Select(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'price': forms.NumberInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'material': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'finish': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'fabric': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'length': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'width': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'height': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'capacity': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'sealing_system': forms.TextInput(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'dispatch_type': forms.Select(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-surface-container-highest text-on-surface px-3 py-2 rounded border border-outline/30 focus:border-primary focus:outline-none font-body-sm', 'rows': 3}),
        }
