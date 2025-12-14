// server.js
const net = require('net');
const express = require("express");
const axios = require("axios");
const dotenv = require('dotenv');
dotenv.config();

const PORT_TCP = 5002;   // TCP 드론
const PORT_HTTP = 3000;  // HTTP Express

let droneSocket = null;


/* ------------------------------------------------------------
    TCP 서버 (드론 연결)
------------------------------------------------------------ */
const tcpServer = net.createServer((socket) => {
    console.log("drone connected:", socket.remoteAddress);
    droneSocket = socket;

    socket.on('data', (data) => {
        const messages = data.toString().trim().split("\n");

        messages.forEach(msgStr => {
            try {
                const json = JSON.parse(msgStr);
                console.log("response from drone:", json);

                json.status = "IDLE";
                sendToServer(json);
            } catch (e) {
                console.log("message Failed:", msgStr);
            }
        });
    });

    socket.on('close', () => {
        console.log("drone connection End");
        notifyDisconnect();
        droneSocket = null;
    });

    socket.on('error', (err) => {
        console.error("Socket ERROR:", err);
        notifyDisconnect();
        droneSocket = null;
    });
});

tcpServer.listen(PORT_TCP, () => {
    console.log(`🚁 TCP server is running on port: ${PORT_TCP}`);
});


/* ------------------------------------------------------------
    드론에 데이터 전송 함수
------------------------------------------------------------ */
function sendToDrone(jsonObj) {
    if (!droneSocket) {
        console.log("❌ No drone connection. Cannot send.");
        return false;
    }
    try {
        droneSocket.write(JSON.stringify(jsonObj) + "\n");
        console.log("Server -> drone:", jsonObj);
        return true;
    } catch (err) {
        console.error("server to drone failed:", err);
        return false;
    }
}


/* ------------------------------------------------------------
    서버로 전송 (Spring 서버로 forwarding)
------------------------------------------------------------ */
async function sendToServer(jsonObj) {
    try {
        const response = await axios.post(process.env.DRONE_FORWARD_URL, jsonObj);
        console.log(`data has sent (${response.status})`);
    }
    catch(err) {
        console.error('Forwarding Failed:', err.message);
    }
}


/* ------------------------------------------------------------
    드론 연결 끊김 처리
------------------------------------------------------------ */
function notifyDisconnect() {
    const data = {
        timestamp: new Date().toISOString().slice(0, 19).replace('T', ' '),
        event: "drone",
        deviceName: "drone_NO1",
        status : "DISCONNECTED",
        data: {
            locationX: -1,
            locationY: -1,
            batteryRemain: -1.0,
            speedX: -1,
            speedY: -1,
            speedZ: -1
        }
    };
    sendToServer(data);
}


/* ------------------------------------------------------------
    Express HTTP 서버 (요청 → 드론으로 전달)
------------------------------------------------------------ */
const app = express();
app.use(express.json());

app.post("/api/drone-command", (req, res) => {
    const json = req.body;

    console.log("📨 HTTP → send-to-drone:", json);

    const ok = sendToDrone(json);

    if (!ok) {
        return res.status(500).json({ message: "Drone not connected" });
    }

    res.json({ message: "Sent to drone", data: json });
});

app.listen(PORT_HTTP, () => {
    console.log(`🌐 Express HTTP server running on port ${PORT_HTTP}`);
});
