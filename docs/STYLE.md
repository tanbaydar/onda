[Onda](../README.md) / [Documentation](README.md) / Writing standard

# Writing standard

> **For** people who write or review these pages. **Read time** 4 minutes.

These pages follow the writing rules of ASD-STE100 Simplified Technical English, Issue 9.
The aerospace industry made this standard for maintenance manuals.
A reader with limited English must do the task correctly the first time.
The same properties help an engineer who reads fast.

## In brief

- A sentence is short. An instruction has a maximum of 20 words. A description has a maximum of 25 words.
- A word has one meaning. A thing has one name.
- Verbs are in the active voice and in simple tenses.
- A script measures the rules that a program can measure. CI runs the script on each change to a page.

## Rules from ASD-STE100

| Rule | Number | Who does the check |
|---|---|---|
| Use approved words, technical nouns and technical verbs | 1.1 | Script (word list), then the writer |
| Use one technical noun for one thing | 1.11 | [Glossary](GLOSSARY.md), then the writer |
| Use American English spelling | 1.14 | Script |
| Write a maximum of three nouns in a multi-word noun | 2.1 | Writer |
| Use the infinitive, the imperative, the simple tenses, and the past participle as an adjective | 3.2 | Script |
| Use the "-ing" form only as a technical noun | 3.5 | Script |
| Use the active voice. Use the passive voice only when the agent is not known | 3.6 | Script shows each candidate. The writer makes the decision |
| Do not use contractions. Do not omit words | 4.2 | Script (contractions) |
| Use a vertical list for complex text | 4.3 | Writer |
| Write a maximum of 20 words in an instruction | 5.1 | Script |
| Write one instruction in each sentence | 5.2 | Writer |
| Write instructions in the imperative form | 5.3 | Writer |
| Write a maximum of 25 words in a descriptive sentence | Section 6 | Script |
| Write a maximum of 6 sentences in a paragraph | Section 6 | Script |
| Do not use the semicolon | 8.1 | Script |
| Do not use Latin abbreviations | GR-6 | Script |

## Project rules

ASD-STE100 tells each project to use the standard together with a style guide.
These rules are the style guide for this repository.

- **One page, one job.** A page explains, or gives reference data, or gives a procedure.
- **Start with the reader.** Each page gives its reader, its read time, and a section "In brief".
- **Give the source of each number.** A number links to a test, a file, or a command.
- **Use "I" in decision records.** One engineer made each decision.
- **Keep product labels as the app shows them.** For example: "Been", "Will Be There", "Favourites".
- **Keep code names in code font.** For example: `DIARY_ENTRY`, `save_rating`, `409`.
- **Write dates as year, month, day.** For example: 2026-11-27.
- **Do not use dashes in a sentence.** Use a comma, a full stop, or parentheses.
- **Give each figure a text alternative.** Build each figure with the script in `docs/tools`.
- **Keep legal text as it is.** The standard does not apply to a copyright notice. Two comment lines turn the check off and on for such text.

## Technical nouns and technical verbs

ASD-STE100 lets a project add the nouns and the verbs of its subject field (rules 1.5 and 1.12).
The [glossary](GLOSSARY.md) contains the technical nouns of this project.
These are the technical verbs.

| Field | Technical verbs |
|---|---|
| Data | archive, commit, create, delete, fetch, filter, index, lock, migrate, parse, query, reconcile, replay, roll back, save, serialize, sort, store, update, validate |
| Network and operations | authenticate, back up, build, deploy, expire, fail, log in, log out, redirect, register, restore, retry, return, run, upload |
| Product | approve, decline, follow, hide, like, rate, reject, review |

## How to do the check

1. Open a terminal in the repository root.
2. Run the check on all pages.

   ```bash
   python3 docs/tools/check_docs.py
   ```

3. Correct each line that starts with `error`.
4. Read each line that starts with `note`. Change the sentence if the agent is known.
5. Build the figures again if you changed `docs/tools/figures.py`.

   ```bash
   pip install fonttools brotli uharfbuzz
   python3 docs/tools/figures.py
   ```

Python 3.10 or later is necessary for the check. No other package is necessary.

## Limits of the check

- The script does not contain the ASD-STE100 dictionary, because ASD owns the copyright of the dictionary. The script contains this project's list of words that are frequent in software text and are not approved.
- The writer applies the other parts of the dictionary by hand. Thus an error in word selection is possible.
- A program cannot know if a passive sentence has a known agent. A person makes that decision.
- This project has no connection with ASD. ASD does not approve or certify the script or these pages.

## Credits

The figures and the video use the typefaces of the product: Rozha One, General Sans and Gambetta.
Indian Type Foundry owns the copyrights and the trademarks of these typefaces.
