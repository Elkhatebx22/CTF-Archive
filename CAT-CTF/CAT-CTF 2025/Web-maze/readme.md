
the player should do the following:
reset admin pass via host header injection
steals the 2fa setup qr code by cache deception
get an RCE and get the flag in enc via SSTI

in cache deception make sure to set the URL in env to the public url infront of the proxy (nginx), not the internal one, because the proxy is the one chaching