import itertools
import math

import pixie
import scipy

from .utils import build_adj

# Image
im_size = 1000
# Point
pnt_num = 6
pnt_radius = 50
# Edges
edge_color_123 = "#0000ff"
edge_color_12 = "#ff0000"
edge_color_13 = "#00ff00"
# Font
font = pixie.read_font("fonts/Roboto-Regular_1.ttf")
font.size = 20

paint = pixie.Paint(pixie.SOLID_PAINT)
paint_123 = pixie.Paint(pixie.SOLID_PAINT)
paint_12 = pixie.Paint(pixie.SOLID_PAINT)
paint_13 = pixie.Paint(pixie.SOLID_PAINT)

paint.color = pixie.Color(0, 0, 0, 1)
paint_123.color = pixie.parse_color(edge_color_123)
paint_12.color = pixie.parse_color(edge_color_12)
paint_13.color = pixie.parse_color(edge_color_13)


def points_in_circumference(r, n=6):
    r = r - pnt_radius
    return [(math.cos(2 * math.pi / n * x) * r + im_size / 2, math.sin(2 * math.pi / n * x) * r + im_size / 2) for x in
            range(0, n)]


def draw(num_points: int, edges):
    adj = build_adj(num_points, edges)

    edges_num = scipy.special.comb(num_points, 2)
    edges_subsets = list(itertools.combinations((range(0, num_points)), 2))

    # Sample points
    image = pixie.Image(im_size, im_size)
    image.fill(pixie.Color(1, 1, 1, 1))
    ctx = image.new_context()

    # Edges
    points = points_in_circumference(im_size / 2, n=num_points)
    for i1, p1 in enumerate(points):
        for i2, p2 in enumerate(points):
            ctx.line_width = 10
            if adj[i1][i2][0] and adj[i1][i2][1]:
                ctx.stroke_style = paint_123
                ctx.stroke_segment(p1[0], p1[1], p2[0], p2[1])
            elif adj[i1][i2][0]:
                ctx.stroke_style = paint_12
                ctx.stroke_segment(p1[0], p1[1], p2[0], p2[1])
            elif adj[i1][i2][1]:
                ctx.stroke_style = paint_13
                ctx.stroke_segment(p1[0], p1[1], p2[0], p2[1])

    # Points
    ctx.fill_style = paint
    for i, point in enumerate(points):
        ctx.circle(point[0], point[1], r=pnt_radius)
        ctx.fill()

    return image
