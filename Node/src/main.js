const { videoListenAndSend } = require('./videoListener');
require('./tcpServer');
require('./droneController');


function main() {
    console.log('Central Node is Started...\n')
    videoListenAndSend();
}

main();