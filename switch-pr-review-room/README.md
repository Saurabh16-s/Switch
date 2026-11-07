# Switch PR Review Room

A small team workflow where **AI agents and a human share one chat room** and
get a code review done together, built with [Switch](https://github.com/sandbox-quantum/switch)
for the **Flip the Switch Hackathon** (WeMakeDevs, Nov 2026).

> Demo video: **<ADD LINK>**

![Demo screenshot](docs/screenshot.png)
<!-- Add a screenshot or GIF of the room and save it as docs/screenshot.png -->

## What it does

A human posts a code change in a chat room. Three agents, each with its own
job, work in the same room:

| Agent | Job | Access |
|---|---|---|
| `reviewer` | Reads the diff, ranks bugs and security risks, hands the riskiest parts to `@tester` | Read only |
| `tester` | Writes the smallest test for each risk, runs it, posts the exact output | Writes tests, asks before risky actions |
| `hunter` | Finds active, beginner-friendly GitHub repos and issues that match a stack | Read only (GitHub CLI) |

The human makes the final call: nobody approves or merges until a person
replies `approve` or `changes needed`.

### Why Switch is central

Without the shared room, the agents cannot hand work to each other or wait for
a human decision. Switch turns each chat channel into a room: a shared log of
messages, instructions and decisions that people and agents all read. In our
run the reviewer even invited the tester into the room itself.

The same agents run in **Mattermost** (local, via Docker) and **Telegram**,
because agents belong to the Switch server, not to one chat app.

## Example run

Input (the sample in `sample/transfer.py`, which is buggy on purpose):

```
@reviewer review this change and hand any risky parts to @tester
```

1. `reviewer` posts one message: SQL injection, no transaction, no amount
   validation, no balance check, and tags `@tester` with three specific tests.
2. `tester` writes `tests/test_transfer.py`, runs it, and posts the output.
   In our run the injection, rollback and negative-amount tests **failed**,
   which proves the bugs are real.
3. The human replies `changes needed: use parameterized queries, validate
   amount > 0, wrap both updates in a transaction`.

## Repository layout

```
README.md
agents/      reviewer.md, tester.md, hunter.md (description, settings, instructions)
room/        room-instructions.md
sample/      transfer.py (the deliberately buggy sample)
```

## Setup

Tested on Windows. You need Node.js, and Docker Desktop if you want Mattermost.

1. **Install Switch Console** from the Switch project and open it.
2. **Start the local server** from the setup screen. It installs PostgreSQL and
   the Switch server for you. Keep Docker Desktop running so Mattermost can be
   set up.
3. **Install OpenCode** and log in to a model provider:
   ```
   npm install -g opencode-ai
   opencode            # then /connect, or: opencode auth login
   opencode models     # note a provider/model value to use below
   ```
   Create an API key on the provider's site, paste it only into OpenCode, and
   never commit it. Restart Switch Console afterwards so it detects the login;
   OpenCode should show as Ready under Providers.
4. **Create the agents** in Switch Console (provider OpenCode). Use the
   descriptions, settings and instructions in `agents/`. The model field must
   be `provider/model`, for example a line printed by `opencode models`.
5. **Create the room** and paste `room/room-instructions.md` into its
   Instructions field. Add `reviewer` and `tester`.
6. **(Optional) Connect Telegram:**
   - Create a bot with @BotFather and save the token (shown once).
   - In BotFather turn **Group Privacy** off *before* adding the bot anywhere.
   - In Switch Console: server Home, Messaging apps, Connect, Telegram, paste
     the token and bot username.
   - Create a Telegram group, add the bot, then invite agents with
     `!invite-agent @reviewer`.
   - Link your Telegram account from the Home page (you need a Telegram
     username).
7. **(Optional) For `hunter`:** install GitHub CLI from https://cli.github.com,
   run `gh auth login`, restart Switch Console, then invite `@hunter`.
8. **Run the demo:** post the contents of `sample/transfer.py` in the room with
   `@reviewer review this change and hand any risky parts to @tester`.

In Telegram, agent names do not autocomplete: type them in full with the `@`.

## Honest limitations

- The `tester` pastes its own copy of the function into its test file, so it
  tests the snippet's logic, not a real codebase with a real database. The
  concurrency test it wrote runs on in-memory SQLite and does not exercise
  cross-process locking.
- The agents ran on free OpenCode models, which are slow (each step takes
  minutes) and weaker at code than paid models.
- `hunter` depends on the GitHub CLI being installed and logged in, and on
  GitHub search flags that can differ between `gh` versions.
- Switch Console support on Windows was rough in places (agents showed
  `Failed` after a restart until recreated; the Mattermost bridge needs Docker
  running).
- No GitHub Action yet: diffs are pasted into the room by hand.

## Security notes

- Secrets (Telegram bot token, model API keys, GitHub login) are entered only
  into BotFather, OpenCode, `gh` and Switch Console, never into this repo.
  `.gitignore` excludes `.env` files and the `.switch/` folder.
- `reviewer` and `hunter` are read-only. `tester` runs commands, so it uses
  auto mode (risky actions ask first), bypass permissions stay off, and its
  working directory is a dedicated folder.
- If a token leaks, send `/revoke` to BotFather or delete the key on the
  provider's site and replace it.

## Ideas for next steps

- A GitHub Action that posts each new pull request into the room.
- Let `tester` import the real module from a cloned repo.
- Have `hunter` hand a chosen issue to `reviewer` to draft a plan and a
  claiming comment that a human approves before anything is posted.

## License

Choose a license (for example MIT) before publishing.
