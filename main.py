import os
import zlib
import struct
import math

# Bitmap font (5x7)
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00000", "00100", "00000"),
}

class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.data = bytearray(w * h * 3)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            idx = (y * self.w + x) * 3
            self.data[idx:idx+3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        for i in range(y, y + h):
            for j in range(x, x + w):
                self.set_pixel(j, i, color)

    def rect_outline(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx)**2 + (y - cy)**2 <= r**2:
                    self.set_pixel(x, y, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if (rx > 0 and ry > 0) and (x - cx)**2 / rx**2 + (y - cy)**2 / ry**2 <= 1:
                    self.set_pixel(x, y, color)

    def draw_line(self, x0, y0, x1, y1, color, thickness):
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            return
        
        # Perpendicular vector
        ux = -dy / length
        uy = dx / length
        
        # Offset
        ox = ux * (thickness / 2)
        oy = uy * (thickness / 2)
        
        points = [
            (int(x0 + ox), int(y0 + oy)),
            (int(x1 + ox), int(y1 + oy)),
            (int(x1 - ox), int(y1 - oy)),
            (int(x0 - ox), int(y0 - oy))
        ]
        self.fill_polygon(points, color)

    def draw_thick_line(self, x1, y1, x2, y2, color, thickness):
        # Very simple thick line (using rects for segments if needed, but here simple loop)
        for t in range(thickness):
            # This is a bit simplistic, but should suffice given constraints
            for i in range(max(abs(x2-x1), abs(y2-y1)) + 1):
                t_val = i / max(abs(x2-x1), abs(y2-y1)) if max(abs(x2-x1), abs(y2-y1)) > 0 else 0
                x = int(x1 + t_val * (x2 - x1))
                y = int(y1 + t_val * (y2 - y1))
                self.set_pixel(x+t//2, y+t//2, color)

    def fill_polygon(self, points, color):
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        for y in range(min_y, max_y + 1):
            intersections = []
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(x)
            intersections.sort()
            for i in range(0, len(intersections), 2):
                x_start = math.ceil(intersections[i])
                x_end = math.floor(intersections[i+1])
                for x in range(x_start, x_end + 1):
                    self.set_pixel(x, y, color)

    def draw_text(self, x, y, text, color, scale):
        for char in text:
            if char in FONT:
                glyph = FONT[char]
                for r, row in enumerate(glyph):
                    for c, pixel in enumerate(row):
                        if pixel == '1':
                            for i in range(scale):
                                for j in range(scale):
                                    self.set_pixel(x + c * scale + j, y + r * scale + i, color)
                x += 6 * scale - 1

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def save_png(canvas, filename):
    w, h = canvas.w, canvas.h
    def chunk(type, data):
        return struct.pack(">I", len(data)) + type + data + struct.pack(">I", zlib.crc32(type + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    scanlines = bytearray()
    for y in range(h):
        scanlines.append(0)
        scanlines.extend(canvas.data[y * w * 3 : (y + 1) * w * 3])
    compressed_data = zlib.compress(scanlines, 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed_data)
    png += chunk(b"IEND", b"")
    with open(filename, "wb") as f:
        f.write(png)

def draw_header(canvas):
    canvas.fill_rect(0, 0, 1024, 112, hex_to_rgb("#0F1E33"))
    canvas.fill_rect(0, 112, 1024, 6, hex_to_rgb("#E8B33C"))
    canvas.draw_text(230, 18, "13 NOVEMBER 2026", hex_to_rgb("#FFFFFF"), 6)
    canvas.draw_text(306, 68, "WORLD NEWS IN ONE IMAGE", hex_to_rgb("#E8B33C"), 3)

def draw_tile1(canvas, tx, ty):
    canvas.fill_rect(tx, ty, 320, 296, hex_to_rgb("#EAF3E2"))
    canvas.fill_rect(tx+62, ty+72, 176, 132, hex_to_rgb("#1B1B1B"))
    for i in range(5):
        canvas.fill_rect(tx+78+i*32, ty+64, 14, 8, hex_to_rgb("#9AA0A6"))
        canvas.fill_rect(tx+78+i*32, ty+204, 14, 8, hex_to_rgb("#9AA0A6"))
    canvas.rect_outline(tx+76, ty+86, 148, 104, hex_to_rgb("#76B900"), 6)
    canvas.fill_circle(tx+150, ty+138, 46, hex_to_rgb("#76B900"))
    canvas.fill_circle(tx+150, ty+138, 18, hex_to_rgb("#1B1B1B"))
    canvas.fill_polygon([(tx+262,ty+84), (tx+290,ty+84), (tx+290,ty+150), (tx+306,ty+150), (tx+276,ty+196), (tx+246,ty+150), (tx+262,ty+150)], hex_to_rgb("#C8102E"))
    canvas.draw_text(tx + 196, ty + 16, "-16%", hex_to_rgb("#C8102E"), 3)

def draw_tile2(canvas, tx, ty):
    canvas.fill_rect(tx, ty, 320, 296, hex_to_rgb("#DCE8F7"))
    canvas.fill_rect(tx+28, ty+52, 96, 54, hex_to_rgb("#2B6CB0"))
    # The Ukraine flag blue/yellow
    canvas.fill_rect(tx+28, ty+52, 96, 27, hex_to_rgb("#2B6CB0"))
    canvas.fill_rect(tx+28, ty+79, 96, 27, hex_to_rgb("#F2C200"))
    # US flag
    canvas.fill_rect(tx+196, ty+52, 96, 54, hex_to_rgb("#FFFFFF"))
    for i in range(7):
        if i % 2 == 0: canvas.fill_rect(tx+196, ty+52+i*8, 96, 8, hex_to_rgb("#B22234"))
    canvas.fill_rect(tx+196, ty+52, 40, 24, hex_to_rgb("#3C3B6E"))
    # Add 6 dots to canton
    for r in range(2):
        for c in range(3):
            canvas.fill_rect(tx+196+8+c*10, ty+52+6+r*10, 3, 3, hex_to_rgb("#FFFFFF"))
    # Table
    canvas.fill_rect(tx+40, ty+212, 240, 16, hex_to_rgb("#8A5A2B"))
    canvas.fill_rect(tx+60, ty+228, 10, 44, hex_to_rgb("#8A5A2B"))
    canvas.fill_rect(tx+250, ty+228, 10, 44, hex_to_rgb("#8A5A2B"))
    # Figures
    canvas.fill_circle(tx+112, ty+168, 24, hex_to_rgb("#E8B98A"))
    canvas.fill_polygon([(tx+84,ty+196), (tx+140,ty+196), (tx+152,ty+228), (tx+72,ty+228)], hex_to_rgb("#2B6CB0"))
    canvas.fill_circle(tx+208, ty+168, 24, hex_to_rgb("#E8B98A"))
    canvas.fill_polygon([(tx+180,ty+196), (tx+236,ty+196), (tx+248,ty+228), (tx+168,ty+228)], hex_to_rgb("#1F2A37"))
    # Handshake
    canvas.draw_line(tx+128, ty+204, tx+160, ty+214, hex_to_rgb("#E8B98A"), 4)
    canvas.draw_line(tx+192, ty+204, tx+160, ty+214, hex_to_rgb("#E8B98A"), 4)
    canvas.fill_circle(tx+160, ty+214, 9, hex_to_rgb("#E8B98A"))

def draw_tile3(canvas, tx, ty):
    canvas.fill_rect(tx, ty, 320, 296, hex_to_rgb("#FBEACD"))
    canvas.fill_rect(tx, ty+218, 320, 78, hex_to_rgb("#2E6FA3"))
    # Wave lines
    canvas.fill_rect(tx+16, ty+248, 80, 4, hex_to_rgb("#FFFFFF"))
    canvas.fill_rect(tx+180, ty+262, 100, 4, hex_to_rgb("#FFFFFF"))
    # Mast/Dish
    canvas.fill_rect(tx+92, ty+120, 8, 98, hex_to_rgb("#6B7280"))
    canvas.fill_rect(tx+72, ty+206, 48, 12, hex_to_rgb("#6B7280"))
    canvas.fill_circle(tx+96, ty+118, 52, hex_to_rgb("#6B7280"))
    canvas.fill_rect(tx+44, ty+118, 104, 52, hex_to_rgb("#FBEACD"))
    canvas.fill_circle(tx+96, ty+118, 36, hex_to_rgb("#9AA0A6"))
    # Spoke lines (3 spokes)
    canvas.draw_line(tx+96, ty+118, tx+96, ty+78, hex_to_rgb("#6B7280"), 4) # Vertical
    canvas.draw_line(tx+96, ty+118, tx+60, ty+82, hex_to_rgb("#6B7280"), 4) # Up-left
    canvas.draw_line(tx+96, ty+118, tx+132, ty+82, hex_to_rgb("#6B7280"), 4) # Up-right
    # Blast/Starburst
    for i in range(8):
        angle = i * 45
        # Inner radius ~30, Outer radius ~45
        x1 = tx+150 + 30 * math.cos(math.radians(angle))
        y1 = ty+78 + 30 * math.sin(math.radians(angle))
        x2 = tx+150 + 45 * math.cos(math.radians(angle))
        y2 = ty+78 + 45 * math.sin(math.radians(angle))
        # Draw spike as triangle
        canvas.fill_polygon([(int(x1-5),int(y1)), (int(x1+5),int(y1)), (int(x2),int(y2))], hex_to_rgb("#C8102E"))
        
    canvas.fill_circle(tx+150, ty+78, 30, hex_to_rgb("#C8102E"))
    canvas.fill_circle(tx+150, ty+78, 8, hex_to_rgb("#FFD23F"))
    # Tanker
    canvas.fill_polygon([(tx+168,ty+236), (tx+300,ty+236), (tx+288,ty+268), (tx+180,ty+268)], hex_to_rgb("#1F2A37"))
    canvas.fill_rect(tx+196, ty+216, 56, 20, hex_to_rgb("#1F2A37"))
    canvas.fill_rect(tx+256, ty+208, 18, 28, hex_to_rgb("#C8102E"))
    # Containers
    canvas.fill_rect(tx+200, ty+218, 20, 14, hex_to_rgb("#E8B33C"))
    canvas.fill_rect(tx+225, ty+218, 20, 14, hex_to_rgb("#FFFFFF"))
    canvas.fill_rect(tx+250, ty+218, 20, 14, hex_to_rgb("#76B900"))
    # Sea Mine
    canvas.fill_circle(tx+52, ty+258, 10, hex_to_rgb("#111827"))
    # 6 spike lines
    for i in range(6):
        angle = i * 60
        x1 = tx+52 + 10 * math.cos(math.radians(angle))
        y1 = ty+258 + 10 * math.sin(math.radians(angle))
        x2 = tx+52 + 25 * math.cos(math.radians(angle))
        y2 = ty+258 + 25 * math.sin(math.radians(angle))
        canvas.draw_line(int(x1), int(y1), int(x2), int(y2), hex_to_rgb("#111827"), 3)

def draw_tile4(canvas, tx, ty):
    canvas.fill_rect(tx, ty, 320, 296, hex_to_rgb("#E4E6F2"))
    canvas.fill_rect(tx+62, ty+66, 196, 128, hex_to_rgb("#111827"))
    canvas.fill_rect(tx+72, ty+76, 176, 108, hex_to_rgb("#1E3A5F"))
    canvas.fill_circle(tx+160, ty+112, 18, hex_to_rgb("#E8B98A"))
    canvas.fill_ellipse(tx+160, ty+168, 34, 20, hex_to_rgb("#E8B98A"))
    # REC dot
    canvas.fill_circle(tx+92, ty+86, 6, hex_to_rgb("#C8102E"))
    # Triangle bottom-right
    canvas.fill_polygon([(tx+216,ty+150), (tx+240,ty+186), (tx+192,ty+186)], hex_to_rgb("#E8B33C"))
    # Exclamation (rectangle)
    canvas.fill_rect(tx+214, ty+160, 4, 14, hex_to_rgb("#111827"))
    canvas.fill_rect(tx+214, ty+178, 4, 4, hex_to_rgb("#111827"))
    # Laptop base
    canvas.fill_rect(tx+42, ty+194, 236, 14, hex_to_rgb("#1F2937"))
    # Coins
    canvas.fill_circle(tx+238, ty+248, 16, hex_to_rgb("#E8B33C"))
    canvas.fill_circle(tx+272, ty+248, 16, hex_to_rgb("#E8B33C"))
    canvas.fill_circle(tx+255, ty+224, 16, hex_to_rgb("#E8B33C"))
    canvas.draw_text(tx+235, ty+240, "$", hex_to_rgb("#000000"), 2)
    canvas.draw_text(tx+269, ty+240, "$", hex_to_rgb("#000000"), 2)
    canvas.draw_text(tx+252, ty+216, "$", hex_to_rgb("#000000"), 2)

def draw_tile5(canvas, tx, ty):
    canvas.fill_rect(tx, ty, 320, 296, hex_to_rgb("#FDE8E4"))
    canvas.fill_rect(tx+58, ty+96, 204, 150, hex_to_rgb("#FFFFFF"))
    canvas.rect_outline(tx+58, ty+96, 204, 150, hex_to_rgb("#111827"), 3)
    canvas.fill_rect(tx+50, ty+84, 220, 12, hex_to_rgb("#6B7280"))
    # Cross ABOVE windows
    canvas.fill_rect(tx+146, ty+112, 28, 72, hex_to_rgb("#C8102E"))
    canvas.fill_rect(tx+124, ty+134, 72, 28, hex_to_rgb("#C8102E"))
    # Windows
    for i in range(2):
        for j in range(4):
            if i==1 and j==1: continue # Door
            canvas.fill_rect(tx+78+j*50, ty+196+i*26, 22, 18, hex_to_rgb("#1F2A37"))
    # Door
    canvas.fill_rect(tx+128, ty+222, 28, 24, hex_to_rgb("#6B7280"))
    # Crack
    canvas.fill_rect(tx+210, ty+96, 4, 44, hex_to_rgb("#111827")) # simplified crack
    # Smoke
    canvas.fill_circle(tx+92, ty+68, 13, hex_to_rgb("#9AA0A6"))
    canvas.fill_circle(tx+128, ty+58, 11, hex_to_rgb("#9AA0A6"))
    # Ambulance
    canvas.fill_rect(tx+16, ty+252, 84, 30, hex_to_rgb("#FFFFFF"))
    canvas.rect_outline(tx+16, ty+252, 84, 30, hex_to_rgb("#111827"), 1)
    canvas.fill_rect(tx+100, ty+260, 30, 22, hex_to_rgb("#FFFFFF"))
    canvas.rect_outline(tx+100, ty+260, 30, 22, hex_to_rgb("#111827"), 1)
    canvas.fill_rect(tx+48, ty+260, 12, 4, hex_to_rgb("#C8102E"))
    canvas.fill_rect(tx+52, ty+256, 4, 12, hex_to_rgb("#C8102E"))
    canvas.fill_circle(tx+38, ty+286, 8, hex_to_rgb("#111827"))
    canvas.fill_circle(tx+112, ty+286, 8, hex_to_rgb("#111827"))

def draw_tile6(canvas, tx, ty):
    canvas.fill_rect(tx, ty, 320, 296, hex_to_rgb("#CDEBCB"))
    for i in range(5):
        canvas.fill_rect(tx + i * 64, ty, 64, 296, hex_to_rgb("#43A047") if i % 2 == 0 else hex_to_rgb("#388E3C"))
    # Pitch lines
    canvas.fill_rect(tx+160, ty, 4, 296, hex_to_rgb("#FFFFFF"))
    # Circle center at (tx+160, ty+148) r=46
    # Drawing circle with outline
    canvas.fill_circle(tx+160, ty+148, 46, hex_to_rgb("#FFFFFF"))
    canvas.fill_circle(tx+160, ty+148, 42, hex_to_rgb("#388E3C"))
    # Goal
    canvas.fill_rect(tx+268, ty+100, 8, 88, hex_to_rgb("#FFFFFF")) # Posts
    canvas.fill_rect(tx+308, ty+100, 8, 88, hex_to_rgb("#FFFFFF"))
    canvas.fill_rect(tx+268, ty+100, 48, 8, hex_to_rgb("#FFFFFF")) # Top
    canvas.fill_rect(tx+268, ty+188, 48, 8, hex_to_rgb("#FFFFFF")) # Bottom
    # Net lines (2 vertical)
    canvas.draw_line(tx+280, ty+108, tx+280, ty+188, hex_to_rgb("#FFFFFF"), 2)
    canvas.draw_line(tx+295, ty+108, tx+295, ty+188, hex_to_rgb("#FFFFFF"), 2)
    # Player
    canvas.fill_circle(tx+104, ty+108, 20, hex_to_rgb("#E8B98A"))
    canvas.fill_polygon([(tx+82,ty+132), (tx+126,ty+132), (tx+134,ty+182), (tx+74,ty+182)], hex_to_rgb("#FFFFFF"))
    canvas.fill_rect(tx+80, ty+182, 48, 22, hex_to_rgb("#111827")) # shorts
    canvas.fill_rect(tx+92, ty+204, 10, 44, hex_to_rgb("#E8B98A")) # leg
    canvas.fill_rect(tx+116, ty+204, 10, 36, hex_to_rgb("#E8B98A")) # leg
    # Arms
    canvas.fill_rect(tx+60, ty+140, 20, 8, hex_to_rgb("#FFFFFF"))
    canvas.fill_rect(tx+130, ty+140, 20, 8, hex_to_rgb("#FFFFFF"))
    # Ball
    canvas.fill_circle(tx+168, ty+244, 16, hex_to_rgb("#FFFFFF"))
    canvas.fill_circle(tx+168, ty+244, 5, hex_to_rgb("#111827"))
    # 126
    canvas.draw_text(tx+199, ty+19, "126", hex_to_rgb("#111827"), 6) # shadow
    canvas.draw_text(tx+196, ty+16, "126", hex_to_rgb("#FFFFFF"), 6)

def draw_labels(canvas, tx, ty, labels):
    canvas.fill_rect(tx+3, ty+296, 314, 135, hex_to_rgb("#F2F4F7")) 
    canvas.fill_rect(tx, ty+296, 320, 3, hex_to_rgb("#C9D1D9"))
    
    n = len(labels)
    block_height = n * 36 - 8
    start_y = ty + 296 + (135 - block_height) // 2
    for i, label in enumerate(labels):
        text_width = len(label) * (6 * 4 - 1)
        canvas.draw_text(tx + (320 - text_width) // 2, start_y + i * 36, label, hex_to_rgb("#111827"), 4)

def main():
    canvas = Canvas(1024, 1024)
    canvas.fill_rect(0, 0, 1024, 1024, hex_to_rgb("#FFFFFF"))
    
    draw_header(canvas)
    
    tiles = [
        ((20, 130), ["NVIDIA CEO", "HUANG RESIGNS"], "TECH", draw_tile1),
        ((352, 130), ["UKRAINE TALKS", "EUROPE JOINS"], "TALKS", draw_tile2),
        ((684, 130), ["IRAN CLAIMS", "RADAR STRIKE"], "GULF", draw_tile3),
        ((20, 573), ["FBI: N. KOREA", "STEALS $400M"], "CYBER", draw_tile4),
        ((352, 573), ["STRIKE ON", "GAZA HOSPITAL", "KILLS 6"], "GAZA", draw_tile5),
        ((684, 573), ["KANE SETS", "ENGLAND CAPS", "RECORD: 126"], "SPORT", draw_tile6)
    ]
    
    tag_colors = [hex_to_rgb(c) for c in ["#76B900", "#1F4E79", "#B45309", "#1E40AF", "#C8102E", "#166534"]]
    
    for i, ((tx, ty), labels, tag, draw_func) in enumerate(tiles):
        canvas.rect_outline(tx, ty, 320, 431, hex_to_rgb("#C9D1D9"), 3)
        draw_func(canvas, tx, ty)
        # Tag
        canvas.fill_rect(tx+12, ty+12, len(tag)*(6*2-1)+16, 24, tag_colors[i])
        canvas.draw_text(tx+20, ty+16, tag, hex_to_rgb("#FFFFFF"), 2)
        draw_labels(canvas, tx, ty, labels)
        
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_png(canvas, os.path.join(output_dir, "entry.png"))

if __name__ == "__main__":
    main()
