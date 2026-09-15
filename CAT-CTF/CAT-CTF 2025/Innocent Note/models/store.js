const users = {
    'admin': {
        username: 'admin',
        password: process.env.ADMIN_PASSWORD,
        role: 'admin'
    }
};

const notes = {
    'admin': []
};

const sessions = {};

const feedback = []; 

module.exports = {
    users,
    notes,
    sessions,
    feedback 
};