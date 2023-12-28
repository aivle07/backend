from django import forms
from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm

class MyCustomSignupForm(SignupForm):
    agree_terms = forms.BooleanField(label='서비스 이용약관 및 개인정보방침 동의')
    agree_marketing = forms.BooleanField(label='마케팅 이용 동의')
    
    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = '아이디를 입력해주세요.'
        self.fields['email'].widget.attrs['placeholder'] = '이메일을 입력해주세요.'
        self.fields['password1'].widget.attrs['placeholder'] = '비밀번호를 입력해주세요.'
        self.fields['password2'].widget.attrs['placeholder'] = '비밀번호를 한번 더 입력해주세요.'
        
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['agree_terms'].widget.attrs['class'] = 'form-check-input'
        self.fields['agree_marketing'].widget.attrs['class'] = 'form-check-input'
            
    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        user.agree_terms = self.cleaned_data['agree_terms']
        user.agree_marketing = self.cleaned_data['agree_marketing']
        user.save()
        return user
    

class MyCustomSocialSignupForm(SocialSignupForm):
    agree_terms = forms.BooleanField(label='서비스 이용약관 및 개인정보방침 동의')
    agree_marketing = forms.BooleanField(label='마케팅 이용 동의')
    
    def __init__(self, *args, **kwargs):
        super(MyCustomSocialSignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = '아이디를 입력해주세요.'
        self.fields['email'].widget.attrs['placeholder'] = '이메일을 입력해주세요.'
        
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['agree_terms'].widget.attrs['class'] = 'form-check-input'
        self.fields['agree_marketing'].widget.attrs['class'] = 'form-check-input'
    
    def save(self, request):
        user = super(MyCustomSocialSignupForm, self).save(request)

        # Add your own processing here.
        user.agree_terms = self.cleaned_data['agree_terms']
        user.agree_marketing = self.cleaned_data['agree_marketing']
        user.save()
        return user