from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, LecturerProfile

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    department = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science, MCA, BCA'}))
    batch = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024, Batch-A'}))
    roll_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'department', 'batch', 'roll_number']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = None
        self.fields['username'].validators = []  # Remove all default validators
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].help_text = 'Minimum 8 characters'
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].help_text = 'Enter the same password again'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Only check if username already exists
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department'),
                batch=self.cleaned_data.get('batch'),
                roll_number=self.cleaned_data.get('roll_number')
            )
        return user

class LecturerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science'}))
    designation = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Professor, Assistant Professor'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'department', 'designation']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = None
        self.fields['username'].validators = []  # Remove all default validators
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].help_text = 'Minimum 8 characters'
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].help_text = 'Enter the same password again'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Only check if username already exists
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'lecturer'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            LecturerProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department'),
                designation=self.cleaned_data.get('designation')
            )
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

class LecturerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = LecturerProfile
        fields = ['department', 'designation', 'subjects']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'subjects': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Enter subjects you teach (comma-separated)\ne.g., Data Structures, Database Management'
            }),
        }
        help_texts = {
            'subjects': 'List all subjects you teach, separated by commas'
        }

class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['department', 'batch', 'roll_number']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'batch': forms.TextInput(attrs={'class': 'form-control'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
