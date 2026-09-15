# DNS Frenzy

- **Author:** p._.k
- **Category:** Web
- **Solves:** 19
- **Connection:** `http://34.134.162.213:17004`

## Description

1.1.1.1? 8.8.8.8? Nah, I built my own custom DNS resolver with internal subdomains! Port Mappings: 17004 -> 5335 and 17014 -> 53535 Author: p._.k <http://34.134.162.213:17004> [DNSFrenzy.zip](<https://ctf.l3ak.team/files/9ad9e80c6c9e36c3e8d394384a7f8a7a/DNSFrenzy.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjg3fQ.aHLmVA.xeuRSY-_div8ARQTFGPoU_N0t18>)
DNSFrenzy.zip

---

### Solution

The goal is to somehow cache your internal domain to resolve to `127.0.0.1`. However, the resolver explicitly ensures that this does not happen.

There are numerous issues with the resolver to allow for the intended exploit chain to occur. The most outstanding issue is that the resolver doesn't verify the sender of the response to its DNS query. This means that if we are able to respond faster than the intended server, we should be able to redirect the resolver towards our own DNS server to carry out the rest of the query. This seems to be the case as well since there is a `time.sleep(1)` before sending the DNS request to the actual server.

The resolver does check if the TXID of the response is the same as that of the request. In most cases, this would cause issues with the exploit mentioned above. However, the TXID is generated in a predictable and reproducable way.

We now have a race condition + weak TXID generation. In order to obtain the flag, we need to take over the DNS request/response chain and provide our internal domain to be cached.

```py
self.update_cache(query.questions[0].qname, final_ip)
```

This particular line after the resolution is what allows us to cache our internal domain. Looking at the `resolve_next_hop` function, the code appears to be setting the qname to whatever the response has. Since we control the response, we should be able to change this value to our internal domain.

After the internal domain is cached, make a DNS request for that same domain and you will get the flag.
