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