#!/usr/bin/env python3
import logging
import os
import json
import weakref
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import tornado.template
import game
from config import *

waiting_rooms = {}
games = {}
loader = tornado.template.Loader("template")

class GameServer:
    def __init__(self, conn1, conn2, room):
        self.players = [weakref.ref(conn1), weakref.ref(conn2)]
        self.game = game.Game()
        self.room = room
        logging.info("Room {}: create game".format(room))
        logging.info("Room {}: first player ip {}, id {}".format(room, \
                     conn1.request.remote_ip, id(conn1)))
        logging.info("Room {}: second player ip {}, id {}".format(room, \
                     conn2.request.remote_ip, id(conn2)))
        m1 = json.dumps({"type": "start", "player": 1})
        m2 = json.dumps({"type": "start", "player": 2})
        conn1.write_message(m1)
        conn2.write_message(m2)
        m_state = json.dumps({"type": "state", "board": self.game.get_field(), \
                              "aviable": self.game.get_allowed_moves()})
        conn1.write_message(m_state)

    def on_message(self, message, player):
        m = json.loads(message)
        try:
            if m["type"] == "ok":
                pass
            elif m["type"] == "move":
                closeConnection = False
                if player != self.game.turn:
                    logging.info("Room {}: move from wrong player".format(room))
                res = self.game.make_move(int(m["move"][0]), int(m["move"][1]))
                mes = [{"type": "state", "board": self.game.get_field()}, \
                       {"type": "state", "board": self.game.get_field()}]
                mes[self.game.turn]["aviable"] = self.game.get_allowed_moves()
                mes[(self.game.turn+1)%2]["aviable"] = []
                if len(mes[self.game.turn]["aviable"]) == 0:
                    results = self.game.get_points()
                    mes = [{"type": "end", "points": results}, \
                           {"type": "end", "points": results}]
                    if results[0] > results[1]:
                        mes[0]["result"] = "win"
                        mes[1]["result"] = "lose"
                    elif results[1] > results[0]:
                        mes[0]["result"] = "lose"
                        mes[1]["result"] = "win"
                    else:
                        mes[0]["result"] = mes[1]["result"] = "draw"
                    closeConnection = True
                self.players[0]().write_message(mes[0])
                self.players[1]().write_message(mes[1])
                if closeConnection:
                    self.players[0]().close(reason = "Game ended")
                    self.players[1]().close(reason = "Game ended")
        except:
            pass

    def on_close(self, player, code, reason):
        logging.info("Room {}, player {} close connection (code {}, reason {})".format(self.room,
                     player, code, reason))
        # FIXME: error message

class MainHandler(tornado.web.RequestHandler):
    def get(self, name):
        self.render("base.html", BOARD_SIZE=BOARD_SIZE)

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
            self.write_message(json.dumps({"type": "wait"}))
            waiting_rooms[room] = self

    def on_message(self, message):
        if hasattr(self, "game"):
            self.game.on_message(message, self.player)
        else:
            logging.warning("{}, {}: there are messages, but game isn't running".format(self.request.remote_ip, self.room))
            self.write_message(json.dumps({"type": "wait"}))

    def on_close(self):
        if self.close_reason != "Game ended":
            self.game.on_close(self.player, self.close_code, self.close_reason)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "template_path": os.path.join(os.path.dirname(__file__), "template")
}

application = tornado.web.Application([
        (r"/([0-1a-z]+)", MainHandler),
        (r"/sock/([0-1a-z]+)", WebSocketHandler),
        (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"]})
    ], **settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    logging.info("Starting up")
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
