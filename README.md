# Rule of 100, as a Claude Code skill

Alex Hormozi's Rule of 100, from *$100M Leads*: do 100 primary actions every day, for 100 days in a row, on one way of getting customers. 100 reach-outs, or 100 minutes making content, or 100 minutes making ads.

The rule is easy to state and hard to keep. This skill is for keeping it. You tell Claude the task. It sets up the run, does the day's 100 itself where it has the tools and your go-ahead, keeps the count with a script instead of from memory, and reviews the week against the benchmarks Hormozi gives in the book.

It works for whatever task you choose. Mine would be reaching out to 100 people a day about my business. Yours might be 100 minutes of content, or 100 follow-ups.

## What it does

| Step | What happens |
|---|---|
| Pick the 100 | If you don't have a task yet, it uses the order of the book: warm reach-outs first, then content, then cold reach-outs, then paid ads. |
| Define the action | One sentence a stranger could count, plus a written list of what doesn't count. Building a list is not a reach-out. |
| Your go-ahead, once | Which action, from which account, to what kind of person, up to how many a day. Inside that, it works without asking again. Outside it, it asks first. |
| Check that 100 a day can happen | Where the session can search the web, it looks up the current limits and rules of the platforms involved before the first day, and says so when it can't. Some won't carry 100 a day from one account, and some ban automated sending. When that's the case it tells you the real number and your options. |
| Do the day's 100 | With email or messaging tools connected, it sends. Where it can't act for you, it prepares everything so your part is one click or one paste per item. For content, it has the day's topics and hooks ready so your 100 minutes go to making. |
| Every day | If your setup can run scheduled jobs, it sets one up and sends you one short message a day with the count and the streak. If it can't, it tells you, and offers the day's 100 whenever you open a session. |
| Count | A script keeps the count and a record of who was contacted, and refuses a second first message to the same person. A day is hit, short or missed. Doing 240 tomorrow doesn't repair a missed day. Each day is marked as seen by the skill or reported by you. |
| Review each week | Actions done, the reply rate next to Hormozi's benchmark for that channel, what this week's one test showed, and next week's test. Then a call in his order: more, then better, then new. |

## What's in it from the book

The skill carries a short summary of Hormozi's method for each of the four channels: his steps, his follow-up cadence, and his benchmarks. The summaries were made from transcripts of him reading the book on his podcast, not from the printed book, and transcripts can be wrong. For example, for warm reach-outs he says 100 a day should get about 20 replies, about 4 people taking a free offer, and about 1 paying customer later. The weekly review uses figures like that to show which step is weak.

`rule-of-100/references/the-rule.md` lists the sources and separates three things: what he says, what other people commonly attribute to him, and what he never addresses. He says nothing about missed days, for instance, so the rules for those are this skill's own and are labelled that way.

The summaries are short and they don't replace the book. Read the book.

## Install

You need [Claude Code](https://claude.com/claude-code) and Python 3.9 or newer. The tracker uses only the standard library.

For every project on your machine:

```
git clone https://github.com/alecstephens3-stack/rule-of-100-skill.git
cp -R rule-of-100-skill/rule-of-100 ~/.claude/skills/
```

For one project only, copy the folder into that project's `.claude/skills/` instead.

Start a new Claude Code session afterwards so it picks the skill up.

## Use

Say what you want in plain words:

- "Start a rule of 100 on warm reach-outs for my business."
- "I want to do the rule of 100 but I don't know which channel."
- "Run today's 100."
- "I did 60 today, log it."
- "How's the rule of 100 going?"
- "Weekly review."

Each run gets a folder named `rule-of-100/<name>/` in the project you're working in. It holds the run's definition and your go-ahead in plain words, a log with one row per day, a record of each person contacted, and a list of people never to contact again.

## The tracker by itself

The script works without Claude if you only want the counting. From the cloned folder:

```
python3 rule-of-100/scripts/r100.py init   runs/outreach --action "warm reach-outs" --unit actions
python3 rule-of-100/scripts/r100.py done   runs/outreach --who "Sam Lee" --medium text
python3 rule-of-100/scripts/r100.py log    runs/outreach --count 100 --lead 3
python3 rule-of-100/scripts/r100.py status runs/outreach
```

After a week, `status` prints something like this:

```
outreach: warm reach-outs
Day 7 of 100 (2026-11-05 to 2027-02-12), running, 93 days left.
Today: 100 of 100 actions, 0 to go.
Days hit: 5. Short: 1. Missed: 1.
Streak: 1 now, 2 longest.
Total: 545 of 700 possible so far. Lead measure: 5. Results: 0.
Days reported by the person, not seen: 2.
Short or missed: 2026-11-07, 2026-11-10
```

Days are counted on your computer's clock. Set `R100_TZ` (for example `America/Chicago`) to count them in another time zone.

Tests: `python3 -m unittest discover tests`

## Before you point it at strangers

Sending 100 messages a day has consequences. Platforms restrict accounts that break their rules, new email addresses that send in bulk land in spam, and unsolicited email, texts and calls are regulated in most countries. The skill looks these up and tells you what it found, but the account, the reputation and the legal responsibility are yours. Start with people who know you. That is also where Hormozi says to start.

## Not affiliated

This is an independent project. It is not affiliated with or endorsed by Alex Hormozi or Acquisition.com. The Rule of 100 and the methods summarized here are his, from *$100M Leads*.

## License

MIT
