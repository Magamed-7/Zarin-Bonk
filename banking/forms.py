from django import forms


class TopUpForm(forms.Form):

    amount = forms.DecimalField(
        min_value=1,
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(
            attrs={
                'placeholder':'Введите сумму',
                'class':'topup-input'
            }
        )
    )


class CurrencyConvertForm(forms.Form):

    CURRENCIES = [

        ('TJS','TJS'),
        ('USD','USD'),
        ('EUR','EUR'),
        ('RUB','RUB'),

    ]

    amount = forms.DecimalField(
        min_value=1
    )

    from_currency = forms.ChoiceField(
        choices=CURRENCIES
    )

    to_currency = forms.ChoiceField(
        choices=CURRENCIES
    )



class TransferForm(forms.Form):
 
    sender_account = forms.ModelChoiceField(
        queryset=None,
        empty_label=None,
    )
 
    receiver_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder':  'Номер счёта получателя',
            'autocomplete': 'off',
            'id':           'id_receiver_number',
        }),
    )
 
    amount = forms.DecimalField(
        min_value=1,
        decimal_places=2,
        max_digits=12,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.00',
            'step':        '0.01',
            'id':          'id_amount',
        }),
    )
 
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Назначение платежа (необязательно)',
            'id':          'id_description',
        }),
    )
 
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['sender_account'].queryset = (
                user.accounts.filter(is_active=True)
            )