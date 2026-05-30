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