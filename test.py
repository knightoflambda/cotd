import cv2

template = cv2.imread("./res/col_temp.jpg")
gray = cv2.imread("./res/col_neg.jpg")
res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
print(res)