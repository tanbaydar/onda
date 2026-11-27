[Onda](../README.md) / Documentation

# Documentation

> **Start here.** Find the row that describes you.

## Find your page

| You are | You want to know | Read | Time |
|---|---|---|---|
| All readers | What Onda is, and the reason for each product rule | [Product](PRODUCT.md) | 4 minutes |
| An engineer | How one request goes through the system | [How Onda works](ARCHITECTURE.md) | 9 minutes |
| An engineer | Why the design is this design, and its cost | [Decisions](DECISIONS.md) | 12 minutes |
| An engineer | How Onda trusts data from an external source | [Ingestion](INGESTION.md) | 8 minutes |
| An engineer | How the feed query operates, and its limit | [Home feed](HOME_FEED.md) | 7 minutes |
| An engineer who calls the API | The contract of each route | [API reference](API.md) | Lookup |
| An engineer who reads or writes data | Tables, constraints, safe entry points | [Database reference](DATABASE.md) | Lookup |
| An engineer who runs the code | Local setup, checks, where code goes | [Development](DEVELOPMENT.md) | 15 minutes |
| The operator | How to deploy, back up and restore | [Operations](../infrastructure/README.md) | Procedures |

A [video of 2 minutes 45 seconds](assets/video/onda-how-it-works.mp4) shows the same system in six chapters.

## One page, one job

| Type of page | Its job | Pages |
|---|---|---|
| Explanation | It tells how and why | Product, How Onda works, Decisions, Ingestion, Home feed |
| Reference | It gives facts for a lookup | API reference, Database reference, [Glossary](GLOSSARY.md) |
| Procedure | It gives the steps of a task | Development, Operations |
| Standard | It gives the rules for a writer | [Writing standard](STYLE.md) |

## How these pages are written

- The pages follow the writing rules of ASD-STE100 Simplified Technical English. A sentence is short, a word has one meaning, and the voice is active.
- A script checks the rules that a program can measure, and each link. CI runs it on each change.
- Each number has a source: a test, a file or a command.
- I compared each page with the code on 2026-11-27.

## More material

| Material | Contents |
|---|---|
| [Design contract](../frontend/DESIGN_CONTRACT.md) | The rules of the user interface, and the audit of 2026-08-27 |
| [Benchmark](../benchmarks/home-feed/README.md) | The procedure and the records for the Home feed measurement |
| [Video source](video/README.md) | The script and the scenes of the video |
| [Security policy](../.github/SECURITY.md) | How to report a vulnerability |
