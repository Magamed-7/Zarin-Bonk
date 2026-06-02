from django import forms
from banking.models import BankSettings, ExchangeRate
from loans.models import LoanProgram


class BankSettingsForm(forms.ModelForm):
    class Meta:
        model = BankSettings
        fields = [
            'daily_transfer_limit',
            'monthly_transfer_limit',
            'min_transfer_amount',
            'max_transfer_amount',
            'saving_account_interest_rate',
        ]
        widgets = {
            'daily_transfer_limit': forms.NumberInput(attrs={'step': '0.01'}),
            'monthly_transfer_limit': forms.NumberInput(attrs={'step': '0.01'}),
            'min_transfer_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'max_transfer_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'saving_account_interest_rate': forms.NumberInput(attrs={'step': '0.01'}),
        }


class ExchangeRateForm(forms.ModelForm):
    class Meta:
        model = ExchangeRate
        fields = ['from_currency', 'to_currency', 'rate']
        widgets = {
            'rate': forms.NumberInput(attrs={'step': '0.000001'}),
        }


class LoanProgramForm(forms.ModelForm):
    class Meta:
        model = LoanProgram
        fields = [
            'name', 'description',
            'min_amount', 'max_amount',
            'min_term', 'max_term',
            'interest_rate', 'is_active'
        ]
        widgets = {
            'min_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'max_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'interest_rate': forms.NumberInput(attrs={'step': '0.01'}),
        }
