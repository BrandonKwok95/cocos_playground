import math
import os
import struct
import zlib


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "ui")


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(clamp(lerp(c1[i], c2[i], t)) for i in range(4))


def png_chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def save_png(path, width, height, rgba):
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(rgba[start : start + stride])

    data = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            png_chunk(b"IEND", b""),
        ]
    )
    with open(path, "wb") as f:
        f.write(data)


class Canvas:
    def __init__(self, width, height, scale=1, bg=(0, 0, 0, 0)):
        self.logical_width = width
        self.logical_height = height
        self.scale = scale
        self.width = width * scale
        self.height = height * scale
        self.buf = bytearray(bg * (self.width * self.height))

    def sx(self, x):
        return int(round(x * self.scale))

    def color_at(self, x, y):
        i = (y * self.width + x) * 4
        return self.buf[i : i + 4]

    def blend_pixel(self, x, y, color):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        r, g, b, a = color
        i = (y * self.width + x) * 4
        if a >= 255:
            self.buf[i : i + 4] = bytes((r, g, b, 255))
            return
        if a <= 0:
            return
        dr, dg, db, da = self.buf[i], self.buf[i + 1], self.buf[i + 2], self.buf[i + 3]
        inv = 255 - a
        out_a = a + da * inv // 255
        if out_a == 0:
            return
        self.buf[i] = clamp((r * a + dr * da * inv // 255) / out_a)
        self.buf[i + 1] = clamp((g * a + dg * da * inv // 255) / out_a)
        self.buf[i + 2] = clamp((b * a + db * da * inv // 255) / out_a)
        self.buf[i + 3] = clamp(out_a)

    def fill_rect(self, x0, y0, x1, y1, color):
        x0, y0, x1, y1 = map(self.sx, (x0, y0, x1, y1))
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.width, x1), min(self.height, y1)
        for y in range(y0, y1):
            for x in range(x0, x1):
                self.blend_pixel(x, y, color)

    def vertical_gradient(self, top, bottom):
        for y in range(self.height):
            t = y / max(1, self.height - 1)
            color = mix(top, bottom, t)
            row = bytes(color) * self.width
            start = y * self.width * 4
            self.buf[start : start + self.width * 4] = row

    def ellipse(self, cx, cy, rx, ry, color):
        cx, cy, rx, ry = self.sx(cx), self.sx(cy), self.sx(rx), self.sx(ry)
        x0, x1 = max(0, cx - rx), min(self.width - 1, cx + rx)
        y0, y1 = max(0, cy - ry), min(self.height - 1, cy + ry)
        rx2, ry2 = max(1, rx * rx), max(1, ry * ry)
        for y in range(y0, y1 + 1):
            dy2 = (y - cy) * (y - cy)
            for x in range(x0, x1 + 1):
                if (x - cx) * (x - cx) * ry2 + dy2 * rx2 <= rx2 * ry2:
                    self.blend_pixel(x, y, color)

    def polygon(self, points, color):
        pts = [(self.sx(x), self.sx(y)) for x, y in points]
        if len(pts) < 3:
            return
        min_y = max(0, min(y for _, y in pts))
        max_y = min(self.height - 1, max(y for _, y in pts))
        for y in range(min_y, max_y + 1):
            nodes = []
            j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if (yi < y <= yj) or (yj < y <= yi):
                    x = xi + (y - yi) * (xj - xi) / (yj - yi)
                    nodes.append(int(x))
                j = i
            nodes.sort()
            for i in range(0, len(nodes), 2):
                if i + 1 >= len(nodes):
                    break
                x0, x1 = max(0, nodes[i]), min(self.width - 1, nodes[i + 1])
                for x in range(x0, x1 + 1):
                    self.blend_pixel(x, y, color)

    def line(self, x0, y0, x1, y1, width, color):
        x0s, y0s, x1s, y1s = map(self.sx, (x0, y0, x1, y1))
        ws = max(1, self.sx(width))
        dx, dy = x1s - x0s, y1s - y0s
        length = max(1, int(math.hypot(dx, dy)))
        for i in range(length + 1):
            t = i / length
            x = int(x0s + dx * t)
            y = int(y0s + dy * t)
            self._circle_scaled(x, y, ws // 2, color)

    def _circle_scaled(self, cx, cy, r, color):
        r2 = r * r
        for y in range(max(0, cy - r), min(self.height - 1, cy + r) + 1):
            for x in range(max(0, cx - r), min(self.width - 1, cx + r) + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                    self.blend_pixel(x, y, color)

    def circle_ring(self, cx, cy, outer_r, inner_r, color):
        cx, cy = self.sx(cx), self.sx(cy)
        outer_r, inner_r = self.sx(outer_r), self.sx(inner_r)
        outer2, inner2 = outer_r * outer_r, inner_r * inner_r
        for y in range(max(0, cy - outer_r), min(self.height - 1, cy + outer_r) + 1):
            for x in range(max(0, cx - outer_r), min(self.width - 1, cx + outer_r) + 1):
                d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if inner2 <= d2 <= outer2:
                    self.blend_pixel(x, y, color)
    def downsample(self):
        if self.scale == 1:
            return self.buf
        out = bytearray(self.logical_width * self.logical_height * 4)
        s = self.scale
        area = s * s
        for y in range(self.logical_height):
            for x in range(self.logical_width):
                acc = [0, 0, 0, 0]
                for yy in range(s):
                    for xx in range(s):
                        i = ((y * s + yy) * self.width + (x * s + xx)) * 4
                        acc[0] += self.buf[i]
                        acc[1] += self.buf[i + 1]
                        acc[2] += self.buf[i + 2]
                        acc[3] += self.buf[i + 3]
                o = (y * self.logical_width + x) * 4
                out[o : o + 4] = bytes(clamp(v / area) for v in acc)
        return out

    def save(self, filename):
        path = os.path.join(OUT_DIR, filename)
        save_png(path, self.logical_width, self.logical_height, self.downsample())
        return path


def draw_cloud(c, x, y, scale=1.0, alpha=230):
    col = (255, 255, 255, alpha)
    shade = (213, 239, 250, int(alpha * 0.52))
    c.ellipse(x - 68 * scale, y + 8 * scale, 64 * scale, 30 * scale, shade)
    c.ellipse(x - 58 * scale, y, 46 * scale, 30 * scale, col)
    c.ellipse(x - 15 * scale, y - 16 * scale, 58 * scale, 42 * scale, col)
    c.ellipse(x + 45 * scale, y + 1 * scale, 54 * scale, 32 * scale, col)
    c.ellipse(x + 88 * scale, y + 10 * scale, 36 * scale, 23 * scale, col)


def generate_background():
    c = Canvas(720, 1280, scale=1, bg=(0, 0, 0, 255))
    c.vertical_gradient((91, 199, 247, 255), (219, 250, 255, 255))
    c.ellipse(608, 132, 56, 56, (255, 235, 119, 235))
    c.ellipse(608, 132, 86, 86, (255, 235, 119, 55))
    draw_cloud(c, 116, 132, 0.58, 232)
    draw_cloud(c, 360, 84, 0.47, 220)
    draw_cloud(c, 616, 242, 0.56, 220)

    c.line(34, 292, 286, 264, 4, (103, 86, 73, 255))
    c.line(434, 308, 698, 276, 4, (103, 86, 73, 255))
    pennants = [(236, 89, 92, 255), (68, 205, 162, 255), (255, 204, 81, 255), (100, 149, 255, 255)]
    for i, x in enumerate(range(58, 276, 37)):
        y = 289 - (x - 34) * 28 / 252
        c.polygon([(x, y), (x + 24, y - 3), (x + 13, y + 34)], pennants[i % len(pennants)])
    for i, x in enumerate(range(456, 680, 37)):
        y = 305 - (x - 434) * 32 / 264
        c.polygon([(x, y), (x + 24, y - 3), (x + 13, y + 34)], pennants[(i + 1) % len(pennants)])

    c.polygon([(0, 600), (112, 470), (238, 616), (374, 452), (536, 625), (720, 480), (720, 820), (0, 820)], (81, 181, 127, 255))
    c.polygon([(0, 704), (94, 570), (214, 714), (358, 544), (492, 724), (638, 588), (720, 680), (720, 920), (0, 920)], (61, 158, 119, 255))
    c.fill_rect(0, 744, 720, 1280, (95, 200, 113, 255))
    c.polygon([(0, 820), (92, 780), (226, 814), (360, 770), (514, 816), (720, 778), (720, 1280), (0, 1280)], (119, 217, 100, 255))

    for x in (-20, 86, 632, 748):
        c.polygon([(x - 8, 742), (x + 8, 742), (x + 13, 852), (x - 13, 852)], (123, 78, 45, 255))
        c.ellipse(x, 704, 44, 42, (43, 150, 92, 255))
        c.ellipse(x - 28, 724, 31, 29, (48, 169, 100, 255))
        c.ellipse(x + 28, 724, 31, 29, (36, 137, 84, 255))

    c.ellipse(360, 976, 252, 72, (64, 142, 91, 95))
    c.polygon([(54, 1050), (666, 1050), (720, 1280), (0, 1280)], (166, 103, 54, 255))
    for i, y in enumerate(range(1060, 1280, 34)):
        col = (181, 116, 60, 255) if i % 2 == 0 else (151, 91, 48, 255)
        c.polygon([(30 - i * 20, y), (690 + i * 20, y), (720 + i * 24, y + 28), (0 - i * 24, y + 28)], col)
        c.line(0 - i * 24, y + 28, 720 + i * 24, y + 28, 3, (111, 70, 42, 115))
    for x in range(82, 660, 106):
        c.ellipse(x, 1128, 6, 4, (94, 57, 36, 145))
        c.ellipse(x + 42, 1192, 6, 4, (94, 57, 36, 130))

    return c.save("background.png")

def generate_sword():
    c = Canvas(360, 900, scale=3)
    cx = 180

    c.polygon([(cx - 62, 142), (cx - 21, 50), (cx, 14), (cx + 21, 50), (cx + 62, 142), (cx + 44, 650), (cx, 724), (cx - 44, 650)], (79, 65, 82, 255))
    c.polygon([(cx - 43, 148), (cx - 14, 62), (cx, 30), (cx + 14, 62), (cx + 43, 148), (cx + 28, 631), (cx, 686), (cx - 28, 631)], (218, 240, 246, 255))
    c.polygon([(cx, 32), (cx + 14, 62), (cx + 43, 148), (cx + 28, 631), (cx, 686)], (151, 202, 221, 255))
    c.polygon([(cx - 25, 156), (cx - 10, 82), (cx - 3, 64), (cx - 6, 620), (cx - 20, 610)], (255, 255, 255, 135))
    c.line(cx, 61, cx, 678, 4, (104, 142, 161, 180))

    c.polygon([(66, 662), (112, 622), (248, 622), (294, 662), (250, 709), (110, 709)], (87, 63, 77, 255))
    c.polygon([(78, 656), (118, 632), (242, 632), (282, 656), (244, 692), (116, 692)], (245, 185, 58, 255))
    c.polygon([(105, 641), (255, 641), (231, 674), (128, 674)], (255, 222, 104, 255))
    c.ellipse(cx, 664, 36, 22, (255, 234, 123, 255))
    c.ellipse(cx, 664, 20, 12, (95, 202, 226, 255))

    c.polygon([(132, 700), (228, 700), (216, 825), (144, 825)], (74, 54, 77, 255))
    c.polygon([(147, 711), (213, 711), (204, 814), (156, 814)], (187, 73, 84, 255))
    for y in range(724, 802, 24):
        c.line(149, y, 211, y + 16, 9, (247, 188, 77, 255))
        c.line(211, y + 16, 149, y + 32, 5, (103, 58, 71, 130))
    c.ellipse(cx, 842, 43, 37, (76, 57, 77, 255))
    c.ellipse(cx, 836, 32, 27, (236, 161, 55, 255))
    c.ellipse(cx, 829, 17, 12, (255, 225, 107, 255))

    return c.save("sword.png")


def generate_turntable():
    size = 900
    c = Canvas(size, size, scale=2)
    cx = cy = size // 2
    s = c.scale
    high_cx = cx * s
    high_cy = cy * s
    outer = 420 * s
    inner = 365 * s
    colors = [
        (241, 88, 87, 255),
        (255, 205, 82, 255),
        (81, 191, 150, 255),
        (82, 145, 231, 255),
        (250, 131, 70, 255),
        (151, 109, 222, 255),
        (111, 206, 91, 255),
        (238, 113, 151, 255),
    ]

    # Paint the main wheel in one pass for smooth wedge edges.
    for y in range(max(0, high_cy - outer), min(c.height, high_cy + outer)):
        dy = y - high_cy
        for x in range(max(0, high_cx - outer), min(c.width, high_cx + outer)):
            dx = x - high_cx
            r = math.hypot(dx, dy)
            if r > outer:
                continue
            if r > inner:
                base = (118, 76, 54, 255)
                t = (r - inner) / max(1, outer - inner)
                col = mix((211, 139, 72, 255), base, t)
            else:
                a = (math.atan2(dy, dx) + math.pi * 2 + math.pi / 8) % (math.pi * 2)
                idx = int(a / (math.pi * 2 / 8)) % 8
                col = colors[idx]
                shade = 0.9 + 0.12 * (1 - r / inner)
                col = (clamp(col[0] * shade), clamp(col[1] * shade), clamp(col[2] * shade), 255)
            c.blend_pixel(x, y, col)

    c.circle_ring(cx, cy, 432, 412, (73, 55, 64, 255))
    c.circle_ring(cx, cy, 412, 370, (204, 125, 65, 255))

    for i in range(8):
        ang = i * math.pi * 2 / 8
        x = cx + math.cos(ang) * 366
        y = cy + math.sin(ang) * 366
        c.line(cx, cy, x, y, 10, (255, 246, 214, 230))
        c.line(cx, cy, x, y, 4, (93, 67, 73, 95))

    c.ellipse(cx, cy, 144, 144, (82, 60, 72, 255))
    c.ellipse(cx, cy, 124, 124, (255, 223, 93, 255))
    c.ellipse(cx, cy, 82, 82, (239, 83, 80, 255))
    c.ellipse(cx, cy, 38, 38, (255, 244, 151, 255))

    for ring in (225, 305):
        c.circle_ring(cx, cy, ring + 5, ring - 5, (255, 255, 255, 120))

    for i in range(12):
        ang = i * math.pi * 2 / 12 + 0.14
        x = cx + math.cos(ang) * 388
        y = cy + math.sin(ang) * 388
        c.ellipse(x, y, 15, 15, (88, 61, 57, 255))
        c.ellipse(x - 3, y - 4, 6, 5, (244, 195, 111, 190))

    c.ellipse(cx - 110, cy - 145, 62, 26, (255, 255, 255, 70))
    c.ellipse(cx - 36, cy - 185, 36, 15, (255, 255, 255, 50))

    return c.save("turntable.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    paths = [
        generate_background(),
        generate_sword(),
        generate_turntable(),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()



