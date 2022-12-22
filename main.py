import os
import cv2
import numpy as np
import random

from utils import *


class Item:
    def __init__(self, img_name):
        self.name = img_name
        self.img_path = os.path.join(IMG_DIR, self.name)

        self.img = cv2.imread(self.img_path, cv2.IMREAD_COLOR)
        self.img_w = self.img.shape[1]
        self.img_h = self.img.shape[2]
        
        self.gray = self.get_gray()
        self.bw = cv2.adaptiveThreshold(self.gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)

        self.horizontal = self.get_horizontal()
        self.vertical = self.get_vertical()


    def copy_img(self, src):
        return np.copy(src)

    
    def get_gray(self):
        if len(self.img.shape) != 2:
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.img
        return cv2.bitwise_not(gray)
    
    
    def get_horizontal(self):
        horizontal = self.copy_img(self.bw)
        cols = horizontal.shape[1]
        horizontal_size = cols // 30
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        horizontal = cv2.erode(horizontal, horizontalStructure)
        horizontal = cv2.dilate(horizontal, horizontalStructure)
        if ANALYZE:
            cv2.imwrite(os.path.join("./horizontal", self.name), horizontal)
        return cv2.bitwise_not(horizontal)
    
    
    def get_vertical(self):
        vertical = self.copy_img(self.bw)
        rows = vertical.shape[1]
        vertical_size = rows // 30
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
        vertical = cv2.erode(vertical, verticalStructure)
        vertical = cv2.dilate(vertical, verticalStructure)
        if ANALYZE:
            cv2.imwrite(os.path.join("./vertical", self.name), vertical)
        return cv2.bitwise_not(vertical)


    def get_lines(self):
        h_lines = []
        v_lines = []

        masks = [self.vertical, self.horizontal]
        line_image = self.copy_img(self.img) * 0
        clone = self.copy_img(self.img) 
        for mask in masks:
            edges = cv2.adaptiveThreshold(mask, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, -2)

            lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
            try:
                for line in lines:
                    x1, y1, x2, y2 = line[0]                
                    if x1 == x2:
                        percent = abs(y1 - y2) * 100 / self.img_h
                        if percent > 40:
                            h_lines.append([x1, y1, x2, y2])
                    else:
                        percent = abs(x1 - x2) * 100 / self.img_w
                        if percent > 40:
                            v_lines.append([x1, y1, x2, y2])
            except:
                print("Cant find line")
        return [h_lines, v_lines]


    def combine_lines(self):
        h_lines, v_lines = self.get_lines()
        # Horizontal
        grouped_h_lines = group_h_lines(h_lines)
        combined_h_lines = []
        for group in grouped_h_lines:
            mean = combine_h_lines(group)
            for line in group:
                x1, y1, x2, y2 = line
                combined_h_lines.append([mean, y1, mean, y2])
        # Vertical
        grouped_v_lines = group_v_lines(v_lines)
        combined_v_lines = []
        for group in grouped_v_lines:
            mean = combine_v_lines(group)
            for line in group:
                x1, y1, x2, y2 = line
                combined_v_lines.append([x1, mean, x2, mean])
        return [combined_h_lines, combined_v_lines]
    

    def link_lines(self):
        # Just apply for combined horizontal and combined vertical
        h_lines, v_lines = self.combine_lines()
        return [link_h_lines(h_lines), link_v_lines(v_lines)]


    def get_intersections1(self):
        h_lines, v_lines = self.link_lines()
        intersections = []

        for h_line in h_lines:
            for v_line in v_lines:
                inter = find_intersection1(h_line, v_line)
                if inter != False:
                    intersections.append(inter)
        return intersections


    def get_intersections(self):
        h_lines, v_lines = self.link_lines()
        intersections = []

        for h_line in h_lines:
            for v_line in v_lines:
                inter = find_intersection(h_line, v_line)
                if inter != False:
                    intersections.append(inter)
        return intersections


    def draw_lines(self, masks, dir):
        img = self.copy_img(self.img)
        for mask in masks:
            for line in mask:
                x1, y1, x2, y2 = line
                cv2.line(img, (x1, y1), (x2, y2), ((random.randint(0, 255)), random.randint(0, 255), random.randint(0, 255)), 2)
            cv2.imwrite(os.path.join(r"./" + dir, self.name), img)


    def draw_intersection(self):
        intersections = self.get_intersections()
        clone = self.copy_img(self.img)
        for inter in intersections:
            try:
                x = int(inter[0])
                y = int(inter[1])
                clone = cv2.circle(clone, (x, y), radius=0, color=(0, 0, 255), thickness=5)
            except:
                continue
        cv2.imwrite(os.path.join("./intersections", self.name), clone)

    def draw_intersection1(self):
        intersections = self.get_intersections1()
        clone = self.copy_img(self.img)
        for inter in intersections:
            try:
                x = int(inter[0][0])
                y = int(inter[0][1])
                clone = cv2.circle(clone, (x, y), radius=0, color=(0, 0, 255), thickness=5)
            except:
                continue
        cv2.imwrite(os.path.join("./intersections1", self.name), clone)

if __name__ == "__main__":
    IMG_DIR = "./source/document_layout"
    OUT_DIR = "./outputs"

    ANALYZE = True

    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 50  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 50  # minimum number of pixels making up a line
    max_line_gap = 0.005  # maximum gap in pixels between connectable line segments

    for img in os.listdir(IMG_DIR):
        item = Item(img)
        print(item.img_path)
        item.draw_lines(item.get_lines(), "outputs")
        item.draw_lines(item.combine_lines(), "combined")
        item.draw_lines(item.link_lines(), "linked")
        item.draw_intersection()
        item.draw_intersection1()
    
    # Pipeline:
    # 1. Tìm edges
    # 2. Tìm lines (lọc các lines có độ lớn bé hơn 40% kích thước chiều dài hoặc chiều dọc) - "./outputs"
    # 3. Nhóm các lines trùng lặp hoặc gần như trùng lặp (cùng biểu diễn 1 border) - "./grouped"
    # 4. Hợp nhất các lines trùng lặp (combined_lines) - "./combined"
    # 5. Nối các lines cùng nằm trên 1 đường thẳng (linked_lines) - "./linked"
    # 6. Tìm giao điểm 
    ## 6.1. Tìm giao điểm bằng Cramer's rules (thay vì biểu diễn bằng đoạn thẳng thì cách này biểu diễn bằng đường thẳng nên sẽ có các cases như roi125 hay roi 125padding) - "./intersection"
    ## 6.2. Tìm giao điểm bằng thư viện Shapely (tránh được các cases như roi125 hay roi125_padding như bị miss ở 1 vài cases như roi93_padding) - "./intersections1"