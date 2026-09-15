from __future__ import annotations
import random, base64, io
from PIL import Image
import json
from hashlib import md5


class Piece:
    def __init__(self, img: Image, index: int) -> Piece:
        self.image_index = index
        self.image_data = img
        self.image_width, self.image_height = img.size
        self.right_edge = [img.getpixel((self.image_width - 1, y)) for y in range(self.image_height)]
        self.left_edge = [img.getpixel((0, y)) for y in range(self.image_height)]
        self.top_edge = [img.getpixel((x,0)) for x in range(self.image_width)]
        self.bottom_edge = [img.getpixel((x,self.image_height - 1)) for x in range(self.image_width)]

        prev_color = self.right_edge[0]
        broken = (prev_color[0] < 127 or prev_color[1] < 127 or prev_color[2] < 127)
        for p in self.right_edge:
            if p != prev_color:
                broken = True
                break
        self.is_right_border = not broken

        prev_color = self.left_edge[0]
        broken = (prev_color[0] < 127 or prev_color[1] < 127 or prev_color[2] < 127)
        for p in self.left_edge:
            if p != prev_color:
                broken = True
                break
        self.is_left_border = not broken

        prev_color = self.top_edge[0]
        broken = (prev_color[0] < 127 or prev_color[1] < 127 or prev_color[2] < 127)
        for p in self.top_edge:
            if p != prev_color:
                broken = True
                break
        self.is_top_border = not broken

        prev_color = self.bottom_edge[0]
        broken = (prev_color[0] < 127 or prev_color[1] < 127 or prev_color[2] < 127)
        for p in self.bottom_edge:
            if p != prev_color:
                broken = True
                break
        self.is_bottom_border = not broken

    def compare_edge_right(self, other: Piece) -> int:
        if self.image_height != other.image_height:
            raise ValueError
        diff = 0
        for i in range(self.image_height):
            p1 = self.right_edge[i]
            p2 = other.left_edge[i]
            diff += abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) + abs(p1[2]-p2[2])
        return diff
    
    def compare_edge_bottom(self, other: Piece) -> int:
        if self.image_width != other.image_width:
            raise ValueError
        diff = 0
        for i in range(self.image_width):
            p1 = self.bottom_edge[i]
            p2 = other.top_edge[i]
            diff += abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) + abs(p1[2]-p2[2])
        return diff
    
    def __repr__(self):
        return md5((str(self.top_edge)+str(self.bottom_edge)+str(self.right_edge)+str(self.left_edge)).encode()).hexdigest()

class Puzzle:
    def __init__(self, data: dict, attempt: int = 1) -> Puzzle:
        self.width = data['cols']
        self.height = data['rows']
        self.piece_width = data['width']
        self.piece_height = data['height']
        puzzle_pieces = data['pieces']
        self.puzzle_id = data['puzzle_id']
        self.name = data['title']
        self.assembled_image = [[None]*self.width for _ in range(self.height)]
        self.top_border_pieces: set[Piece] = set()
        self.bottom_border_pieces: set[Piece] = set()
        self.right_border_pieces: set[Piece] = set()
        self.left_border_pieces: set[Piece] = set()
        self.top_border: list[Piece] = list()
        self.bottom_border: list[Piece] = list()
        self.right_border: list[Piece] = list()
        self.left_border: list[Piece] = list()
        self.center_pieces: set[Piece] = set()
        self.attempt = attempt
        for i,piece_data in enumerate(puzzle_pieces):
            image_bytes = io.BytesIO(base64.b64decode(piece_data))
            piece_image = Image.open(image_bytes).convert('RGB')
            piece = Piece(piece_image,i)
            if piece.is_top_border:
                if piece.is_right_border:
                    self.top_right = piece
                elif piece.is_left_border:
                    self.top_left = piece
                else:
                    self.top_border_pieces.add(piece)
            elif piece.is_bottom_border:
                if piece.is_right_border:
                    self.bottom_right = piece
                elif piece.is_left_border:
                    self.bottom_left = piece
                else:
                    self.bottom_border_pieces.add(piece)
            elif piece.is_right_border:
                self.right_border_pieces.add(piece)
            elif piece.is_left_border:
                self.left_border_pieces.add(piece)
            else:
                self.center_pieces.add(piece)
    
    def make_image(self):
        img = Image.new('RGBA', (self.width*self.piece_width, self.height*self.piece_height))
        for y, row in enumerate(self.assembled_image):
            for x, p in enumerate(row):
                if p is not None:
                    img.paste(p.image_data, (x*self.piece_width, y*self.piece_height))
        return img
    
    def build_edge(self, pieces: set[Piece], edge: list[Piece], start: Piece, end: Piece, right_compare: bool = False):
        edge_len = len(pieces)
        current = start
        for _ in range(edge_len):
            edge.append(current)
            candidates = []
            for p in pieces:
                if right_compare:
                    candidates.append((p, current.compare_edge_right(p)))
                else:
                    candidates.append((p, current.compare_edge_bottom(p)))
            candidates.sort(key=lambda x: x[1])

            if len(candidates) > 1 and self.attempt > 0:
                top_candidates = [c for c in candidates if c[1] <= (candidates[0][1] + (self.piece_height+self.piece_width)//2*5)]
                top_candidates.sort(key=lambda x: random.random() * x[1])
                candidates = top_candidates

            current = candidates[0][0]
            pieces.remove(current)
        edge.append(current)
        edge.append(end)

    def solve(self) -> Puzzle:
        self.build_edge(self.top_border_pieces, self.top_border, self.top_left, self.top_right, True)
        self.build_edge(self.bottom_border_pieces, self.bottom_border, self.bottom_left, self.bottom_right, True)
        self.build_edge(self.right_border_pieces, self.right_border, self.top_right, self.bottom_right, False)
        self.build_edge(self.left_border_pieces, self.left_border, self.top_left, self.bottom_left, False)

        self.assembled_image[0] = self.top_border
        self.assembled_image[-1] = self.bottom_border

        for i,row in enumerate(self.assembled_image):
            row[0] = self.left_border[i]
            row[-1] = self.right_border[i]

        for y,row in enumerate(self.assembled_image):
            for x,pos in enumerate(row):
                if pos is not None:
                    continue
                candidates = []
                for p in self.center_pieces:
                    if self.attempt % 2 == 0:
                        candidates.append((p, row[x-1].compare_edge_right(p) + self.assembled_image[y-1][x].compare_edge_bottom(p)))
                    else:
                        candidates.append((p, min(row[x-1].compare_edge_right(p), self.assembled_image[y-1][x].compare_edge_bottom(p))))
                candidates.sort(key=lambda x: x[1])

                if len(candidates) > 1 and self.attempt > 5:
                    top_candidates = [c for c in candidates if c[1] <= (candidates[0][1] + (self.piece_height+self.piece_width)//2*5)]
                    top_candidates.sort(key=lambda x: random.random() * x[1] * 2)
                    candidates = top_candidates

                found = candidates[0][0]
                self.center_pieces.remove(found)
                row[x] = found
        return self
    
    def order(self) -> list[int]:
        piece_order = []
        for row in self.assembled_image:
            for p in row:
                piece_order.append(p.image_index)
        return piece_order
    
puzzledata = json.load(open("puzzledata.json"))

puzzle = Puzzle(puzzledata, 0)
order = puzzle.solve().order()

print(order)