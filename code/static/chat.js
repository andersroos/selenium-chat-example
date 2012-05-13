
function on_screen(msg, color) {
    chat = $("#chat")
        chat.append("<p style='color: " + color + ";'>" + msg + "</p>")
        chat.prop("scrollTop", chat.prop("scrollHeight"))
}

$(document).ready(function() {

    //var ws = new WebSocket("ws://echo.websocket.org/");
    var ws = new WebSocket("ws://localhost:8080/chat");

    ws.onopen = function() {
    };
    
    ws.onmessage = function (evt) { 
        var msg = evt.data;
        on_screen(msg, "black");
    };
    ws.onclose = function() {
        on_screen("Connection closed.", "black");
    };

    $('#send').click(function() {
        var msg = $('#text').val();
        $('#text').val("")
        ws.send(msg);
        on_screen(msg, "red")
    });

    
});
      
