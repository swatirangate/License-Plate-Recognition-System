import cv2
import pytesseract
import mysql.connector
framewidth = 640
frameheight = 480
plateCascade = cv2.CascadeClassifier("C:\Program Files\haarcascade_russian_plate_number.xml")
minArea = 500
count = 0

color = (255, 0, 255)
cap = cv2.VideoCapture(0)           # to open the camera
cap.set(3, framewidth)
cap.set(4, frameheight)
cap.set(10,150)
while True:
    success, image = cap.read()         # to read the image
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    plates = plateCascade.detectMultiScale(gray_img, 1.1, 4)

    for(x, y, w, h) in plates:
        area = w * h
        if area >minArea:
            # to show rectangular box around number plate
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(image, "Number Plate", (x,y-5), cv2.FONT_HERSHEY_COMPLEX_SMALL,1,color,2)
            imgRoi = image[y:y+h,x:x+w]
            cv2.imshow("ROI", imgRoi)
    cv2.imshow("Result", image)
    if cv2.waitKey(1) & 0xFF == ord('s'):

        cv2.imshow("Result",image)
        cv2.waitKey(1000)
        count += 1


        # canny edge detection
        canny_edge = cv2.Canny(gray_img, 170, 200)

        # find contours based on edges
        # CHAIN_APPROX_SIMPLE to remove the redundant points and compresses the contour
        contours, new = cv2.findContours(canny_edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

        # initialize plate contour and x,y coordinates
        contour_with_plate = None
        plate = None
        x = None
        y = None
        w = None
        h = None

        # find the contour with corners and create ROI around it
        for contour in contours:
            # to calculate perimeter of contour and is true to set contour to be true
            perimeter = cv2.arcLength(contour, True)

            # to determine the shape of the plate
            approx = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
            if len(approx) == 4:  # see whether its rectangle
                contour_with_plate = approx
                x, y, w, h = cv2.boundingRect(contour)
                plate = gray_img[y:y + h, x:x + w]
                break

        # remove noise
        # plate = cv2.bilateralFilter(plate, 11, 17, 17)
        # (thresh, plate) = cv2.threshold(plate, 150, 180, cv2.THRESH_BINARY)

        # Text Recognition using pytesseract
        text = pytesseract.image_to_string(plate)

        #storing the data in the string format
        lplate = text.strip()

        # draw rectangular box around plate and write number plate text above it
        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
        image = cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 2)

        print("License Plate Number: ", lplate)
        cv2.imshow("License Plate Detection", image)

        # to connect with mysql database
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="1234", database="license")
        mycursor = mydb.cursor()

        query = """select * from info where l_plate = %s"""         # query passed to the database
        mycursor.execute(query, (lplate,))
        result = mycursor.fetchall()

        # to display the details about the number plate
        for i in result:
                print("License Plate Number =  ",i[0])
                print("Owner Name           =  ",i[1])
                print("Vehicle Class        =  ",i[2])
                print("Fuel Type            =  ",i[3])
                print("Registration No      =  ",i[4])
                print("Registration Date    =  ",i[5])
                print("Fitness Upto         =  ",i[6])
                print("PUCC No              =  ",i[7])
                print("Insurance Policy No  =  ",i[8])
        cv2.waitKey(0)
