# 01 — What Scrooner Is and Why We Are Building It

The product thesis, customer, problem, value proposition and business
intent.

> **Status:** Canonical · **Owner:** Founder / Product · **Review:** When a core decision changes

---

## Executive definition

Scrooner is a research and fundamental stock-screening product for
US-listed companies. It lets a serious retail investor describe a
financial screen in plain English and receive deterministic, traceable
results backed by normalized company filings—not an AI-generated
opinion.

The shortest product promise is: the easiest way to screen US companies
using complex fundamental logic in plain English.

## The problem

- US company filings contain rich, authoritative data, but the raw SEC/XBRL structure is difficult for ordinary investors to use.

- Existing screeners often force users to learn field names, filters and formulas before they can express a real investment idea.

- Generic AI research products can produce fluent answers without a stable calculation trail, creating a trust problem for financial analysis.

- Serious individual investors need multi-year consistency tests—growth, returns on capital, cash generation and dilution—not just a snapshot dashboard.

- Global investors interested in US stocks face the same research problem even when they invest through different brokers.

## Who it is for

| **Audience**          | **Need**                                                                             | **Initial priority** |
|-----------------------|--------------------------------------------------------------------------------------|----------------------|
| Primary               | Serious self-directed fundamental investors researching US-listed companies.         | Highest              |
| Initial geographies   | United States and India, while remaining usable globally.                            | High                 |
| Language and currency | English interface; USD financial reporting.                                          | Locked for V1        |
| Also included         | Researchers evaluating US stocks even if they do not yet own them.                   | Included             |
| Not the target        | Day traders, options traders, passive-only investors, crypto users and institutions. | Excluded from MVP    |

## The wedge and the moat

| **Layer**         | **Role**                                                                                                                      |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Wedge             | A very simple prompt-like search experience that hides complex screening logic.                                               |
| Core engine       | Natural language is translated into a validated, deterministic financial query.                                               |
| Data moat         | SEC data is collected once, normalized consistently, mapped to canonical concepts and converted into trusted metrics.         |
| Trust moat        | Every result can be traced to definitions, periods and source filings; AI is an interface assistant, not the source of truth. |
| Distribution moat | Indexable company, screen, guide and glossary pages compound through SEO over time.                                           |

## Representative job to be done

“Find US companies below $20B market cap with revenue growing more than
15% for five years, average ROIC above 15%, positive free cash flow
every year and less than 5% share dilution.”

Scrooner should parse this request, show the interpreted conditions,
execute them against canonical metrics, return matching companies and
let the user verify why each company passed or failed.

## Why build it now

- SEC EDGAR provides a durable primary-data foundation that can be processed into a proprietary normalized dataset.

- Natural-language interfaces reduce the learning cost of advanced screening without requiring AI to invent financial facts.

- The founder has deep SEO and product experience, making programmatic company pages, screen pages and educational content a credible acquisition channel.

- A focused product can be bootstrapped: build the data asset first, expose a narrow high-value workflow, then expand only after real usage.

## Business intent

- Initial premium price hypothesis: approximately $100 per year.

- First meaningful commercial milestone: about 1,000 paid customers, roughly equivalent to $100,000 ARR before fees and discounts.

- Longer-term ambition: 5,000–10,000 paid customers, earned through a broad free audience and trusted research utility.

- Core model: free product for discovery and habit formation; premium subscription for higher limits and advanced workflows.

- Possible later revenue—not MVP commitments—includes broker affiliates, advertising and a B2B data API.

## What Scrooner will not become

Scrooner is not “another AI stock research platform.” It will not begin
as a trading terminal, news app, portfolio tracker, recommendation
engine or all-purpose finance chatbot. Its identity is narrow:
dependable US fundamental screening made dramatically easier.

## Success definition

- A user can express a meaningful multi-condition fundamental screen without learning Scrooner syntax.

- The system returns the same result for the same data and conditions.

- Metrics are accurate enough to survive manual comparison with filings and known benchmarks.

- Users understand the interpreted query and can audit the result.

- The product earns repeat usage and paid conversion before scope expands.
