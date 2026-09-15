# Secrets for Sale

## Description

> *"In the Eastern Kingdoms, rulers pay well to hear what happens beyond their walls. A house that can bring back the right secrets will always find a place at court."*

Today, we tell the story of such a house: 0-Days, remote-access trojans, email collection, social media surveillance, stolen data, and much more, all in one place, feeding APTs and intelligence agencies end-to-end.

Early in the Year of the Dragon (February 2024), a massive leak occurred, and all internal operations went public.

**Objective:** Trace the leaks, correlate chats with attachments, link handles to names and roles, and connect project discussions to sales and purchase records to answer the 6 parts below.

> [!NOTE]
> ⚠️ Using web-based LLM is allowed **only for translation** in this challenge.

---

### Questions & Formats

#### P1: The Messenger

- **Question:** What is the email address associated with the leaker account?
- **Format:** `<full email address>`

#### P2: The Main Door

- **Question:** What room number was listed for the company's APT Defense and Research Laboratory as published on the official website?
- **Format:** `<room-number>`

#### P3: Behind the Masks

- **Question:** In the original leaked files, the CEO sent a meeting invitation to another participant in August 2020. Messages from February 2021 reveal that participant's real name and identify them as the COO. What were their chat handles and the COO's real name?
- **Format:** `CEO-handle_COO-handle_COO-real-name` (e.g., `Cipher7_NightFox_John-Smith`)

#### P4: The Nile Entry

- **Question:** One of the leaked inventories lists claimed access to organizations across multiple countries. What is the English translation of the Egyptian institution named in its sample description?
- **Format:** `Original name` (without translation or added spaces)

#### P5: Follow the Money

In spring 2021, two executives discussed splitting a project's budget among four parties. The customer insisted they act as prime contractor, while they complained about preparing acceptance paperwork.

Identify the project and correlate that discussion with its sales and purchase ledgers to recover:

1. The contract identifier printed in the customer-facing sales entry.
2. The date recorded for the Telegram-system purchase (`YYYYMMDD`).
3. The amount recorded for that Telegram-system purchase (`RMB`).

- **Format:** `sales-contract-id_telegram-purchase-in-YYYYMMDD_telegram-purchase-RMB` (e.g., `AB202104_20210618_246800`)

#### P6: The Supplier’s Inbox

In late 2021, a requester complained that he had received hardware models instead of firmware versions. Trace his request for Vietnamese telecom data to the contact who said it was unavailable.

The following month, that contact received Linux documentation. Identify the original requester’s handle, the ZIP filename used to share the documentation, and the Linux client executable’s name and exact size in bytes.

- **Format:** `requester-handle_ZIP-filename_client-filename_size-in-bytes` (e.g., `SignalFox_Documents.zip_agent.bin_1234567`)

---

### Flag Format

```
CATF{P1_P2_P3_P4_P5_P6}
```

---

## solver summary

### discovery

- **Tech Stack:**
    1. OSINT / Threat Intelligence (I-Soon / Anxun Leaks)
    2. GitHub / Leaked Archives Analysis

- **Endpoints:**
    1.
    2.

- **Vulnerabilities:**
    1.
    2.

### PoC/Exploitation

1.
2.

### flag

- `CATF{...}`
