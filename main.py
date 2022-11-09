import cv2
import numpy as np

from aux_scripts import find_dominant_color, compare_if_same_color

MATCHER = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
SIFT = cv2.SIFT_create()
DISTANCE = 50
RATIO_COLOR = 0.25


# Detect sift keypoints and descriptors for an img of a bottle cap
def get_kp_and_dcp(img: np.ndarray):
    kp_1, d_1 = SIFT.detectAndCompute(img, None)
    return kp_1, d_1


# Draw kp from an image path
def draw_kp(img_path: str, kp_1: tuple):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_kp = cv2.drawKeypoints(gray, kp_1, img, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow('image', img_kp)
    cv2.waitKey(0)


def read_img(img_path: str):
    return cv2.cvtColor(cv2.imread(img_path), 1)


def get_pix_kp_img(matches: list, cap_kp: tuple, photo_kp: tuple):
    cap_kp_lst, photo_kp_lst = set(), set()

    for mat in matches:
        # Get the matching keypoints for each of the images
        cap_idx = mat.queryIdx
        photo_idx = mat.trainIdx

        # x - columns
        # y - rows
        # Get the coordinates
        (x1, y1) = cap_kp[cap_idx].pt
        (x2, y2) = photo_kp[photo_idx].pt

        cap_kp_lst.add((int(x1), int(y1)))
        photo_kp_lst.add((int(x2), int(y2)))

    return cap_kp_lst, photo_kp_lst


def compare_two_imgs(img_cap: np.ndarray, img_photo: np.ndarray):
    # Get the keypoints and descriptors
    kp_cap, dcp_cap = get_kp_and_dcp(img_cap)
    kp_photo, dcp_photo = get_kp_and_dcp(img_photo)

    matches = MATCHER.match(dcp_cap, dcp_photo)
    matches = sorted(matches, key=lambda x: x.distance)[:30]

    _, lst_pix = get_pix_kp_img(matches, kp_cap, kp_photo)
    return lst_pix


def detect_squares(points: set, max_distance: int):
    centroid_distance = []
    already_in_square = set()
    for origin_point in points:
        # p_X is on the horizontal axis and p_Y is on the vertical axis
        pMaxX, pMinX, pMaxY, pMinY = origin_point, origin_point, origin_point, origin_point
        already_in_square.add(origin_point)

        centroid_list = []
        for p in points:
            # Checks if the cap is in the range of the max caps
            if (distance(pMaxX, p) < max_distance
                or distance(pMinX, p) < max_distance
                or distance(pMaxY, p) < max_distance
                or distance(pMinY, p) < max_distance) \
                    and p not in already_in_square:
                already_in_square.add(p)
                centroid_list.append(p)
                # Check horizontally
                if p[0] > pMaxX[0]:
                    pMaxX = p
                elif p[0] < pMinX[0]:
                    pMinX = p
                # Check vertically
                if p[1] > pMaxY[1]:
                    pMaxY = p
                elif p[1] < pMinY[1]:
                    pMinY = p
        if len(centroid_list) > 5:
            pTopLeft = (pMinX[0], pMaxY[1])
            pBotRight = (pMaxX[0], pMinY[1])
            centroid = np.array(centroid_list).mean(axis=0)
            centroid = tuple([int(i) for i in centroid])
            dis = max(distance(centroid, pTopLeft), distance(centroid, pBotRight))
            centroid_distance.append([centroid, dis])
    return centroid_distance


def distance(p1: tuple, p2: tuple):
    dist = ((abs(p1[0] - p2[0]) ** 2) + (abs(p1[1] - p2[1]) ** 2)) ** 0.5
    return dist


def get_cropped_squares(squares: list, img: np.ndarray):
    print(type(img))
    croppeds = []
    for s in squares:
        top = (int(abs(s[0][0] - s[1])), int(s[0][1] - s[1]))
        bot = (int(s[0][0] + s[1]), int(abs(s[0][1] + s[1])))

        h, w = bot[1] - top[1], bot[0] - top[0]
        croppeds.append([img[top[1]:top[1] + h, top[0]:top[0] + w].copy(), top, bot])
    return croppeds


def main():
    img_cap = './caps_imgs/t_cap_blue_2.jpg'
    img_test = './test_images/3.jpg'
    img_cap = read_img(img_cap)
    img_test = read_img(img_test)

    points = compare_two_imgs(img_cap=img_cap, img_photo=img_test)
    squares = detect_squares(points, DISTANCE)
    r = img_test.copy()
    croppeds = get_cropped_squares(squares, r)

    if len(croppeds) == 1:
        r = cv2.rectangle(r, croppeds[1], croppeds[2], (255, 100, 0), 3)
    else:
        color_cap = find_dominant_color(img_cap)
        for crop in croppeds:
            crop_img = crop[0]
            color_crop = find_dominant_color(crop_img)
            # Only apply color comparison when multiple matches of the same img
            if compare_if_same_color(color_crop, color_cap, RATIO_COLOR):
                r = cv2.rectangle(r, crop[1], crop[2], (255, 100, 0), 3)


    cv2.imshow("Original", img_cap)
    cv2.imshow("Result", r)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()
