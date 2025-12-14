const net = require("net");
const axios = require("axios");
const dotenv = require('dotenv')
const FormData = require('form-data');

const TCP_PORT = 5001;   // Raspberry Pi → Node


dotenv.config();
/*
   TCP로 라즈베리파이에서 영상 수신
 */
function videoListener(onFrameReceived) {
    const server = net.createServer((socket) => {
        console.log("Raspberry Pi connected");

        let buffer = Buffer.alloc(0);

        socket.on("data", (data) => {
            buffer = Buffer.concat([buffer, data]);

            // 프레임 길이 + 데이터 조합 처리
            while (buffer.length >= 4) {
                const frameLen = buffer.readUInt32BE(0);

                if (buffer.length >= 4 + frameLen) {
                    const frame = buffer.slice(4, 4 + frameLen);
                    buffer = buffer.slice(4 + frameLen);

                    onFrameReceived(frame); // 콜백 실행
                } else {
                    break;
                }
            }
        });

        socket.on("close", () => console.log("Raspberry Pi disconnected"));
    });

    server.listen(TCP_PORT, () => {
        console.log(`TCP Listener Running on port ${TCP_PORT}`);
    });
}

async function videoSender(frame) {
    try {
        await axios.post(process.env.VIDEO_FORWARD_URL, frame, {
            headers: { "Content-Type": "image/jpeg" }
        });
        console.log("Frame sent to Spring");
    } catch (err) {
        console.error("Error sending frame to Spring:", err.message);
    }
}

function videoListenAndSend() {
    let latestFrame = null;
    console.log("VideoListener has Started...")
    videoListener((frame) => {
        videoSender(frame);

        latestFrame = frame;
    });

    setInterval(async () => {
        if (!latestFrame) return;

        try {
            const form = new FormData();
            form.append('deviceId', 'drone'); // 원하는 deviceId
            form.append('file', latestFrame, {
                filename: 'frame.jpg',
                contentType: 'image/jpeg'
            });

            await axios.post(process.env.IMAGE_URL, form, {
                headers: form.getHeaders() // multipart/form-data 헤더 자동 설정
            });

            console.log("Image sent to server");
        } catch (err) {
            console.error("Error sending Image:", err.message);
        }
    }, 1000);

}

module.exports = {
    videoListenAndSend
};