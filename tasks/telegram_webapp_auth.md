# Task: Implement Secure Telegram WebApp Authentication

## Goal

Create a working example demonstrating secure authentication of a Telegram user into a web application launched via a button in a Telegram bot. The authentication must verify the user's identity using Telegram's `WebAppInitData` mechanism.

## Reasoning

The standard and secure method for authenticating a user accessing a web application from a Telegram bot link is via the `WebAppInitData`.

1.  **Bot Setup:** The bot sends a message with a special `WebAppInfo` inline button pointing to the web application URL.
2.  **Web App Launch:** When the user clicks the button, Telegram opens the web app URL in an in-app browser and passes signed initialization data (`initData`) as a URL fragment or query parameter (`tgWebAppData`).
3.  **Frontend:** The web app's frontend JavaScript (`telegram-web-app.js`) accesses this `initData`.
4.  **Backend Verification:** The frontend sends the `initData` to the web app's backend. The backend verifies the `hash` within `initData` using the bot's token. This involves:
    *   Parsing the `initData` string.
    *   Constructing the `data-check-string` by sorting key-value pairs (excluding `hash`) alphabetically and joining them with newlines (`key=value
...`).
    *   Calculating the secret key: `HMAC-SHA256("WebAppData", bot_token)`.
    *   Calculating the expected hash: `HMAC-SHA256(secret_key, data_check_string)`.
    *   Comparing the calculated hash with the received `hash`.
5.  **Authentication:** If the hashes match, the backend trusts the user data (ID, name, etc.) contained within `initData` and can establish a session for that user.

This prevents replay attacks or users forging requests for other users, as the signature relies on the secret bot token.

## Checked Paths/Files

*   None yet.

## Implementation Steps

1.  [X] Create `tasks/telegram_webapp_auth.md`
2.  [X] Create `.env.example` (User will create `.env`)
3.  [X] Create `requirements.txt`
4.  [X] Create `bot.py`
5.  [X] Create `webapp/app.py`
6.  [X] Create `webapp/templates/index.html`
7.  [X] Create `README.md`
8.  [X] Enhance `README.md` with Mermaid diagram and Next Steps 