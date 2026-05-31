const receiverInput =
document.querySelector(
'input[name="receiver_number"]'
);

const amountInput =
document.querySelector(
'input[name="amount"]'
);

const senderSelect =
document.querySelector(
'select[name="sender_account"]'
);

const receiverBox =
document.getElementById(
'receiverBox'
);

const balanceBox =
document.getElementById(
'balanceCheck'
);

const balances={};

document
.querySelectorAll(
'select[name="sender_account"] option'
)
.forEach(o=>{

balances[
o.value
]=parseFloat(
o.textContent.match(
/[\d.]+/
)?.[0] || 0
);

});

receiverInput.addEventListener(
'input',
()=>{

fetch(
`${window.lookupUrl}?number=${receiverInput.value}`
)

.then(r=>r.json())

.then(data=>{

receiverBox.innerText=

data.found
? `Получатель: ${data.name}`
: 'Получатель не найден';

});

});

function validate(){

const balance=
balances[
senderSelect.value
] || 0;

const amount=
parseFloat(
amountInput.value || 0
);

balanceBox.innerText=

amount>balance
? 'Недостаточно средств'
: `Баланс OK (${balance})`;

}

amountInput.addEventListener(
'input',
validate
);

senderSelect.addEventListener(
'change',
validate
);

validate();