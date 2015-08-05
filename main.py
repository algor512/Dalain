#!/usr/bin/env python3
import logging
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import game

waiting_rooms = {}
games = {}

class GameServer:
    def __init__(conn1, conn2, room):
        self.players = [weakref.ref(conn1), weakref.ref(conn2)]
        self.game = game.Game()
        self.room = room
        logging.info("Room {}: create game".format(room))
        logging.info("Room {}: first player ip {}, id {}".format(room, \
                     conn1.request.remote_ip, id(conn1)))
        logging.info("Room {}: second player ip {}, id {}".format(room, \
                     conn2.request.remote_ip, id(conn2)))
        message = json.dumps({"type": "command", "data": "run"})
        conn1.write_message(message)
        conn2.write_message(message)

    def on_message(self, message, player):
        m = json.loads(message)
        try:
            if m["type"] == "answer":
                pass
                # Обрабатываем, отправляем одному opponents_turn, другому your_turn
        except:
            pass

    def on_close(self, player):
        pass # FIXME

class MainHandler(tornado.web.RequestHandler):
    def get(self, name):
        self.write("Hello, {}".format(name))

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, room):
        logging.info("{}, {}: open connection".format(self.request.remote_ip, room))
        self.room = room
        if room in waiting_rooms:
            games[room] = GameServer(waiting_rooms[room], self, room)
            waiting_rooms[room].game = games[room]
            waiting_rooms[room].player = 0
            self.game = games[room]
            self.player = 1
            del waiting_rooms[room]
        else:
            self.write_message(json.dumps({"type": "command", "data": "wait"}))
            waiting_rooms[room] = self

    def on_message(self, message):
        if hasattr(self, "game"):
            self.game.on_message(message, self.player)
        else:
            logging.warning("{}, {}: there are messages, but game isn't running".format(self.request.remote_ip, self.room))
            self.write_message(json.dumps({"type": "command", "data": "wait"}))

    def on_close(self):
        if self.close_reason != "Game ended":
            self.game.on_close(self.player)

application = tornado.web.Application([
    (r"/([0-1a-z]+)", MainHandler),
    (r"/sock/([0-1a-z]+)", MainHandler)
])

if __name__ == "__main__":
    tornado.options.parse_command_line()
    logging.info("Starting up")
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
