var BOARD_SIZE = Math.round(Math.sqrt($("g").length));
var ROOM_NAME = window.location.pathname.substr(1);

var aviable_turns = new Array(0)
var field = new Array(BOARD_SIZE);
for (var i = 0; i < BOARD_SIZE; ++i) {
    field[i] = new Array(BOARD_SIZE);
    for (var j = 0; j < BOARD_SIZE; ++j) {
        field[i][j] = 0;
    }
}
update_field();

var player;
var sock = new WebSocket("ws://" + window.location.host + "/sock/" + ROOM_NAME);
sock.onopen = function() {
    state = "Wait";
    $("div#statusline").attr("class", "ok")
                       .html("Соединение установлено, жду начала игры");
}

sock.onmessage = function(event) {
    message = JSON.parse(event.data);
    switch (message["type"]) {
        case "wait":
            break;
        case "start":
            player = message["player"];
            $("div#statusline").attr("class", "ok")
                               .html("Игра началась");
            break;
        case "state":
            for (var i = 0; i < BOARD_SIZE; ++i)
                for (var j = 0; j < BOARD_SIZE; ++j)
                    field[i][j] = message["board"][i][j];
            if (player < 2) {
                aviable_turns = message["aviable"]
                if (aviable_turns.length > 0) {
                    $("div#statusline").html("<b>Ваш ход</b>");
                } else {
                    $("div#statusline").html("Ход противника");
                }
            }
            update_field();
            break;
        case "end":
            for (var i = 0; i < BOARD_SIZE; ++i)
                for (var j = 0; j < BOARD_SIZE; ++j)
                    field[i][j] = message["board"][i][j];
            aviable_turns = []
            update_field();
            var text = "Конец игры. ";
            if (player < 2) {
                if (message["result"] == "win")
                    text += "Вы выиграли. ";
                else if (message["result"] == "lose")
                    text += "Вы проиграли. ";
                else
                    text += "Вы сыграли в ничью. ";
            }
            text += ("Cчёт " + message["points"][0] + ":" + message["points"][1]);
            $("div#statusline").attr("class", "ok")
                               .html(text);
            sock.close();
            break;
        case "connection_error":
            var text = "Игрок " + message["player"] + " оборвал соединение"
            $("div#statusline").attr("class", "error")
                               .html(text);
            sock.close();
            break;
    }
}

function update_field() {
    for (var i = 0; i < BOARD_SIZE; ++i) {
        for (var j = 0; j < BOARD_SIZE; ++j) {
            var g_id = "g#" + i + "-" + j;
            var cur_cell = $(g_id);
            cur_cell.off("click");
            var classes = "";
            for (var k in aviable_turns) {
                if (aviable_turns[k][0] == i+1 && aviable_turns[k][1] == j+1) {
                    cur_cell.click(make_move);
                    classes += "aviable ";
                    break;
                }
            }
            switch (field[i][j]) {
                case 0:
                    classes += "empty";
                    break;
                case 1:
                    classes += "fpoint";
                    break;
                case 2:
                    classes += "spoint";
                    break;
                case 3:
                    classes += "facomm";
                    break;
                case 4:
                    classes += "sacomm";
                    break;
                case 5:
                    classes += "fdcomm";
                    break;
                case 6:
                    classes += "sdcomm";
                    break;
            }
            cur_cell.attr("class", classes);
        }
    }
}

function make_move(event) {
    var coords = event.delegateTarget.id.split("-");
    var m = JSON.stringify({ type: "move", move: [(+coords[0])+1, (+coords[1])+1] });
    sock.send(m);
}
