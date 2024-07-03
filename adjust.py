import cv2
import numpy as np
import pickle
import sys
import keyboard
import subprocess
import os

def nothing(x):
    pass

def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def is_pixel_row_white(x, T):
    for i in x:
        if i < T:
            return False
    return True

def is_pixel_column_white(x, T):
    for i in x:
        if i[0] < T:
            return False
    return True

def alphabet_vertical_allignment():
    alpha = storage_dict[0]
    short = ['g', 'j', 'p', 'q', 'y']
    average = ['a', 'c', 'e', 'i', 'm', 'n', 'o', 'r', 's', 'u', 'v', 'w', 'x', 'z']
    tall = ['b', 'd', 'f', 'h', 'k', 'l', 't']
    tallest = -1
    for ch in tall:
        if alpha[ord(ch) - 97].shape[0] > tallest:
            tallest = alpha[ord(ch) - 97].shape[0]
    shortest = -1
    for ch in short:
        if alpha[ord(ch) - 97].shape[0] > shortest:
            shortest = alpha[ord(ch) - 97].shape[0]
    summ = 0
    for ch in average:
        summ += alpha[ord(ch) - 97].shape[0]
    average_height = summ // len(average)
    diff_t = tallest - average_height
    diff_s = shortest - average_height
    for i in range(26):
        ch = chr(i + 97)
        if ch not in tall:
            padd = np.zeros([diff_t, alpha[i].shape[1]], dtype=np.uint8)
            padd.fill(255)
            alpha[i] = cv2.vconcat([padd, alpha[i]])
        if ch not in short:
            padd = np.zeros([diff_s, alpha[i].shape[1]], dtype=np.uint8)
            padd.fill(255)
            alpha[i] = cv2.vconcat([alpha[i], padd])
    storage_dict[0] = alpha
    save_obj(storage_dict, "storage_dict")

def punctiation_vertical_allignment():
    punct = storage_dict[1]
    average = [3, 4, 6, 7, 9, 10, 11, 12, 13, 14, 15]
    summ = 0
    for ch in average:
        summ += punct[ch].shape[0]
    average_height = summ // len(average)
    for i in [1, 2, 5, 8]:
        padd = np.zeros([average_height - punct[i].shape[0], punct[i].shape[1]], dtype=np.uint8)
        padd.fill(255)
        punct[i] = cv2.vconcat([padd, punct[i], padd])
    for i in [0]:
        padd = np.zeros([(average_height - punct[i].shape[0]) // 2, punct[i].shape[1]], dtype=np.uint8)
        padd.fill(255)
        punct[i] = cv2.vconcat([padd, punct[i], padd])
    storage_dict[1] = punct
    save_obj(storage_dict, "storage_dict")

def process_characters(x, i, T, img_crop):
    y_top = 0
    while y_top < len(img_crop):
        if is_pixel_row_white(img_crop[y_top], T):
            y_top += 1
        else:
            break
    y_bottom = len(img_crop) - 1
    while y_bottom > 0:
        if is_pixel_row_white(img_crop[y_bottom], T):
            y_bottom -= 1
        else:
            break
    img_crop = img_crop[y_top:y_bottom, 0:img_crop.shape[1]]
    return img_crop

def apply_segmentation(img, T, save):
    global storage_dict
    font = cv2.FONT_HERSHEY_SIMPLEX
    char_types = {'alphabet': 26, 'punctuation': 16, 'number': 9}
    captions = ['alphabet', 'punctuation', 'number']
    img_backup = img.copy()
    character_class_BR = [[0, 0] for i in char_types]
    if save:
        storage_dict = [dict() for i in char_types]
    active = False
    count = 0
    for i in range(len(img)):
        row = img[i]
        if count == len(captions):
            break
        if active:
            if is_pixel_row_white(row, T):
                character_class_BR[count][1] = i
                count += 1
                active = False
            else:
                pass
        else:
            if is_pixel_row_white(row, T):
                pass
            else:
                character_class_BR[count][0] = i
                active = True
    for x in range(len(character_class_BR)):
        char_max = char_types[captions[x]]
        ans = []
        bounds_X = character_class_BR[x]
        active = False
        count = 0
        for i in range(img.shape[1]):
            if count == char_max:
                break
            column = img_backup[bounds_X[0]:bounds_X[1], i:i+1]
            if active:
                if is_pixel_column_white(column, T):
                    ans[count][1] = [bounds_X[1], i]
                    count += 1
                    active = False
                else:
                    pass
            else:
                if is_pixel_column_white(column, T):
                    pass
                else:
                    ans.append([[bounds_X[0], i], [0, 0]])
                    active = True
        for i in range(len(ans)):
            temp = ans[i]
            if save:
                storage_dict[x][i] = process_characters(x, i, T, img_backup[temp[0][0]:temp[1][0]+1, temp[0][1]:temp[1][1]+1])
            else:
                cv2.rectangle(img, pt1=(temp[0][1], temp[0][0]), pt2=(temp[1][1], temp[1][0]), color=(0, 255, 255), thickness=1)
    if save:
        save_obj(storage_dict, "storage_dict")
        return
    return img

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python adjust.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    storage_dict = []
    imgray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    cv2.namedWindow('image')

    cv2.createTrackbar('T', 'image', 0, 255, nothing)
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'image', 0, 1, nothing)

    t = -1
    s = -1

    while True:
        t = cv2.getTrackbarPos('T', 'image')
        s = cv2.getTrackbarPos(switch, 'image')
        (thresh, img) = cv2.threshold(imgray, t, 255, cv2.THRESH_BINARY)
        if s == 1:
            img1 = apply_segmentation(img.copy(), t, False)
            cv2.imshow('image', img1)
        else:
            cv2.imshow('image', img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
            
    if s == 1:
        apply_segmentation(img, t, True)
        alphabet_vertical_allignment()
        punctiation_vertical_allignment()
    cv2.destroyAllWindows()
    
