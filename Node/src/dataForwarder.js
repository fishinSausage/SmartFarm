const axios =require('axios');
const dotenv = require('dotenv');
dotenv.config();

async function dataForwarder(payload) {
    try {
        const response = await axios.post(process.env.FORWARD_URL, payload);
        console.log(`data has sent (${response.status})`);
    }
    catch(err) {
            console.error('Forwarding Failed: ', err.message);
    }

}

module.exports = { dataForwarder };