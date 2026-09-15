def parse_cookie_header(header: str):
    i = 0
    n = len(header)
    cookies = {}

    def skip_whitespace():
        nonlocal i
        while i < n and header[i] in ' \t':
            i += 1

    while i < n:
        skip_whitespace()
        key_start = i
        while i < n and header[i] not in ('=', ';'):
            i += 1
        key = header[key_start:i].strip()

        if i >= n or header[i] != '=':
            while i < n and header[i] != ';':
                i += 1
            if i < n and header[i] == ';':
                i += 1
            continue

        i += 1  
        skip_whitespace()
        if i < n and header[i] in ('"', "'"):
            quote_char = header[i]
            i += 1
            val = ''
            escaped = False
            while i < n:
                char = header[i]
                if escaped:
                    val += char
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == quote_char:
                    i += 1 
                    break
                else:
                    val += char
                i += 1
        else:
            val_start = i
            while i < n and header[i] != ';':
                i += 1
            val = header[val_start:i].strip()

        cookies[key] = val

        if i < n and header[i] == ';':
            i += 1
    return cookies
