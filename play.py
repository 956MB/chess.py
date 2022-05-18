#!/usr/bin/env python3
from chess import Chess
# from datetime import datetime
import sys, random, tty, os, termios
import argparse
from time import sleep

def play_console():
    global cursor,turn

    # chess.place_available_spots(cursor)
    chess.draw_board(cursor)
    try:
        while True:
            k = getkey()

            if k == 'up':
                cursor = chess.move_piece(cursor, "up")
                chess.draw_board(cursor)
            elif k == 'right':
                cursor = chess.move_piece(cursor, "right")
                chess.draw_board(cursor)
            elif k == 'down':
                cursor = chess.move_piece(cursor, "down")
                chess.draw_board(cursor)
            elif k == 'left':
                cursor = chess.move_piece(cursor, "left")
                chess.draw_board(cursor)
            elif k == 'space':
                chess.move_action(cursor)
                cursor = chess.set_new_cursor()
                chess.draw_board(cursor)
            elif k in ['backspace', 'esc']:
                chess.clear_moves()
                chess.draw_board(cursor)
            elif k in ['test1']:
                chess.add_blue_captures()
                chess.draw_board(cursor)
            elif k in ['test2']:
                chess.add_red_captures()
                chess.draw_board(cursor)
            elif k == 'esc':
                break

    except (KeyboardInterrupt, SystemExit):
        os.system('stty sane')
        sys.exit()

def sim():
    global cursor,turn

    while True:
        chess.play_random(turn)
        turn = -1 if turn == 1 else 1
        chess.change_turn(turn)
        chess.draw_board(cursor, turn)
        sleep(delay)

def getkey():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3: k = ord(b[2])
            else: k = ord(b)

            # print(k)

            key_mapping = { 27:'esc', 32:'space', 68:'left', 67:'right', 66:'down', 65:'up', 127:'backspace', 116:'test1', 121:'test2' }
            return key_mapping.get(k, chr(k))

    except Exception: sys.exit()
    finally: termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Play Chess in the terminal. Written in Python.")
    opt = ap._action_groups.pop()
    req = ap.add_argument_group('required arguments')
    opt.add_argument("-V","--version",action="store_true",help="show script version")
    opt.add_argument("-s","--starter",const=1,type=int,choices=range(0,2),nargs="?",help="set starting piece. Blue/Red (0, 1)")
    opt.add_argument("-t","--touch_move",action="store_true",help="set \"Touch-move\" rule on ON")
    opt.add_argument("-d","--show_debug",action="store_true",help="set \"Show Debug\" option on ON")
    ap._action_groups.append(opt)
    args = vars(ap.parse_args())

    cursor, starter, touch_move, show_debug = [7,0], 0, False, False
    if args["version"]:    sys.exit("v1.0.0")
    starter = 1 if starter == 0 else -1
    if args["touch_move"]: touch_move = True
    if args["show_debug"]: show_debug = True

    chess = Chess(cursor=cursor, starter=starter, touch_move_on=touch_move, show_debug=show_debug)
    play_console()