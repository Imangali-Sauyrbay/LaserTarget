# Line through two points
def find_x(p1, p2, y):
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    c = (p2[1] - (m * p2[0]))

    return (c - y) / (-m)


def find_y(p1, p2, x):
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    c = (p2[1] - (m * p2[0]))

    return m * x + c


def find_x_bounds(points, y):
    p1, p2, p3, p4 = points

    if p1[0] == p4[0]:
        res_p1 = p1[0]
    else:
        res_p1 = find_x(p1, p4, y)

    if p2[0] == p3[0]:
        res_p2 = p2[0]
    else:
        res_p2 = find_x(p2, p3, y)

    return res_p1, res_p2


def find_y_bounds(points, x):
    p1, p2, p3, p4 = points

    if p1[1] == p2[1]:
        res_p1 = p1[1]
    else:
        res_p1 = find_y(p1, p2, x)

    if p4[1] == p3[1]:
        res_p2 = p4[1]
    else:
        res_p2 = find_y(p4, p3, x)

    return res_p1, res_p2


def get_normalized_x(points, coords, w):
    x, y = coords
    x_left, x_right = find_x_bounds(points, y)
    px = ((x - x_left) / (x_right - x_left)) * w
    if w < px or px < 0:
        return None
    return px


def get_normalized_y(points, coords, h):
    x, y = coords
    y_top, y_bottom = find_y_bounds(points, x)
    py = ((y - y_top) / (y_bottom - y_top)) * h
    if h < py or py < 0:
        return None
    return py
