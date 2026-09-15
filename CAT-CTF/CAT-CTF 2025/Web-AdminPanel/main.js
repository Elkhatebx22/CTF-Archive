const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const fs = require('fs');
const crypto = require('crypto');
const { SignJWT, jwtVerify, importPKCS8, importSPKI, exportJWK, importJWK } = require('jose');

const app = express();
const FLAG = process.env.FLAG || 'CATF{F1nD1ng_tHe_trUth_1n_th3_weB}';

const privatePem = fs.readFileSync('./private.pem', 'utf8');
const publicPem = fs.readFileSync('./public.pem', 'utf8');

const ADMIN_PASSWORD = crypto.randomInt(100000, 999999).toString();
console.log(`[+] Admin password: ${ADMIN_PASSWORD}`);

let publicJWK;

(async () => {
    const pubKey = await importSPKI(publicPem, 'RS256');
    publicJWK = await exportJWK(pubKey);
    publicJWK.kid = 'rsa-key-1';
    publicJWK.use = 'sig';
    publicJWK.alg = 'RS256';
})();

app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());

app.get('/jkus.json', (req, res) => {
    return res.json({ keys: [publicJWK] });
});

app.get('/', (req, res) => {
    res.send(`
        <html>
        <head>
            <title>Secure Admin Login</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f2f2f2;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .login-box {
                    background: white;
                    padding: 30px 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    width: 300px;
                }
                .login-box h2 {
                    margin-bottom: 20px;
                    text-align: center;
                }
                input {
                    width: 100%;
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }
                button {
                    width: 100%;
                    padding: 10px;
                    background: #007BFF;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>Admin Login</h2>
                <form method="POST" action="/login">
                    <input name="username" placeholder="admin" required>
                    <input name="password" placeholder="password" type="password" required>
                    <button>Login</button>
                </form>
            </div>
        </body>
        </html>
    `);
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    if (username === 'admin' && password === ADMIN_PASSWORD) {
        const privateKey = await importPKCS8(privatePem, 'RS256');

        const token = await new SignJWT({ username: 'admin' })
            .setProtectedHeader({
                alg: 'RS256',
                kid: 'rsa-key-1',
                jku: `http://${req.headers.host}/jkus.json`
            })
            .setIssuedAt()
            .setExpirationTime('1h')
            .sign(privateKey);

        res.cookie('token', token, {
            httpOnly: true,
            secure: false, 
            sameSite: 'Strict',
            maxAge: 60 * 60 * 1000
        });

        return res.redirect('/flag');
    } else {
        res.send('❌ Invalid credentials');
    }
});

app.get('/flag', async (req, res) => {
    const token = req.cookies.token;
    if (!token) return res.redirect('/');

    try {
        const header = JSON.parse(Buffer.from(token.split('.')[0], 'base64url').toString());
        const kid = header.kid;

        const response = await fetch(`http://${req.headers.host}/jkus.json`);
        if (!response.ok) throw new Error('Unable to fetch jku');
        const { keys } = await response.json();

        const jwk = keys.find(k => k.kid === kid);
        if (!jwk) throw new Error('No matching kid in JKU');
        const publicKey = await importJWK(jwk, 'RS256');
        const { payload } = await jwtVerify(token, publicKey);

        if (payload.username === 'admin') {
            return res.send(`
                <html>
                <head><title>Flag</title></head>
                <body style="font-family:sans-serif;text-align:center;margin-top:10%">
                    <h1>🏁 Flag</h1>
                    <p><b>${FLAG}</b></p>
                    <a href="/">🔒 Logout</a>
                </body>
                </html>
            `);
        }

        return res.redirect('/');
    } catch (err) {
        console.error('JWT verify error:', err.message);
        return res.redirect('/');
    }
});

app.listen(3000, () => console.log('http://localhost:3000'));
