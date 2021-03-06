#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
from __future__ import print_function
import numpy as np
import os, sys, random, string
import termios, tty
import argparse
from time import sleep

class Chess(object):
    def __init__(self, cursor=[7,0], starter=1, touch_move_on=False, show_debug=False):
        self.rooks_red, self.knights_red, self.bishops_red, self.queens_red, self.kings_red, self.pawns_red = [7], [8], [9], [10], [11], [12]        
        self.rooks_blue, self.knights_blue, self.bishops_blue, self.queens_blue, self.kings_blue, self.pawns_blue = [1], [2], [3], [4], [5], [6]
        self.color_spots, self.red_pieces, self.blue_pieces, self.available_pieces = [1, 3, 5, 7, 8, 10, 12, 14, 17, 19, 21, 23, 24, 26, 28, 30, 33, 35, 37, 39, 40, 42, 44, 46, 49, 51, 53, 55, 56, 58, 60, 62], [7,8,9,10,11,12], [1,2,3,4,5,6], [13, 14, 15, 16, 17, 18, 19]
        self.available_en_passant_pieces = []

        self.turns = {
            1:"\033[94m ● \033[0m", # blue turn
            -1:"\033[91m ● \033[0m" # red turn
        }
        # 94: blue, 91: red, 95: pink, 36: cyan, 32: green, 30: black
        # black background: \033[40m
        self.colors = {
            1:"\033[94m{}\033[0m", 2:"\033[91m{}\033[0m", 3:"\033[95m{}\033[0m",
            4:"\033[36m{}\033[0m", 5:"\033[32m{}\033[0m", 9:"\033[30m{}\033[0m"
        }
        self.pieces = {
            # cursors
            -1:"\033[32m ● \033[0m", 0:" · \033[0m",
            # 94 = blue
            1:"\033[94m ♜ \033[0m", 2:"\033[94m ♞ \033[0m", 3:"\033[94m ♝ \033[0m", 4:"\033[94m ♛ \033[0m", 5:"\033[94m ♚ \033[0m", 6:"\033[94m ♟ \033[0m",
            # 91 = red
            7:"\033[91m ♜ \033[0m", 8:"\033[91m ♞ \033[0m", 9:"\033[91m ♝ \033[0m", 10:"\033[91m ♛ \033[0m", 11:"\033[91m ♚ \033[0m", 12:"\033[91m ♟ \033[0m",
            # hovered/selected
            13:"\033[32m ♜ \033[0m",
            14:"\033[32m ♞ \033[0m", 15:"\033[32m ♝ \033[0m", 16:"\033[32m ♛ \033[0m",
            17:"\033[32m ♚ \033[0m", 18:"\033[32m ♟ \033[0m", 19:"\033[36m ♟ \033[0m" 
        }
        self.pieces_letters = {
            -1:"\033[36ma\033[0m", 0:"\033[90me\033[0m", 1:"\033[94mr\033[0m", 2:"\033[94mn\033[0m", 3:"\033[94mb\033[0m", 4:"\033[94mq\033[0m", 5:"\033[94mk\033[0m", 6:"\033[94mp\033[0m", 7:"\033[91mR\033[0m", 8:"\033[91mN\033[0m", 9:"\033[91mB\033[0m", 10:"\033[91mQ\033[0m", 11:"\033[91mK\033[0m", 12:"\033[91mP\033[0m", 13:"\033[36mЯ\033[0m", 14:"\033[36mИ\033[0m", 15:"\033[36mᗺ\033[0m", 16:"\033[36mϘ\033[0m", 17:"\033[36mꓘ\033[0m", 18:"\033[36mᑫ\033[0m", 19:"\033[36mc\033[0m"
        }

        self.show_debug, self.touch_move_on = show_debug, touch_move_on
        self.board = self.populate_board()
        self.showing_moves, self.cursor_item, self.available_moves, self.available_capture_piece_moves, self.available_castle_rooks, self.selected = False, cursor, [], [], [], []
        self.current_turn, self.moves = starter, []
        self.blue_captures, self.red_captures = [], []
        self.red_moves, self.blue_moves, self.total_moves = 0, 0, 0

        self.en_passant, self.in_check = False, False
        self.current_cursor, self.previous_cursor = [], []
        self.promotion_active, self.promotion_piece_index = False, 0

        # castling bools
        self.red_king_moved, self.red_left_rook_moved, self.red_right_rook_moved = False, False, False
        self.blue_king_moved, self.blue_left_rook_moved, self.blue_right_rook_moved = False, False, False

    def init_new_promotion(self):
        self.promotion_active = True
        self.set_promotion_turn_start()

    def populate_board(self):
        flat = [0]*64

        # default board
        # for i,v in enumerate(flat):
        #     if i in self.rooks_blue:     flat[i] = 1
        #     elif i in self.knights_blue: flat[i] = 2
        #     elif i in self.bishops_blue: flat[i] = 3
        #     elif i in self.queens_blue:  flat[i] = 4
        #     elif i in self.kings_blue:   flat[i] = 5
        #     elif i in self.pawns_blue:   flat[i] = 6
        #     elif i in self.rooks_red:    flat[i] = 7
        #     elif i in self.knights_red:  flat[i] = 8
        #     elif i in self.bishops_red:  flat[i] = 9
        #     elif i in self.queens_red:   flat[i] = 10
        #     elif i in self.kings_red:    flat[i] = 11
        #     elif i in self.pawns_red:    flat[i] = 12
        #     else:                        flat[i] = 0

        # promotion test
        # flat[2], flat[4], flat[29]  = 9, 9, 6

        # in_check test
        flat[61], flat[47], flat[45], flat[44] = 5, 11, 9, 9

        # castling test
        # flat[18], flat[0], flat[63], flat[60], flat[61], flat[52], flat[56] = 6, 7, 1, 5, 6, 12, 1

        return np.reshape(flat, (8,8))

    def set_promotion_turn_start(self):
        self.promotion_piece_index = 6 if self.turn(1) else 12

    def cycle_promotion_piece_index(self, cursor, direction):
        self.promotion_piece_index = self.promotion_piece_index + 1 if direction == "right" else self.promotion_piece_index - 1

        if self.turn(1):
            if self.promotion_piece_index == 7: self.promotion_piece_index = 1
            if self.promotion_piece_index == 0: self.promotion_piece_index = 6
            if self.promotion_piece_index == 5:
                self.promotion_piece_index = self.promotion_piece_index + 1 if direction == "right" else self.promotion_piece_index - 1
        elif self.turn(-1):
            if self.promotion_piece_index == 13: self.promotion_piece_index = 7
            if self.promotion_piece_index == 6: self.promotion_piece_index  = 12
            if self.promotion_piece_index == 11:
                self.promotion_piece_index = self.promotion_piece_index + 1 if direction == "right" else self.promotion_piece_index - 1

        # set board piece from index
        self.board[cursor[0]][cursor[1]] = self.promotion_piece_index
        
        return cursor

    def valid_select(self, selected):
        # only allows selection of correct pieces when its your turn
        if selected in (self.blue_pieces if self.turn(1) else self.red_pieces): return True
        return False

    def clear_moves(self):
        if not self.touch_move_on:
            temp_board = self.board.flatten()

            for i,v in enumerate(temp_board):
                if v == -1: temp_board[i] = 0
                if v in self.available_pieces: temp_board = self.clear_available_pieces(i, v, temp_board)

            self.board = np.reshape(temp_board, (8,8))
            self.selected, self.available_moves, self.previous_cursor = [], [], []
            # self.in_check = False

    def clear_en_passants(self):
        self.available_en_passant_pieces.clear()
        self.en_passant = False

    def push_move(self, capture, set_promotion, new_spot, piece):
        self.check_rook_king_move(piece, self.previous_cursor[0][1])
        self.place_piece(new_spot, set_promotion)
        self.increase_moves(capture, piece)
        self.clear_moves()
    
    def push_move_castle(self, capture, set_promotion, rook_spot, rook_piece):
        self.check_rook_king_move(self.previous_cursor[1], self.previous_cursor[0][1]) # king moved
        self.check_rook_king_move(rook_piece, rook_spot) # rook moved
        # places king in new castle spot, then moves rook over one space next to it
        self.place_piece([self.previous_cursor[0][0], self.previous_cursor[0][1]-2], set_promotion)
        self.place_piece_manual(rook_piece, rook_spot, [self.previous_cursor[0][0], self.previous_cursor[0][1]-1])
        # manually set current cursor to new king castle spot
        self.return_cursor([self.previous_cursor[0][0], self.previous_cursor[0][1]-2], True)
        self.increase_moves(capture, self.previous_cursor[1])
        self.clear_moves()

    def move_action(self, cursor):
        promote = False

        if not self.promotion_active:
            selected_spot  = [cursor[0], cursor[1]]                 # clicked spot cords
            selected_cords = self.return_board_cords(selected_spot) # clicked spot board cords str
            selected_piece = self.board[cursor[0]][cursor[1]]       # clicked piece

            if self.selected:
                if selected_cords in self.available_moves:
                    if selected_cords in self.available_capture_piece_moves:
                        promote = self.check_pawn_promotion(selected_spot)
                        self.push_move(True, promote, selected_spot, selected_piece)
                        self.clear_en_passants()
                    elif selected_cords in self.available_castle_rooks:
                        self.push_move_castle(False, False, selected_spot, selected_piece)
                    else:
                        self.check_pawn_en_passant(selected_spot, 1)
                        promote = self.check_pawn_promotion(selected_spot)
                        self.push_move(True, promote, selected_spot, selected_piece)
                    
                    if not promote: self.change_turn()
                    # check if new pushed move puts king in check
                    self.in_check = self._in_check(self.return_king_pos(self.current_turn))
            else:
                if self.valid_select(selected_piece):
                    self.place_available_spots(cursor)
                    self.previous_cursor = [selected_spot, selected_piece]
        else:
            self.promotion_active = False
            self.change_turn()

    def increase_moves(self, capture, piece):
        if self.turn(1):
            self.blue_moves += 1
            if capture: self.blue_captures.append(self.return_piece_from_available(piece))
        elif self.turn(-1):
            self.red_moves += 1
            if capture: self.red_captures.append(self.return_piece_from_available(piece))

        self.total_moves += 1


    # CHECKS #
    #
    def check_rook_king_move(self, moved_piece, moved_X):
        # moved_piece, moved_X = self.previous_cursor[1], self.previous_cursor[0][1]
        if (not self.red_left_rook_moved)   and (moved_piece == 7)  and (moved_X == 0): self.red_left_rook_moved   = True
        if (not self.red_right_rook_moved)  and (moved_piece == 7)  and (moved_X == 7): self.red_right_rook_moved  = True
        if (not self.blue_left_rook_moved)  and (moved_piece == 1)  and (moved_X == 0): self.blue_left_rook_moved  = True
        if (not self.blue_right_rook_moved) and (moved_piece == 1)  and (moved_X == 7): self.blue_right_rook_moved = True
        if (not self.red_king_moved)        and (moved_piece == 11) and (moved_X == 4): self.red_king_moved        = True
        if (not self.blue_king_moved)       and (moved_piece == 5)  and (moved_X == 4): self.blue_king_moved       = True
    #
    def check_pawn_en_passant(self, _cursor, increment):
        if self.turn(1):
            if (self.previous_cursor[1] == 6) and (_cursor[0] == self.previous_cursor[0][0]-increment) and (_cursor[1] == self.previous_cursor[0][1]):
                self.clear_en_passants()
        elif self.turn(-1):
            if (self.previous_cursor[1] == 12) and (_cursor[0] == self.previous_cursor[0][0]+increment) and (_cursor[1] == self.previous_cursor[0][1]):
                self.clear_en_passants()
    #
    def check_pawn_promotion(self, _cursor):
        if (self.previous_cursor[1] == (6 if self.turn(1) else 12)) and (_cursor[0] == (0 if self.turn(1) else 7)): return True
        return False
    #
    def check_rook_castle(self, cursor, direction, check_piece):
        # checks if to the right/left of the king is two empty squares, then a rook
        check_Y, check_X, empty_count, hit_edge = cursor[0], cursor[1], 0, False
        incr_count, incr, outer_edge = 0, (1 if direction == "right" else -1), (8 if direction == "right" else -1)

        for i in range(check_X, outer_edge, incr):
            incr_count += incr
            if check_X+incr_count == outer_edge:
                hit_edge = True
                break
            if self.board[check_Y][check_X+incr_count] in [-1, 0]: empty_count += 1
            if self.board[check_Y][check_X+incr_count] == check_piece: break

        return (not hit_edge) and (empty_count >= 2)
    #
    def _in_check(self, cursor):
        if not cursor == 0:
            check_Y, check_X = cursor[0], cursor[1]

            # TODO: add queen, knight, and pawn 'paths' to see if king is in check from those, only checking rooks/bishops right now
            rook_paths   = self.return_rook_paths(check_Y, check_X)
            bishop_paths = self.return_bishop_paths(check_Y, check_X)
            all_paths    = [rook_paths[0], rook_paths[1], rook_paths[2], rook_paths[3], bishop_paths[0], bishop_paths[1], bishop_paths[2], bishop_paths[3]]

            friendly_pieces = self.blue_pieces if self.turn(1) else self.red_pieces
            enemy_pieces    = self.red_pieces if self.turn(1) else self.blue_pieces
            enemy_rooks     = self.rooks_red if self.turn(1) else self.rooks_blue
            enemy_bishops   = self.bishops_red if self.turn(1) else self.bishops_blue

            for p in range(0, 8):
                for c in range(0, 7):
                    next_Y, next_X = all_paths[p][c][0], all_paths[p][c][1]
                    if not self.inside_board(next_Y, next_X): break
                    board_piece = self.board[next_Y][next_X]
                    if board_piece in friendly_pieces: break
                    if board_piece in enemy_pieces:
                        if (p in range(0, 4)) and (board_piece in enemy_rooks):
                            # self.in_check = True
                            return True
                        elif (p in range(4, 8)) and (board_piece in enemy_bishops):
                            # self.in_check = True
                            return True
                        else: break

            # self.in_check = False
        return False



    # MOVING/SETTING #
    #
    def move_cursor(self, cursor, direction):
        if not self.promotion_active:
            self.current_cursor = self.check_next_col_row(cursor, direction)
            self.cursor_item    = self.current_cursor
        else:
            self.current_cursor = self.cycle_promotion_piece_index(self.current_cursor, direction)

        return self.current_cursor
    #
    def check_next_col_row(self, cursor, direction):
        if direction == "right": cursor[1] = 0 if cursor[1] == 7 else cursor[1]+1
        elif direction == "left": cursor[1] = 7 if cursor[1] == 0 else cursor[1]-1
        elif direction == "up": cursor[0] = 7 if cursor[0] == 0 else cursor[0]-1
        elif direction == "down": cursor[0] = 0 if cursor[0] == 7 else cursor[0]+1
        
        return cursor
    #
    def place_piece(self, new_spot, set_promotion):
        sel_Y, sel_X, new_Y, new_X = self.selected[0], self.selected[1], new_spot[0], new_spot[1]
        check_king = 5 if self.turn(1) else 11

        if (self.board[sel_Y][sel_X] == check_king) and (self.board[new_Y][new_X] == 19) and (new_X in [0, 7]):
            # print(self.board[newY][newX], selX, self.return_piece_from_available(self.board[newY][newX]))
            if new_X == 7:
                self.board[sel_Y][sel_X+1] = self.return_piece_from_available(self.board[new_Y][new_X])
                self.board[sel_Y][sel_X+2] = self.board[sel_Y][sel_X]
                self.current_cursor        = [sel_Y, sel_X+2]
            elif new_X == 0:
                self.board[sel_Y][sel_X-1] = self.return_piece_from_available(self.board[new_Y][new_X])
                self.board[sel_Y][sel_X-2] = self.board[sel_Y][sel_X]
                self.current_cursor        = [sel_Y, sel_X-2]
            self.board[sel_Y][sel_X] = 0
            self.board[new_Y][new_X] = 0
        else:
            self.board[new_Y][new_X] = self.board[sel_Y][sel_X]
            self.board[sel_Y][sel_X] = 0

        if set_promotion: self.init_new_promotion()
    def place_piece_manual(self, set_piece, old_spot, new_spot):
        self.board[old_spot[0]][old_spot[1]] = 0
        self.board[new_spot[0]][new_spot[1]] = set_piece
    #  
    def place_available_spots(self, cursor):
        cursor_piece = self.board[cursor[0]][cursor[1]]

        if cursor_piece in [1,7]:    self.place_rooks_available_moves(cursor)
        elif cursor_piece in [2,8]:  self.place_knights_available_moves(cursor)
        elif cursor_piece in [3,9]:  self.place_bishops_available_moves(cursor)
        elif cursor_piece in [4,10]: self.place_queens_available_moves(cursor)
        elif cursor_piece in [5,11]: self.place_kings_available_moves(cursor)
        elif cursor_piece in [6,12]: self.place_pawns_available_moves(cursor)

        if self.available_moves: self.selected = [cursor[0], cursor[1]]
        self.available_moves.sort()
    #
    def clear_available_pieces(self, index, piece, _temp_board):
        _temp_board[index] = self.return_piece_from_available(piece)
        return _temp_board
    #
    def add_available_move(self, newY, newX, set_piece=-1):
        self.board[newY][newX] = set_piece
        self.available_moves.append(self.return_board_cords([newY, newX]))
    #
    def check_set_capture_piece_available(self, y, x):
        if ((self.turn(1)) and (self.board[y][x] in self.red_pieces)) or ((self.turn(-1)) and (self.board[y][x] in self.blue_pieces)):
            self.add_available_move(y, x, self.return_piece(self.board[y][x]))
            self.available_capture_piece_moves.append(self.return_board_cords([y, x]))
    #
    def set_castle_rook_piece_available(self, y, x):
        self.add_available_move(y, x, self.return_piece(self.board[y][x], True))
        self.available_castle_rooks.append(self.return_board_cords([y, x]))



    # UTILS #
    #
    def turn(self, check):
        return self.current_turn == check
    # 
    def change_turn(self):
        # red = -1, blue = 1
        self.current_turn = -1 if self.turn(1) else 1
    # 
    def inside_board(self, y, x):
        return ((0 <= y <= 7) and (0 <= x <= 7))
    #
    def return_cursor(self, set_cursor, _set=False):
        if _set: self.current_cursor = set_cursor
        return self.current_cursor
    # 
    def return_piece(self, piece_value, castle = False):
        if piece_value in [1,7]:    return 19 if castle else 13
        elif piece_value in [2,8]:  return 14
        elif piece_value in [3,9]:  return 15
        elif piece_value in [4,10]: return 16
        elif piece_value in [5,11]: return 17
        elif piece_value in [6,12]: return 18
    #
    def return_king_pos(self, turn):
        found_king, find_king = 0, (5 if turn == 1 else 11)
        kings = np.where(self.board == find_king)
        if (not len(kings[0]) == 0) and (not len(kings[1]) == 0):
            found_king = [kings[0][0], kings[1][0]]

        return found_king
    #
    def return_piece_from_available(self, piece):
        if self.turn(1):
            return 1 if piece == 19 else piece-6
        elif self.turn(-1):
            return 7 if piece == 19 else piece-12
    #
    def return_board_cords(self, spot):
        spot_Y, spot_X = spot[0], spot[1]
        return "{}{}".format(string.ascii_lowercase[spot_X], -(spot_Y-8))



    # PATHS #
    #
    def return_rook_paths(self, y, x):
        up, right, down, left = [[y-i, x] for i in range(1, 8)], [[y, x+i] for i in range(1, 8)], [[y+i, x] for i in range(1, 8)], [[y, x-i] for i in range(1, 8)]
        return [up, right, down, left]
    #
    def return_bishop_paths(self, y, x):
        top_left, top_right, bottom_right, bottom_left = [[y-i, x-i] for i in range(1, 8)], [[y-i, x+i] for i in range(1, 8)], [[y+i, x+i] for i in range(1, 8)], [[y+i, x-i] for i in range(1, 8)]
        return [top_left, top_right, bottom_right, bottom_left]



    # AVAILABLE MOVES #
    #
    def place_pawns_available_moves(self, cursor):
        pawn_Y, pawn_X = cursor[0], cursor[1]
        up_ys_blue, up_xs_blue, down_ys_red, down_xs_red     = [pawn_Y-1, pawn_Y-2], [pawn_X, pawn_X], [pawn_Y+1, pawn_Y+2], [pawn_X, pawn_X]
        diag_ys_blue, diag_xs_blue, diag_ys_red, diag_xs_red = [pawn_Y-1, pawn_Y-1], [pawn_X-1, pawn_X+1], [pawn_Y+1, pawn_Y+1], [pawn_X-1, pawn_X+1]
        en_passant_ys, en_passant_xs                         = [pawn_Y, pawn_Y], [pawn_X-1, pawn_X+1]

        vert_ys      = up_ys_blue if self.turn(1) else down_ys_red
        vert_xs      = up_xs_blue if self.turn(1) else down_xs_red
        diag_ys      = diag_ys_blue if self.turn(1) else diag_ys_red
        diag_xs      = diag_xs_blue if self.turn(1) else diag_xs_red
        enemy_pieces = self.red_pieces if self.turn(1) else self.blue_pieces
        row_check    = 6 if self.turn(1) else 1

        # vert 1
        for u in range(0, 1):
            if self.inside_board(vert_ys[u], vert_xs[u]):
                if (self.board[vert_ys[u]][vert_xs[u]] == 0):
                    self.add_available_move(vert_ys[u], vert_xs[u])

        # vert 2
        for u in range(1, 2):
            if pawn_Y == row_check:
                if self.inside_board(vert_ys[u], vert_xs[u]):
                    if (self.board[vert_ys[u]][vert_xs[u]] == 0):
                        self.add_available_move(vert_ys[u], vert_xs[u])
                        if (vert_ys[u] == pawn_Y+2) or (vert_ys[u] == pawn_Y-2): self.available_en_passant_pieces.append([vert_ys[u], vert_xs[u]])
        # diag
        for d in range(0, 2):
            if self.inside_board(diag_ys[d], diag_xs[d]):
                if self.board[diag_ys[d]][diag_xs[d]] in enemy_pieces:
                    if (self.board[diag_ys[d]][diag_xs[d]] == 0):
                        self.add_available_move(diag_ys[d], diag_xs[d])
                    else:
                        self.check_set_capture_piece_available(diag_ys[d], diag_xs[d])
        # en passant
        for e in range(0, 2):
            if self.inside_board(en_passant_ys[e], en_passant_xs[e]):
                if self.board[en_passant_ys[e]][en_passant_xs[e]] in enemy_pieces:
                    if (len(self.available_en_passant_pieces) >= 1) and ([en_passant_ys[e], en_passant_xs[e]] == self.available_en_passant_pieces[0]):
                        self.en_passant = True
                        self.check_set_capture_piece_available(en_passant_ys[e], en_passant_xs[e])
    #
    def place_queens_available_moves(self, cursor):
        self.place_rooks_available_moves(cursor)
        self.place_bishops_available_moves(cursor)
    #
    def place_bishops_available_moves(self, cursor):
        bishop_Y, bishop_X = cursor[0], cursor[1]
        bishop_spots = self.return_bishop_paths(bishop_Y, bishop_X)

        # loop up-left/up-right/down-right/down-left paths
        for p in range(0,4):
            for b in range(0, 7):
                next_Y, next_X = bishop_spots[p][b][0], bishop_spots[p][b][1]
                if self.inside_board(next_Y, next_X):
                    if self.board[next_Y][next_X] == 0:
                        self.add_available_move(next_Y, next_X)
                    else:
                        self.check_set_capture_piece_available(next_Y, next_X)
                        break
                else: break
    #
    def place_knights_available_moves(self, cursor):
        knights_Y, knights_X = cursor[0], cursor[1]
        knights_spots = [[knights_Y-1, knights_X-2], [knights_Y-2, knights_X-1], [knights_Y-1, knights_X+2], [knights_Y-2, knights_X+1], [knights_Y-1, knights_X-2], [knights_Y+2, knights_X-1], [knights_Y+1, knights_X+2], [knights_Y+2, knights_X+1]]

        for i in range(0, 8):
            next_Y, next_X = knights_spots[i][0], knights_spots[i][1]
            if self.inside_board(next_Y, next_X):
                if self.board[next_Y][next_X] == 0:
                    self.add_available_move(next_Y, next_X)
                else:
                    self.check_set_capture_piece_available(next_Y, next_X)
    #
    def place_kings_available_moves(self, cursor):
        king_Y, king_X = cursor[0], cursor[1]
        kings_spots = [[king_Y, king_X-1], [king_Y, king_X+1], [king_Y-1, king_X], [king_Y+1, king_X], [king_Y-1, king_X-1], [king_Y-1, king_X+1], [king_Y+1, king_X-1], [king_Y+1, king_X+1]]

        # loop spots
        for i in range(0, 8):
            next_Y, next_X = kings_spots[i][0], kings_spots[i][1]
            if self.inside_board(next_Y, next_X):
                if self.board[next_Y][next_X] == 0: # 0 = empty square
                    # check if available spot wont put king in check, then append
                    if not self._in_check([next_Y, next_X]):
                        self.add_available_move(next_Y, next_X)
                else:
                    self.check_set_capture_piece_available(next_Y, next_X) # potential enemy piece

        # check castle
        if self.turn(1): king_moved, right_rook_moved, left_rook_moved, rook = self.blue_king_moved, self.blue_right_rook_moved, self.blue_left_rook_moved, 1
        elif self.turn(-1): king_moved, right_rook_moved, left_rook_moved, rook = self.red_king_moved, self.red_right_rook_moved, self.red_left_rook_moved, 7

        # right 2 (castle)
        if (not king_moved and not right_rook_moved):
            if (not self._in_check([king_Y, king_X])) and (not self._in_check([king_Y, king_X+1])) and (not self._in_check([king_Y, king_X+2])):
                if self.check_rook_castle(cursor, "right", rook):
                    self.set_castle_rook_piece_available(king_Y, king_X+3)
        # left 3 (castle)
        if (not king_moved and not left_rook_moved):
            if (not self._in_check([king_Y, king_X])) and (not self._in_check([king_Y, king_X-1])) and (not self._in_check([king_Y, king_X-2])) and (not self._in_check([king_Y, king_X-3])):
                if self.check_rook_castle(cursor, "left", rook):
                    self.set_castle_rook_piece_available(king_Y, king_X-4)

        # check appended available moves for in_check, then remove them

        # if available moves are reduced down to 0 because they were all in check, check mate
    #
    def place_rooks_available_moves(self, cursor):
        rook_Y, rook_X = cursor[0], cursor[1]

        rook_paths = self.return_rook_paths(rook_Y, rook_X)

        # loop up/down/left/right paths
        for p in range(0, 4):
            for r in range(0, 7):
                next_Y, next_X = rook_paths[p][r][0], rook_paths[p][r][1]
                if (0 <= next_Y <= 7) and (0 <= next_X <= 7):
                    if self.board[next_Y][next_X] == 0:
                        self.add_available_move(next_Y, next_X)
                    else:
                        self.check_set_capture_piece_available(next_Y, next_X)
                        break


    
    def draw_board(self, cursor):
        os.system('clear')
        col_idx, row_num, letters = 0, 8, ""

        if self.show_debug:
            print()
            # print("                          \033[90mDEBUG \033[0m\n")
            # print(" self.promotion_active:  {}".format(self.promotion_active))
            # print(" self.en_passant:        {}".format(self.en_passant))
            print(" self.in_check:          {} {}".format(self.in_check, self.turns[self.current_turn]))
            # print(" self.avail_en_passant:  {}".format(self.available_en_passant_pieces))
            print(" self.previous_cursor:   {}".format(self.previous_cursor))

            # print(" self.red_left_rook_moved:   {}".format(self.red_left_rook_moved))
            # print(" self.red_right_rook_moved:  {}".format(self.red_right_rook_moved))
            # print(" self.red_king_moved:        {}".format(self.red_king_moved))
            # print(" self.blue_left_rook_moved:  {}".format(self.blue_left_rook_moved))
            # print(" self.blue_right_rook_moved: {}".format(self.blue_right_rook_moved))
            # print(" self.blue_king_moved:       {}".format(self.blue_king_moved))

            print(" self.moves:             {} , {} , {} ".format(self.colors[1].format(self.blue_moves), self.colors[2].format(self.red_moves), self.total_moves))
            print(" self.current_turn:     {}, {}".format(self.turns[self.current_turn], self.current_turn))
            if self.selected:
                print(" self.selected:          {} ,{}, {} ".format(self.return_board_cords(self.selected), self.pieces[self.board[self.selected[0]][self.selected[1]]], self.board[self.selected[0]][self.selected[1]]))
            else:
                print(" self.selected:          · ")
            print(" self.cursor_item:       {}{} ,{}, {} ".format(string.ascii_lowercase[self.cursor_item[1]], -(self.cursor_item[0]-8), self.pieces[self.board[self.cursor_item[0]][self.cursor_item[1]]], self.board[self.cursor_item[0]][self.cursor_item[1]]))
            print(" self.available_moves:   {}".format(', '.join([self.colors[5].format(x) if x in self.available_capture_piece_moves else self.colors[4].format(x) if not x in self.available_castle_rooks else self.colors[5].format(x) for x in self.available_moves])))
            
            # print(" self.blue_captures:    {}".format(self.colors[2].format(','.join([self.colors[2].format(x) for x in self.blue_captures]))))
            # print(" self.red_captures:     {}".format(self.colors[1].format(','.join([self.colors[2].format(x) for x in self.red_captures]))))

        # red captures top
        if len(self.red_captures) >= 1:
            print("\n    {} {} {} {} {} {}".format(
                ''.join([self.pieces[x].replace(' ', '') for x in self.red_captures if x == 6]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.red_captures if x == 3]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.red_captures if x == 2]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.red_captures if x == 1]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.red_captures if x == 4]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.red_captures if x == 5]) 
            ))
        else: print()

        for row_index, row in enumerate(self.board):
            # print(" ", end="")
            if -(self.cursor_item[0]-8) == row_num:
                # pink number
                print(" \033[95m%d\033[0m " % (row_num), end="")
            else:
                # grey number
                print(" \033[90m%d\033[0m " % (row_num), end="")

            for col_index, item in enumerate(row):
                current = [row_index, col_index]
                # self.board[row_index][col_index]

                if item == -1:   self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ● " if current == cursor else " · "))
                elif item == 1:  self.print_item(col_idx, self.colors[3 if current == cursor else 1].format(" ♜ "))
                elif item == 2:  self.print_item(col_idx, self.colors[3 if current == cursor else 1].format(" ♞ "))
                elif item == 3:  self.print_item(col_idx, self.colors[3 if current == cursor else 1].format(" ♝ "))
                elif item == 4:  self.print_item(col_idx, self.colors[3 if current == cursor else 1].format(" ♛ "))
                elif item == 5:  self.print_item(col_idx, self.colors[3 if current == cursor else 1].format(" ♚ "))
                elif item == 6:  self.print_item(col_idx, self.colors[3 if current == cursor else 1].format(" ♟ "))
                elif item == 7:  self.print_item(col_idx, self.colors[3 if current == cursor else 2].format(" ♜ "))
                elif item == 8:  self.print_item(col_idx, self.colors[3 if current == cursor else 2].format(" ♞ "))
                elif item == 9:  self.print_item(col_idx, self.colors[3 if current == cursor else 2].format(" ♝ "))
                elif item == 10: self.print_item(col_idx, self.colors[3 if current == cursor else 2].format(" ♛ "))
                elif item == 11: self.print_item(col_idx, self.colors[3 if current == cursor else 2].format(" ♚ "))
                elif item == 12: self.print_item(col_idx, self.colors[3 if current == cursor else 2].format(" ♟ "))
                elif item == 13: self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ♜ "))
                elif item == 14: self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ♞ "))
                elif item == 15: self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ♝ "))
                elif item == 16: self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ♛ "))
                elif item == 17: self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ♚ "))
                elif item == 18: self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ♟ "))
                elif item == 19: self.print_item(col_idx, self.colors[5 if current == cursor else 4].format(" ♜ "))
                else:            self.print_item(col_idx, self.colors[3 if current == cursor else 1].format(" . " if current == cursor else "   "))

                col_idx += 1
            row_num -= 1

            #print raw board right
            if self.show_debug:
                if row_num == 7:   print("  {}".format(' '.join([ self.pieces_letters[self.board[0][x]] for x in range(0, 8) ])), end="")
                elif row_num == 6: print("  {}".format(' '.join([ self.pieces_letters[self.board[1][x]] for x in range(0, 8) ])), end="")
                elif row_num == 5: print("  {}".format(' '.join([ self.pieces_letters[self.board[2][x]] for x in range(0, 8) ])), end="")
                elif row_num == 4: print("  {}".format(' '.join([ self.pieces_letters[self.board[3][x]] for x in range(0, 8) ])), end="")
                elif row_num == 3: print("  {}".format(' '.join([ self.pieces_letters[self.board[4][x]] for x in range(0, 8) ])), end="")
                elif row_num == 2: print("  {}".format(' '.join([ self.pieces_letters[self.board[5][x]] for x in range(0, 8) ])), end="")
                elif row_num == 1: print("  {}".format(' '.join([ self.pieces_letters[self.board[6][x]] for x in range(0, 8) ])), end="")
                elif row_num == 0: print("  {}".format(' '.join([ self.pieces_letters[self.board[7][x]] for x in range(0, 8) ])), end="")

            print()
        
        # letters
        for i in range(0,8):
            if self.cursor_item[1] == i:
                # pink letter
                letters += "\033[95m {} \033[0m".format(string.ascii_lowercase[i])
            else:
                # grey letter
                letters += "\033[90m {} \033[0m".format(string.ascii_lowercase[i])

        print("   {}".format(letters), end="")

        # blue captures bottom
        if len(self.blue_captures) >= 1:
            print("\n    {} {} {} {} {} {}".format(
                ''.join([self.pieces[x].replace(' ', '') for x in self.blue_captures if x == 12]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.blue_captures if x == 9]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.blue_captures if x == 8]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.blue_captures if x == 7]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.blue_captures if x == 10]),
                ''.join([self.pieces[x].replace(' ', '') for x in self.blue_captures if x == 11]) 
            ))
        else: print()

        print("\n ⭠ ⭡⭣ ⭢  to move.\n SPACE to select.\n BACKSPACE to deselect.\n ESC to exit.\n")

    def print_item(self, idx, item):
        if idx in self.color_spots: print("\033[40m{}\033[0m".format(item), end="")
        else: print("\033[43m{}\033[0m".format(item), end="")

    def print_captures_in_range(self, capture_list, loop_list, color):
        out_str = ""

        for i in range(0, 4):
            if len(capture_list) >= loop_list[i]+1:
                out_str += f"{capture_list[loop_list[i]]} "
            else: break

        print(out_str, end="")


    # test
    def add_blue_captures(self):
        self.blue_captures.append(random.randrange(7, 13))
    def add_red_captures(self):
        self.red_captures.append(random.randrange(1, 8))


def play_console():
    global cursor,turn

    # chess.place_available_spots(cursor)
    chess.draw_board(cursor)
    try:
        while True:
            k = getkey()

            if k == 'up':
                cursor = chess.move_cursor(cursor, "up")
                chess.draw_board(cursor)
            elif k == 'right':
                cursor = chess.move_cursor(cursor, "right")
                chess.draw_board(cursor)
            elif k == 'down':
                cursor = chess.move_cursor(cursor, "down")
                chess.draw_board(cursor)
            elif k == 'left':
                cursor = chess.move_cursor(cursor, "left")
                chess.draw_board(cursor)
            elif k == 'space':
                chess.move_action(cursor)
                cursor = chess.return_cursor(cursor)
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
        sleep(0.5)

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