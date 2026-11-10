# CS85 astronomy teaser project

The person you're working with is an undergraduate who is new to coding. They're doing a one-week project: plan Tuesday, build Tuesday to Thursday, and demo a prototype Thursday. Explain what you're doing in plain language and keep the code readable.

## Where things are

- `starters/NN_*.py`: one starter script per project. NN matches the project number in the course email. Each script downloads a small public dataset and saves one plot.
- `plots/`: save every figure here as a PNG.
- `data/`: put downloaded data here. It's git-ignored, so large files never get committed.
- `run_all_starters.py`: a test runner that checks the starters still work.

## How to work

1. Start by running the student's starter script unchanged, so they get a real first plot quickly.
2. Make every figure with code: matplotlib, or plotly for interactive work. Never invent or simulate data and present it as real. If a download fails, say so and show the error.
3. Save each figure to `plots/` with a descriptive name. Commit the code and the plots, then push, so the student can open them on GitHub. GitHub shows PNG images in the browser.
4. At the end of each task, list the plot files you made with their GitHub links, and explain in 2 to 4 sentences what each one shows.
5. Keep downloads small, preferably under 200 MB. Cache them in `data/` so they're only downloaded once.
6. Cite the data source in the notebook, README, or slides you help the student make.

## Network

This cloud environment only allows the data sites listed in `allowed_domains.txt`, plus the standard package registries and GitHub. If a request fails with a 403 or a proxy error, don't try to get around it. Tell the student which domain to add under the environment's "Allowed domains" setting at claude.ai/code. If an API's address or fields seem to have changed, check the service's current documentation and fix the call.

## Free sign-ups

Project 02 needs a free AAVSO API token in the `AAVSO_TOKEN` environment variable. If the student wants it, they should add it to their own personal cloud environment, never to a shared one, and never commit it.
