<div align="center">

# ZarinPay

**Personal banking with a dark glass interface, gold accents, and an AI that actually explains your money instead of just showing you a number.**

Accounts, transfers, loans, savings, budgets, financial goals, and a live financial-rating score, all running for real users, not seeded demo data.

[**Open zarinpay.glossa.best**](https://zarinpay.glossa.best) &nbsp;·&nbsp; [Author: Magamed-7](https://github.com/Magamed-7) &nbsp;·&nbsp; [Email](mailto:teachermaga7@gmail.com)

**[English](#english)** &nbsp;|&nbsp; **[Русский](#русский)** &nbsp;|&nbsp; **[Тоҷикӣ](#тоҷикӣ)**

</div>

---

## English

### What this actually is

ZarinPay is a full personal-finance product built on Django: multi-currency accounts (TJS, USD, RUB), transfers between your own accounts or to other users, a loan pipeline with a repayment calculator and a real payment schedule, savings accounts with simulated interest, category-based budgeting with overspend alerts, financial goals with progress tracking, and a support-ticket system. On top of all of that sits a financial rating score (Bronze / Silver / Gold / Platinum) computed from real account activity, deposit regularity, loan repayment history, and savings usage, and an AI assistant, powered by Claude, that answers real questions about your own finances instead of generic advice.

### Architecture

The whole system is one Django project, split into focused apps rather than one giant monolith:

- **`accounts`** — auth (email verification, password recovery, login history), profile, and the financial-rating engine
- **`banking`** — accounts, transfers, transaction history, PIN management
- **`loans`** — credit applications, repayment calculator, repayment schedules, savings/deposit accounts with simulated interest
- **`budget`** — category budgets with limits and overspend notifications
- **`goals`** — financial goals with progress tracking
- **`ai_assistant`** — a Claude-backed assistant scoped to the user's own financial data
- **`support`** — ticketing with status flow (pending → in progress → resolved → closed)
- **`notifications`** — in-app notification feed
- **`manager`** / **`administration`** — role-scoped staff panels on top of the same data, for loan approvals, ticket handling, and system-wide administration

Three real roles sit on top of this: a client sees only their own money, a manager reviews loan applications and support tickets, an administrator has full control including exchange rates, budget categories, and user roles.

### What I personally built

I designed and built the entire application: the Django app layout above, the financial-rating scoring algorithm, the loan and savings math, the budget and goals tracking, and the Claude-backed AI assistant integration. I also ran a security pass on this codebase and fixed a real production-hardening gap, `ALLOWED_HOSTS` was unrestricted and `DEBUG` could default to `True`, both closed and visible in the commit history.

### Running it

```bash
pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Fill in `.env` first: `SECRET_KEY`, `EMAIL_HOST*` for verification mail, and `CLAUDE_API_KEY` for the AI assistant. SQLite is the default database, no extra setup needed to run it locally.

### Contact

Looking at this for a role or a project: [github.com/Magamed-7](https://github.com/Magamed-7) · [teachermaga7@gmail.com](mailto:teachermaga7@gmail.com)

---

## Русский

### Что это

ZarinPay, это полноценный продукт для управления личными финансами на Django: мультивалютные счета (TJS, USD, RUB), переводы между своими счетами и другим пользователям, кредитный конвейер с калькулятором и реальным графиком платежей, сберегательные счета с имитацией начисления процентов, бюджетирование по категориям с уведомлениями о превышении лимита, финансовые цели с отслеживанием прогресса и система тикетов поддержки. Поверх всего этого работает финансовый рейтинг (Бронза / Серебро / Золото / Платина), который считается по реальной активности счёта, регулярности пополнений, истории погашения кредитов и использованию сбережений, а также AI-ассистент на базе Claude, отвечающий на вопросы именно о ваших финансах, а не общими советами.

### Архитектура

Вся система, это один Django-проект, разбитый на прицельные приложения, а не один гигантский монолит:

- **`accounts`** — аутентификация (подтверждение почты, восстановление пароля, история входов), профиль и движок финансового рейтинга
- **`banking`** — счета, переводы, история транзакций, управление PIN
- **`loans`** — заявки на кредит, калькулятор погашения, графики платежей, сберегательные/депозитные счета с имитацией процентов
- **`budget`** — бюджеты по категориям с лимитами и уведомлениями о превышении
- **`goals`** — финансовые цели с отслеживанием прогресса
- **`ai_assistant`** — ассистент на Claude, ограниченный данными самого пользователя
- **`support`** — тикеты со статусами (в ожидании → в работе → решено → закрыто)
- **`notifications`** — лента уведомлений внутри приложения
- **`manager`** / **`administration`** — панели для сотрудников поверх тех же данных: одобрение кредитов, обработка тикетов и администрирование системы

Поверх этого три реальные роли: клиент видит только свои деньги, менеджер обрабатывает заявки на кредит и тикеты поддержки, администратор имеет полный контроль, включая курсы валют, категории бюджета и роли пользователей.

### Что сделал лично я

Я спроектировал и построил всё приложение целиком: структуру Django-приложений выше, алгоритм расчёта финансового рейтинга, математику кредитов и сбережений, отслеживание бюджета и целей, и интеграцию AI-ассистента на Claude. Также провёл security-аудит кодовой базы и закрыл реальный пробел в продакшен-хардненинге: `ALLOWED_HOSTS` был не ограничен, а `DEBUG` мог оставаться включённым по умолчанию, оба закрыты и видны в истории коммитов.

### Запуск

```bash
pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Сначала заполните `.env`: `SECRET_KEY`, `EMAIL_HOST*` для писем подтверждения и `CLAUDE_API_KEY` для AI-ассистента. База по умолчанию SQLite, дополнительная настройка для локального запуска не нужна.

### Контакты

Если смотрите этот проект по работе или заказу: [github.com/Magamed-7](https://github.com/Magamed-7) · [teachermaga7@gmail.com](mailto:teachermaga7@gmail.com)

---

## Тоҷикӣ

### Ин чист

ZarinPay як маҳсулоти пурраи молияи шахсӣ дар асоси Django аст: ҳисобҳои бисёрарзӣ (TJS, USD, RUB), интиқол байни ҳисобҳои худ ва ба корбарони дигар, хатти қарзӣ бо калкулятори бозпардохт ва ҷадвали воқеии пардохт, ҳисобҳои пасандоз бо имитатсияи фоиз, буҷетбандӣ аз рӯи категория бо огоҳиномаи зиёдхарҷӣ, ҳадафҳои молиявӣ бо пайгирии пешрафт ва системаи тикети дастгирӣ. Дар болои ин ҳама рейтинги молиявӣ (Биринҷӣ / Нуқрагин / Тиллоӣ / Платина) кор мекунад, ки аз рӯи фаъолияти воқеии ҳисоб, мунтазамии пуркунӣ, таърихи бозпардохти қарз ва истифодаи пасандоз ҳисоб карда мешавад, инчунин ёрдамчии AI дар асоси Claude, ки ба саволҳо дар бораи маҳз молияи шумо ҷавоб медиҳад, на маслиҳати умумӣ.

### Меъморӣ

Тамоми система як лоиҳаи Django аст, ки ба барномаҳои мушаххас тақсим шудааст, на як монолити калон:

- **`accounts`** — аутентификатсия (тасдиқи почта, барқарорсозии парол, таърихи вуруд), профил ва механизми рейтинги молиявӣ
- **`banking`** — ҳисобҳо, интиқол, таърихи амалиёт, идоракунии PIN
- **`loans`** — дархости қарз, калкулятори бозпардохт, ҷадвали пардохт, ҳисобҳои пасандоз/депозит бо имитатсияи фоиз
- **`budget`** — буҷетҳо аз рӯи категория бо лимит ва огоҳинома
- **`goals`** — ҳадафҳои молиявӣ бо пайгирии пешрафт
- **`ai_assistant`** — ёрдамчӣ дар асоси Claude, маҳдуд ба маълумоти худи корбар
- **`support`** — тикетҳо бо статус (дар интизорӣ → дар кор → ҳал шуд → баста шуд)
- **`notifications`** — рӯйхати огоҳиномаҳо дар дохили барнома
- **`manager`** / **`administration`** — панелҳо барои кормандон дар болои ҳамон маълумот: тасдиқи қарзҳо, коркарди тикетҳо ва идоракунии система

Дар болои ин се нақши воқеӣ: муштарӣ танҳо пули худро мебинад, менеҷер дархости қарз ва тикети дастгириро баррасӣ мекунад, маъмур назорати пурра дорад, аз ҷумла қурби асъор, категорияи буҷет ва нақши корбарон.

### Ман шахсан чӣ сохтам

Ман тамоми барномаро тарҳрезӣ ва сохтам: сохтори барномаҳои Django дар боло, алгоритми ҳисоби рейтинги молиявӣ, математикаи қарз ва пасандоз, пайгирии буҷет ва ҳадафҳо, ва интегратсияи ёрдамчии AI дар асоси Claude. Инчунин аудити амниятӣ гузаронидам ва камбудии воқеии тайёрии продакшенро бартараф кардам: `ALLOWED_HOSTS` маҳдуд набуд ва `DEBUG` метавонист аз рӯи пешфарз фаъол монад, ҳарду ислоҳ шуданд ва дар таърихи коммитҳо намоёнанд.

### Роҳандозӣ

```bash
pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Аввал `.env`-ро пур кунед: `SECRET_KEY`, `EMAIL_HOST*` барои номаи тасдиқ ва `CLAUDE_API_KEY` барои ёрдамчии AI. Пойгоҳи додаҳо аз рӯи пешфарз SQLite аст, барои роҳандозии маҳаллӣ танзими иловагӣ лозим нест.

### Тамос

Агар ин лоиҳаро барои кор ё фармоиш дида истодаед: [github.com/Magamed-7](https://github.com/Magamed-7) · [teachermaga7@gmail.com](mailto:teachermaga7@gmail.com)
