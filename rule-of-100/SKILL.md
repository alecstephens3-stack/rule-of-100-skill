---
name: rule-of-100
description: "Run Alex Hormozi's Rule of 100 on any task the user names: 100 primary actions a day, 100 days in a row, on one thing. Helps pick which 100 using Hormozi's own order, does the actions itself every day wherever it has the tools and the user's go-ahead, keeps the count and the streak honest, and reviews each week against Hormozi's benchmarks. Open this skill FIRST, before searching files for a run, whenever someone says 'rule of 100', 'start a rule of 100 on X', '100 a day', 'today's 100', 'yesterday's 100', 'log my 100', 'I did 60 today', 'what's my streak', 'how's the rule of 100 going', 'what day are we on', or wants a daily number they are held to on outreach, content, ads or any other repeatable action, even if they don't name Hormozi. The skill knows where runs live and how the count is kept, so guessing from files gives wrong numbers. Also use for the weekly review or the day-100 report of a run. Not for a one-off batch with no daily commitment."
---

# Rule of 100

Hormozi's claim in *$100M Leads* is that the simplest way to succeed at getting customers is to take a lot of actions, and that most people take far too few. This skill makes 100 a day happen, every day, and keeps a count nobody has to trust from memory.

The task is whatever the user picks. One person's run is reaching out to 100 people about their business. Another's is 100 minutes of content. The skill is the same either way: pick the 100, do it daily, count it, review it weekly.

## The rule

Hormozi's rule is to advertise by doing 100 primary actions every day for 100 days in a row. He gives one version for each of his four ways to get leads:

| Channel | The daily 100 | Read before starting |
|---|---|---|
| Warm reach-outs (people who know you) | 100 reach-outs | `references/warm-reach-outs.md` |
| Free content | 100 minutes making it, at least one piece published | `references/content.md` |
| Cold reach-outs (strangers) | 100 reach-outs | `references/cold-reach-outs.md` |
| Paid ads | 100 minutes making ads | `references/paid-ads.md` |

You only need one of the four to get leads, so he says to pick one and max it out. After that comes more, better, new, in that order while the business is small: more volume first, then one test a week, then a new channel.

`references/the-rule.md` says exactly what is his, what is other people's version of it, and what he never addressed. Read it before explaining the rule to anyone. The channel files hold his steps, his numbers and his benchmarks. Read the one for the run's channel at setup and again at each weekly review. They are summaries and they don't replace the book.

He says nothing about days off or missed days beyond "100 days in a row". The house rules for those are below. They are this skill's, not his. Never put words in his mouth.

A run on something outside the four (job applications, practice problems, sales calls to existing leads) works the same way, but there are no Hormozi benchmarks for it. Say so, and let the user's own first two weeks become the baseline.

## Where a run lives

`rule-of-100/<slug>/` at the root of the project, one folder per run:

- `run.json`, `log.csv`, `done.csv` and `blocked.csv`: written only by the tracker, `scripts/r100.py` in this skill's folder. Its top lines list every command. Counts are facts, so the script keeps them. Never state a day number, a streak or a total from memory: run `status` in the same turn and report what it prints.
- `run.md`: the plain-words definition, the go-ahead, and the weekly notes. Template in `assets/run-template.md`.
- `done.csv` holds one row per action done: who, medium, proof such as a message id or link, and which test version they got. Write it with the tracker's `done` command, which refuses a second first contact with the same person. `check` says whether someone is new, and `block` puts a person on the never-contact list in `blocked.csv`.

To find the live run, run `list` on `rule-of-100/`. If exactly one is running, use it without asking.

## Picking the 100

If the user arrives with a task, use it. If they arrive with "I want to do the Rule of 100" and no task, help them choose with Hormozi's order, which is the order of the book: warm reach-outs, then content, then cold reach-outs, then paid ads. Each one builds the skills and the money for the next.

- New, or with few customers: warm reach-outs. Everyone has a list (phone, email, followers), it costs nothing, and it is where the first customers and the first proof come from.
- Already doing warm reach-outs: add content, built from the lessons and results of those first customers. He says to add it, not to swap.
- More money than time: cold reach-outs or paid ads. More time than money: content.
- Paid ads come after the others have paid for them.

Give one recommendation with the reason, then go with what the user decides.

## Starting a run

Aim to have the first 100 done the same day. Setup is a few minutes of definition, not a project. Settle these, proposing an answer for each from what you already know about the user's business and asking only what you can't work out:

1. **The one primary action**, in a sentence a stranger could count. "Send one personal message about our business to one person who fits, by email, text or direct message" counts. "Work on outreach" doesn't.
2. **What does not count.** Getting ready is not the action: building lists, research, writing templates, setting up tools, reading replies. Outcomes are not the action either (a reply is the result of one). Follow-ups are worth doing, and Hormozi gives a cadence for them. By default they don't count toward the 100, and the tracker counts first contacts only. If the user wants them counted, add `"count_follow_ups": true` to `run.json` and say so in `run.md`.
3. **The unit and the number.** Actions or minutes, 100 a day. If the user wants a different number, use it, and record it as their adapted number so nobody later reads it as Hormozi's.
4. **Who does the action: the skill or the person.** Default to the skill doing it. Go through the tools this session really has (email, messaging, a browser, a posting tool) and say which part of the action it can carry out end to end. What it can't do, it prepares so the person's part is one click or one paste each. Some actions are the person's by nature, such as 100 minutes of recording themselves: there the skill does the preparation and the person does the minutes.
5. **The go-ahead, once.** Doing 100 outward actions a day unattended needs the user's clear yes, given one time at setup and written into `run.md`: which action, from which account, to what kind of person, with what message pattern, up to what number a day, and any spend limit. That standing yes covers exactly what it describes for the life of the run. Anything outside it (a new account, a new kind of recipient, a new offer, a cost) is asked about first. If the user wants to approve each day's batch before it goes, record that instead and send only after each approval.
6. **Can 100 a day really happen?** Look up the current limits and rules of every platform involved (daily sends, connection or friend requests, automation terms) instead of trusting memory, and note where and when you read them. If this session can't look anything up, say so, mark the limit as unverified in `run.md`, and tell the user to check it before the first full day. An account that gets restricted ends the run, and so does a sending address that lands in spam. Start on the platform where the user has the most contacts, as Hormozi says. Only when that platform can't carry 100 a day, keep the channel and spread the action across its media, which is how he defines reach-outs (email, text, direct message, calls). If the real ceiling is under 100, say so plainly with the number and let the user choose: a lower adapted number, or more media.
7. **Where the 100 a day come from.** A reach-out run needs up to 10,000 people over 100 days. Name the source and how far it goes. If the skill can't see the list itself (phone contacts, followers), ask the user to export or paste it before day 1, because nothing can be prepared without names. Hormozi's own math for a warm list is that 1,000 contacts is ten days of work, so most warm lists run out well before day 100. Say which day that will be and what happens then: the run carries on with the same action on the next platform's list, and after that on people who don't know the user yet, which means reading `references/cold-reach-outs.md` and getting a fresh go-ahead. The clock doesn't restart. Note the change in `run.md`.
8. **The lead measure and the result.** The lead measure is the first sign it works (replies, people taking the offer). The result is what the user wants (customers). Both get logged with the tracker (`--lead`, `--result`), neither replaces the count.
9. **This week's one test.** One thing to vary (the opener, the audience, the offer). Everything else holds still, or the week teaches nothing.

Start the clock on the first day the action can really go out. If the go-ahead, the targets or a working channel is still missing, write `run.md` as a proposal, ask for what's missing, and run `init` the day it arrives. A run that starts on a day nothing can be sent opens with a missed day, and that teaches everyone the count doesn't matter.

Then run `init`, write `run.md`, set up the daily schedule (below), and go straight to today's 100.

One run at a time is the default, because the rule is "pick one". A second run at the same time is the user's call. Say once that it splits the effort, then do what they decide.

## Doing today's 100

1. Run `status`. Open with the day and what's left: "Day 12 of 100. 0 of 100 so far today."
2. Pick today's targets from the source. Run `check` on each one and skip anyone already contacted or blocked, plus anyone on a do-not-contact list the project keeps. Before a new organization or person goes on the list, search what the user already has with them (their notes, their inbox, their CRM) and read what comes back. A target the user is already talking to, or has already applied to, is not a new opportunity, and a list from a search tool or another agent is a list of claims until it has been through this.
3. Do the action, one target at a time, inside the go-ahead in `run.md` and the way the channel file describes. Record each completed action with `done` as it happens, with its proof. If the session stops halfway, the rows already written are the truth and the next session picks up from there.
4. Whatever the skill can't do itself goes in one file with one ready-to-send item per named target, grouped by medium, so the person works straight down. Never paste 100 messages into the chat. Nothing in that file is recorded as done yet. When the person says what they sent, record those targets with `done` (proof: "reported by the person"), so tomorrow's list can skip them.
5. Log the day with `log --from-done`, which counts that day's rows, and report in two or three lines: how many done, how many waiting on the person, the streak, anything that failed. Use `--source person` when the rows rest on the person's word. If nothing has been done yet, log nothing: today stays open until it ends.

Hormozi's fix for being ignored is to personalize and then give value fast, so at this volume each message still has to be true and fit its recipient. A hundred identical messages burn a hundred contacts. Use something real about the person, vary the wording, and hold the week's test variable steady across the day. Run whatever checks the project already has for outgoing copy.

Stop and tell the user, instead of pushing on, when: a platform warns, throttles or blocks; messages start bouncing or landing in spam; the targets run out; a reply shows someone should not have been contacted (`block` them); or the next action would fall outside the go-ahead. Don't pad a day with poor fits to reach 100, and never count an action that failed to send.

The project's own rules still apply and win over this skill: who owns which channel, what needs approval before spend, who must never be contacted, what may be sent without review. The law applies too. Unsolicited email, texts and calls are regulated in most places, so check what applies to the user's country and recipients before a cold run.

## Every single day

The rule only works if it happens daily without anyone remembering to start it. At setup, schedule the run with whatever is available (a cron job, a scheduled agent, a scheduling skill), at a time that suits the recipients' working hours:

- The job runs today's 100, logs it, and sends the user one short message: the count, the streak, and anything that needs them.
- It carries the same go-ahead as `run.md` and nothing wider. Give it only the tools that action needs.
- If the user's part is still open late in their day, it reminds them once.
- Every scheduled run leaves its trace in `done.csv` and the tracker. A job that ran without error but logged nothing did not do the day.

If nothing can be scheduled in this setup, say so, and make today's 100 the first thing offered whenever the user opens a session with the day still open.

## When the person reports their own count

"Done", "I did 60", "log my 100": log it in the same turn. Count from evidence where it exists (sent items, published posts) and log `--source seen`. Where it can't be seen, log their number as `--source person`. If the two disagree, give both numbers and log what was seen. Log the lead measure with `--lead` when there is one. Replies to one day's messages keep arriving for days, so add later ones to the day they belong to with `--count 0 --add --lead N`. Reply in one or two lines: "100 logged. Day 12 done, 9 in a row."

A report for a day that has already passed is fine when the work was done on that day: log it with `--date`, as the person's number. That is a late report, not a make-up.

## Missed and short days (house rules, not Hormozi's)

- A day counts for what was done on it. A day with nothing done is a missed day, and a short day is a short day. Neither is rounded up or repaired by doing 200 on another day.
- The streak resets, the 100-day clock keeps running, and the run goes on. One missed day is not a reason to restart or to quit. Say it plainly, with no lecture, and get today's 100 moving.
- Never log a day in advance.

## Weekly review

Every seventh day of the run, or on request. Short, from the tracker, `done.csv` and the real replies:

- Actions done against possible, days hit, streak.
- The lead measure and its rate per 100 actions, next to Hormozi's benchmark for the channel from its reference file. His figures are his examples, not a promise, so use them to find which step is weak (few replies, or replies that don't take the offer), not to grade the person.
- A rate from a week under about 300 actions is a small sample: say so.
- This week's test: what was varied, what happened, keep or drop.
- Next week's one test.

Then one line of judgement in Hormozi's order: more before better before new. If the days aren't being hit, the answer is volume, and no new channel is proposed until they are. When the days are being hit, ask his question: what is stopping this from being ten times the number? Add the week's notes to `run.md`.

## Status

"How's it going", "what day are we on": run `status`, answer in two or three sentences. Day, today's count, days hit, streak, lead measure.

## Day 100

Write the results report: total actions, days hit, the lead measure, the results, what the weekly tests taught, in plain numbers with their source. Recommend one of more (raise the number), better (keep testing) or new (the next channel in his order). Turn off whatever schedule was set up. The tracker marks the run finished by itself after day 100. To end a run early, use `finish` with the reason, which keeps the log.
