# RDT Inc. Fleet Management App
### Setup Guide for First-Time Users

---

## What This App Does

This is a **web app** that runs in your browser (like a website). It lets:
- **Managers** see all trucks, track maintenance, view incidents, and chat with an AI assistant
- **Drivers** log their mileage and report incidents from their phone

No App Store download needed. Works on phones, tablets, and computers.

---

## What You Need Before Starting

You need **3 things** installed on your computer:

1. **Python 3** — [python.org/downloads](https://www.python.org/downloads/) → click the big yellow "Download" button → install it
2. **Node.js** — [nodejs.org](https://nodejs.org/) → click "LTS" (the recommended version) → install it
3. **A terminal** — On Mac: press `Command + Space`, type "Terminal", press Enter. On Windows: press the Windows key, type "cmd", press Enter.

> After installing Python and Node.js, **close and reopen your terminal** before continuing.

---

## Step 1 — Get an AI Key (Free)

The app uses an AI assistant. You need a free key to activate it.

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create a free account
3. Click **API Keys** in the left sidebar
4. Click **Create Key** → give it any name → click Create
5. Copy the key — it starts with `sk-ant-...`
6. **Keep it somewhere safe** — you'll need it in Step 3

---

## Step 2 — Open the App Folder in Your Terminal

In your terminal, type this and press Enter:

```
cd "/Users/soniangilau/trash company/app/backend"
```

> You can copy-paste this exactly. The quotes are needed because there's a space in "trash company".

---

## Step 3 — Create Your Settings File

This file holds your secret keys. The app won't start without it.

In your terminal, run this command:

```
touch .env
open .env
```

This opens a blank file. Paste in the following (replace the parts in brackets):

```
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
JWT_SECRET_KEY=my-fleet-app-secret-key-2024
```

- Replace `sk-ant-YOUR-KEY-HERE` with the key you copied in Step 1
- The `JWT_SECRET_KEY` can be anything — the line above is fine as-is
- Save the file (`Command + S` on Mac, `Ctrl + S` on Windows)

---

## Step 4 — Install Backend (One Time Only)

In your terminal, run:

```
pip3 install -r requirements.txt
```

This downloads all the code the app needs to run. It may take 1–2 minutes. You'll see a lot of text scroll by — that's normal.
---

## Step 5 — Start the Backend

In your terminal, run:

```
uvicorn main:app --reload --port 8000
```

You should see something like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Leave this terminal window open.** The backend needs to keep running.

---

## Step 6 — Start the Frontend (Open a Second Terminal)

Open a **new terminal window** (don't close the first one).

In the new terminal, run these **one at a time**:

```
cd "/Users/soniangilau/trash company/app/frontend"
```

```
npm install
```

```
npm run dev
```

You should see:

```
  VITE v5.x.x  ready in 500ms
  ➜  Local: http://localhost:5173/
```

---

## Step 7 — Open the App

Open your web browser and go to:

**[http://localhost:5173](http://localhost:5173)**

You should see the RDT Inc. login screen.

---

## Logging In

| Who | Username | Password |
|---|---|---|
| Manager | `manager` | `FleetManager2024!` |
| Driver 1 | `jcooper` | `Driver2024!` |
| Driver 2 | `mrodriguez` | `Driver2024!` |
| Driver 3 | `dtorres` | `Driver2024!` |
| Driver 4 | `cmendez` | `Driver2024!` |
| Driver 5 | `bwalsh` | `Driver2024!` |

Log in as **manager** first to see the full dashboard.

---

## What's Already in the App (Demo Data)

When you first start the backend, it automatically fills the app with realistic demo data:

- **10 trucks** (T-01 through T-10)
- **T-01, T-03, T-05** — show up red (overdue maintenance)
- **T-02, T-07, T-09** — show up yellow (maintenance coming up soon)
- **T-06, T-10** — show up green (all good)
- **6 incidents** already reported
- **5 driver accounts** ready to log in

This is designed to immediately show all the features when you demo it.

---

## How to Stop the App

In each terminal window, press `Control + C` to stop it.

To start it again next time, just repeat **Steps 5 and 6** (you don't need to redo Steps 1–4).

---

## Troubleshooting

**"command not found: pip3"** — Python isn't installed yet. Go back to Step 0 and install it.

**"command not found: npm"** — Node.js isn't installed yet. Install it from nodejs.org.

**The page says "Cannot connect to server"** — The backend (Step 5) isn't running. Open a terminal and start it again.

**The AI assistant says "couldn't reach the AI"** — Your `.env` file is missing or the API key is wrong. Check Step 3.

**Anything else** — Close both terminals, open fresh ones, and start from Step 2.

---

## Adding New Driver Accounts

1. Log in as manager
2. Click **Drivers & Users** in the sidebar
3. Click **+ Add Driver**
4. Type a username and password
5. Share those credentials with the driver — they log in at the same website

---

*Built for RDT Inc. | Vernal, UT*
