const amount =
document.querySelector(
'input[name="amount"]'
);

const from =
document.querySelector(
'select[name="from_currency"]'
);

const to =
document.querySelector(
'select[name="to_currency"]'
);

const result =
document.getElementById(
'liveResult'
);

const rates={

TJS:{
USD:0.091,
EUR:0.079,
RUB:7.25,
TJS:1
},

USD:{
TJS:10.95,
EUR:0.87,
RUB:79.4,
USD:1
},

EUR:{
USD:1.14,
TJS:12.4,
RUB:90.3,
EUR:1
},

RUB:{
USD:0.0126,
EUR:0.011,
TJS:0.137,
RUB:1
}

};

function calc(){

if(!amount)return;

const val =
parseFloat(
amount.value || 0
);

const rate =
rates[
from.value
][
to.value
];

result.innerText =
(val*rate)
.toFixed(2);

}

[
amount,
from,
to

].forEach(el=>{

el.addEventListener(
'input',
calc
);

});

calc();