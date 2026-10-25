# 🧛 Dracula Auth

> A free, open-source Discord bot that adds authentication to your server.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2)
![License](https://img.shields.io/badge/license-MIT-green)

Dracula Auth lets members create an account, log in, and verify their identity with a code sent by email. Once verified, they automatically receive the **Member** role.

📖 **Documentation:** https://dracula-auth-doc.netlify.app/

---

## ✨ Features

- 🔐 Account creation and login directly from Discord
- 📧 Email verification with a one-time code
- ✅ Automatic **Member** role after verification
- 🛠️ Admin panel to view and manage accounts
- ⚙️ Simple setup with a single `/setup` command
- 🆓 Free and open source (MIT)

---

## 🚀 How it works

1. A member clicks **Create account** and registers.
2. They click **Login** and receive a verification code by email.
3. They click **Verify** and enter the code.
4. If the code is valid, they get the **Member** role.

Admins can see and manage accounts from the **admin panel**.

---

## 📦 Installation

### Requirements

- Python 3.10+
- A Discord bot token ([Developer Portal](https://discord.com/developers/applications))
- An SMTP account to send emails

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/TODO/bot-auth.git
cd bot-auth

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the environment
cp .env.example .env
# then edit .env with your values

# 5. Start the bot
python main.py
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Your Discord bot token |
| `SMTP_SERVER` | SMTP server address (e.g. `smtp.gmail.com`) |
| `MAIL_PORT` | SMTP port (e.g. `587` or `465`) |
| `MAIL_USERNAME` | SMTP login |
| `MAIL_PWD` | SMTP password (use an app password if possible) |
| `MAIL_FORM` | Sender address shown in emails |

> ⚠️ **Never commit your `.env` file.** Make sure it is listed in `.gitignore`.

---

## 🧭 Usage

1. Invite the bot to your server with permissions to manage roles and send messages.
2. Make sure the bot's role is **above** the **Member** role in the role list.
3. Run `/setup` to post the authentication embed with the **Create account**, **Login** and **Verify** buttons.
4. Members can now authenticate. Admins can open the admin panel to see accounts.

---

## 📁 Project structure

```
bot-auth/
├── main.py              # Bot entry point
├── db.py                # SQLite database
├── templates/           # Email templates
├── requirements.txt
├── .env.example
├── LICENSE
└── README.md
```

---

## 🔒 Security notes

- Use an SMTP **app password**, not your main account password.
- Keep `DISCORD_TOKEN` and `MAIL_PWD` private.
- Passwords should be stored **hashed** (e.g. bcrypt or argon2), never in plain text.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the project
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Change: my feature"`
4. Push the branch: `git push origin feature/my-feature`
5. Open a pull request

---

## 👥 Credits

- **Bot** developed by PetitGameur404 ([PetitGameur404](https://lucahallet.com))
- **Documentation** written by ArthurLaffont
- Creators: PetitGameur404 & Gaja.21

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
