# SOURCE

## Description

TREAT ALL INFO RELATED TO THIS CHALLENGE AS CONFIDENTIAL

Under a private retainership agreement, your Threat Intelligence unit provides continuous dark-web and surface-web exposure monitoring for high-net-worth clients.

During this morning's telemetry sweeps, an exposure detection alert fired: critical credentials belonging to the client surfaced in an indexed leak. Initial triage suggests this wasn't a standard database dump—it bears the signature exfiltration fingerprints of an active infostealer operation.

Your objective is to trace this exposure back to ground zero, reconstruct the attacker's exfiltration pathway, and determine the exact blast radius.

#### Target Lead

```text
nayaf625@gmail.com:xxxxxx
```

#### Incident Response Deliverables

1. **Victim Origin:** Client's public IP address at time of compromise.
2. **Breach Timestamp:** Exact time the endpoint was infected `[YYYY-MM-DD hh:mm UTC]`.
3. **Exfiltration Timestamp:** Exact time the archive was first uploaded to a file hosting service `[YYYY-MM-DD hh:mm:ss]`.
4. **Attribution:** Specific malware family responsible for harvesting the credential.
5. **C2 Infrastructure:** All primary Telegram channel/bot handles associated with the log drop `[@TGCHANNEL1:@tgchannel2]`.

#### Flag Construction

```text
CATF{<IP>_<BREACH_TIME>_<UPLOAD_TIME>_<MALWARE>_<TELEGRAM_HANDLES>}
```

*Example:* `CATF{192.0.2.1_20215-05-10 14:32_2015-02-10 11:45:02_redline_@dumpchannel:@stealerbot}`

---

---

## solver summary

### discovery

- **Tech Stack:**
    1.
    2.

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

- `CTF{...}`
