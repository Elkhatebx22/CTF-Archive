const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

let mailbox = {};

app.post('/receive', (req, res) => {
  const { to, subject, body } = req.body;
  if (!to.endsWith('@catf.cat')) return res.status(403).send('Invalid email domain');
  if (!mailbox[to]) mailbox[to] = [];
  mailbox[to].push({ subject, body });
  res.sendStatus(200);
});

app.get('/inbox/:email', (req, res) => {
  const email = req.params.email;
  const messages = mailbox[email] || [];
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Inbox - ${email}</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          background-color: #f0f2f5;
          margin: 0;
          padding: 20px;
          color: #1c1e21;
        }
        .container {
          max-width: 800px;
          margin: auto;
          background-color: #ffffff;
          border: 1px solid #dddfe2;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h2 {
          color: #1877f2;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
          margin-top: 0;
        }
        .message {
          border: 1px solid #e0e0e0;
          background-color: #fafafa;
          border-radius: 5px;
          padding: 15px;
          margin-bottom: 15px;
        }
        .message-subject {
          font-size: 1.1em;
          font-weight: bold;
          color: #333;
          margin: 0 0 5px 0;
        }
        .message-body {
          margin: 0;
        }
        .no-messages {
          color: #777;
          font-style: italic;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Inbox for ${email}</h2>
        ${messages.length > 0
          ? messages.map(m => `
              <div class="message">
                <p class="message-subject">${m.subject}</p>
                <p class="message-body">${m.body}</p>
              </div>
            `).join('')
          : '<p class="no-messages">You have no messages.</p>'
        }
      </div>
    </body>
    </html>
  `);
});

app.listen(5001, () => console.log('Mail Server at http://localhost:5001'));
