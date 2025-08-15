function QWebChannel(transport, initCallback) {
    this.transport = transport;

    const send = (data) => {
        transport.send(JSON.stringify(data));
    };

    var channel = this;
    transport.onmessage = function (message) {
        var data = JSON.parse(message.data);
        if (data.type === "signal") {
            channel.objects[data.object][data.signal].apply(null, data.args);
        }
    };

    channel.objects = {};
    channel.objects.pybridge = window.pybridge = {};

    // Créer les méthodes disponibles
    channel.objects.pybridge.closeApplication = function () {
        channel.send({
            type: "invokeMethod",
            object: "pybridge",
            method: "closeApplication",
            args: []
        });
    };

    if (initCallback) {
        setTimeout(() => initCallback(channel), 10);
    }
}


// Code QWebChannel minimal
function initQWebChannel() {
    console.log("Initializing QWebChannel...");
    if (window.QWebChannel) {
        console.log("QWebChannel already initialized.");
        return;
    }


    window.QWebChannel = QWebChannel;

    // Initialiser automatiquement si qt.webChannelTransport est disponible
    // if (window.qt && window.qt.webChannelTransport) {
    //     new QWebChannel(window.qt.webChannelTransport, function (channel) {
    //         console.log('QWebChannel initialized successfully');
    //     });
    // } else {
    //     console.warn("QWebChannel transport not available");
    // }
}

initQWebChannel();