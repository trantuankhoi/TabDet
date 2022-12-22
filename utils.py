# Who need AI?
import enum
from shapely.geometry import LineString, Point
GROUP_THRESHOLD = 5

def group_h_lines(lines):
    # x1 = x2
    flag = []
    result = []
    for idx, line in enumerate(lines):
        if idx in flag:
            continue
        group = []
        x1, y1, x2, y2 = line
        group.append([x1, y1, x2, y2])
        flag.append(idx)
        for i in range(idx, len(lines)):
            if i in flag:
                continue
            x3, y3, x4, y4 = lines[i]
            if abs(x3 - x1) <= GROUP_THRESHOLD:
                group.append([x3, y3, x4, y4])
                flag.append(i)
        result.append(group)
    return result

def combine_h_lines(group):
    s = 0
    for line in group:
        s += line[0] # s += x1
    return int(s / len(group))

def group_v_lines(lines):
    # x1 = x2
    flag = []
    result = []
    for idx, line in enumerate(lines):
        if idx in flag:
            continue
        group = []
        x1, y1, x2, y2 = line
        group.append([x1, y1, x2, y2])
        flag.append(idx)
        for i in range(idx, len(lines)):
            if i in flag:
                continue
            x3, y3, x4, y4 = lines[i]
            if abs(y3 - y1) <= GROUP_THRESHOLD:
                group.append([x3, y3, x4, y4])
                flag.append(i)
        result.append(group)
    return result

def combine_v_lines(group):
    s = 0
    for line in group:
        s += line[1] # s += x1
    return int(s / len(group))

def another_line(line):
    x1, y1, x2, y2 = line
    A = y1 - y2
    B = x2 - x1 
    C = x1*y2 - x2*y1
    return A, B, -C

def find_intersection(line1, line2):
    # Crammer
    # https://hayhochoi.vn/giai-he-phuong-trinh-bac-nhat-2-an-bang-dinh-thuc-cramer-phuong-phap-dinh-thuc-cramer-toan-10-chuyen-de.html
    L1 = another_line(line1)
    L2 = another_line(line2)

    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False

def find_intersection1(line1, line2):
    L1 = LineString([(line1[0], line1[1]), (line1[2], line1[3])])
    L2 = LineString([(line2[0], line2[1]), (line2[2], line2[3])])
    int_pt = L1.intersection(L2)
    return (int_pt.coords)


def link_h_lines(lines):
    # x1 == x2
    result = []
    flag = []
    for i, line in enumerate(lines):
        if i in flag:
            continue
        x1, y1, x2, y2 = line
        lst_y = []
        lst_y.append(y1)
        lst_y.append(y2)
        flag.append(i)
        for j, line1 in enumerate(lines):
            if j in flag:
                continue
            x3, y3, x4, y4 = line1
            if x1 == x2 == x3 == x4:
                lst_y.append(y3)
                lst_y.append(y4)
                flag.append(j)

        _min = min(lst_y)
        _max = max(lst_y)
        linked_line = [x1, _min, x2, _max]
        result.append(linked_line)
    return result


def link_v_lines(lines):
    # y1 == y2
    result = []
    flag = []
    for i, line in enumerate(lines):
        if i in flag:
            continue
        x1, y1, x2, y2 = line
        lst_x = []
        lst_x.append(x1)
        lst_x.append(x2)
        flag.append(i)
        for j, line1 in enumerate(lines):
            if j in flag:
                continue
            x3, y3, x4, y4 = line1
            if y1 == y2 == y3 == y4:
                lst_x.append(x3)
                lst_x.append(x4)
                flag.append(j)

        _min = min(lst_x)
        _max = max(lst_x)
        linked_line = [_min, y1, _max, y2]
        result.append(linked_line)
    return result






# ---------------------------------------------- A(x, y_A) ---------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------ D(x_D, y) ------------------ O(x, y) -------------------- B(x_B, y)----------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# ---------------------------------------------- C(x, y_C) ---------------------------------------

def get_neighborhood(intersections):
    result = {}
    for i, inter in enumerate(intersections):
        x, y = inter
        min_A, min_B, min_C, min_D = 10000
        for j, inter1 in enumerate(intersections):
            if i == j:
                continue

