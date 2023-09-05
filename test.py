import numpy as np
import cv2

blank = np.zeros((300, 300, 3), np.uint8)
blank[:, :, :] = (255, 255, 255)

for i in range(6):
    img = cv2.putText(blank, 'hello', (10, i * 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    
cv2.imwrite(r"C:\Users\arze7\personal\github_projects\img2ASCII\test.jpg", img)
cv2.waitKey(30)