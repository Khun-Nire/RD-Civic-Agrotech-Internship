import cv2
import numpy as np

kernel = np.ones((3,3),np.uint8)

lowgreen = np.array([30, 20, 50])
uppgreen = np.array([85, 255, 255])

lowrainbow = np.array([0, 50, 150])
upprainbow = np.array([180, 255, 255])

def Petals_Detection():
    cap = cv2.VideoCapture(0)#เปิดกล้องหน้าโน๊ตบุค
    check , Photo = cap.read()#รับภาพจากกล้อง frame ต่อ frame
    cap.release()#เคลีย list ของภาพ

    if not check:#หากเกิดความผิดพลาดในการอ่านภาพให้ส่งค่าตัวแปรทั้งหมดกลับเป็น 0 และ 0
        return [0, 0]

    #Photo = cv2.resize(Photo,(1280,720)) #Original: 2688*1520, resize: 1920*1080, 1280*720
    #Photo = Photo[0:720, 0:1280]
    y_Size_of_image, x_Size_of_image, _ = Photo.shape
    hsv = cv2.cvtColor(Photo, cv2.COLOR_BGR2HSV)
    maskgreen = cv2.inRange(hsv,lowgreen,uppgreen)
    erosion = cv2.erode(maskgreen,kernel,iterations=3)
    dilation = cv2.dilate(erosion,None,iterations=3)
    contour,_ = cv2.findContours(dilation,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #สร้างเส้นเค้าโครง

    y_max, y_min, x_max, x_min = None, None, None, None

    for cn in contour:
        if len(cn) > 0:  # Ensure there is at least one point in the contour
            x_min_contour = cn[cn[:, :, 0].argmin()][0][0]
            x_max_contour = cn[cn[:, :, 0].argmax()][0][0]
            y_min_contour = cn[cn[:, :, 1].argmin()][0][1]
            y_max_contour = cn[cn[:, :, 1].argmax()][0][1]

            # Initialize boundary points if they are None
            if x_min is None or x_max is None or y_min is None or y_max is None:
                x_min, x_max, y_min, y_max = x_min_contour, x_max_contour, y_min_contour, y_max_contour
            else:
                # Update the boundary points
                x_min = min(x_min, x_min_contour)
                x_max = max(x_max, x_max_contour)
                y_min = min(y_min, y_min_contour)
                y_max = max(y_max, y_max_contour)

    if y_max == None:
        y_max = 0
    if y_min == None:
        y_min = 0
    if x_max == None:
        x_max = 0
    if x_min == None:
        x_min = 0

    print(x_max, x_min, y_max, y_min)
    color_boundary = maskgreen[y_min:y_max, x_min:x_max]
    green_pixels_count = cv2.countNonZero(color_boundary)
    total_pixels = (x_max-x_min) * (y_max-y_min)

    print("total_pixels: ", total_pixels)

    green_percentage = 0
    rainbow_percentage = 0

    if len(contour) > 0:
        green_percentage = (green_pixels_count / total_pixels) * 100

    cv2.drawContours(Photo, contour, -1, (0,255,0), 2)

    cropgreen = hsv[y_min:y_max, x_min:x_max]
    maskrainbow = cv2.inRange(cropgreen,lowrainbow,upprainbow)
    erosion = cv2.erode(maskrainbow,kernel,iterations=3)
    dilation = cv2.dilate(erosion,None,iterations=3)
    contour,_ = cv2.findContours(dilation,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #สร้างเส้นเค้าโครง

    rainbow_pixels_count = cv2.countNonZero(maskrainbow)
    Ready_for_harvest = False

    if len(contour) > 0:
        rainbow_percentage = (rainbow_pixels_count / total_pixels) * 100
        if rainbow_percentage > green_percentage:
            Ready_for_harvest  = True
            print("Ready for harvest.")
        else:
            print("Not ready for harvest.")

    cv2.drawContours(Photo, contour, -1, (255,255,255), 2)
    cv2.imshow("Detection", Photo)
    print("x/y-Size:", x_Size_of_image, y_Size_of_image)
    print("x-max/min, y-max/min:", x_max, x_min, y_max, y_min)
    print("Percentage of green: ", green_percentage)
    print("Percentage of rainbow: ", rainbow_percentage)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return Ready_for_harvest

Petals_Detection()