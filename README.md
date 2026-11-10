# cs85-astro-template
# CS85 astronomy teaser projects

Run your project in the cloud with Claude Code: nothing to install on your laptop. Your project number from the email matches a file in `starters/`.

## One-time setup (about 10 minutes)

1. **Make your own copy of this repo.** Click **Use this template**, then **Create a new repository** under your own GitHub account. Public is simplest.
2. **Let Claude use it.** Install the Claude GitHub App on your account at https://github.com/apps/claude/installations/new and give it access to your new repo.
3. **Connect GitHub to Claude.** Go to https://claude.ai/code, sign in with your Harvard Claude account, and follow the prompt to connect GitHub.
4. **Create the class environment.** At claude.ai/code, click the cloud icon above the message box, then **Add cloud environment**, and fill it in:
   - **Name:** `CS85 Astronomy`
   - **Network access:** **Custom**. Paste every line from `allowed_domains.txt` into **Allowed domains**, and tick **Also include default list of common package managers**.
   - **Setup script:** paste the contents of `setup_script.sh`.
   - Click **Create**.

## Each work session

At claude.ai/code, pick your repo and the **CS85 Astronomy** environment, then ask something like:

> Run starters/07_sentry_risk.py, save the plot to plots/, and explain what it shows.

Your first session takes a few extra minutes while packages install. After that, sessions start quickly.

**Seeing your plots:** Claude pushes its work to a branch. On GitHub, switch to that branch and open the `plots/` folder. GitHub shows the images right in the browser.

## If something goes wrong

- **"Claude Code isn't available on your account"** or **no GitHub sign-in button:** tell your instructor. That's an account setting, not something you did wrong.
- **A download fails with 403 or "proxy":** a site is missing from the environment's allowed domains. Claude will tell you which one; add it in the environment settings.
- **Anything else:** paste the error into the chat and ask Claude to fix it.
