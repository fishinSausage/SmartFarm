const net= require('net');
const dotenv = require('dotenv');
const {dataForwarder} = require("./dataForwarder.js");

dotenv.config();

console.log("tcpServer has started...")

const server = net.createServer(async (socket) => {
    console.log(`sensor Connected: ${socket.remoteAddress}`);

    socket.on('data', async (data) => {
        const message = data.toString().trim();
        console.log(`Received: ${message}`);

        let payload;

        try {
            payload = JSON.parse(message);
        } catch (e) {
            console.error("JSON parse failed:", e.message);
            return;
        }

        await dataForwarder(payload);
    });
    socket.on('end', () => {
        console.log('sensor disconnected');
    });
});

server.listen(process.env.TCP_PORT, () => {
    console.log(`tcp server listending on port ${process.env.TCP_PORT}`);
});

function parseSensorData(raw) {
    const result ={};
    raw.split(',').forEach((pair) => {
        const [key, value] = pair.split(':');
        result[key.trim().toLowerCase()] = parseFloat(value);
    });
    //이건 json타입으로 {"Temperature" : 36.5, "humidity" : ...} 일경우 상정.
    return result;
}

module.exports = { }