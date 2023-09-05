# Python code to convert an image to ASCII image.
import os
import argparse
import time
from moviepy.editor import VideoFileClip
import numpy as np
import cv2;

from PIL import Image

# gray ratio level values from:
# http://paulbourke.net/dataformats/asciiart/

# 70 levels of gray
gScale70 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# 10 levels of gray
gScale10 = '@%#*+=-:. '

def getAverageGrayscale(imagePortion, ifVid):

    """
    Take a portion of the original grayscale image,
    then returns a single average grayscale level of the entire portion
    """
    
    if ifVid:
        return np.average(imagePortion)
        
    imageArray = np.array(imagePortion)

    width, height = imageArray.shape

    imageArray = imageArray.reshape(width * height)

    return np.average(imageArray)

def covertImageToAscii(image, multiplyer, detailed, imageHeight, imageWidth, ASCIIHeight, ASCIIWidth, blockHeight, blockWidth, ifVid):

    """
    Given the image file and the dimensions, 
    returns an array of grayscale value strings that forms an image
    """

    global gScale70, gScale10

    # an array of grayscale value strings
    asciiData = []
    
    for i in range(ASCIIHeight):
        # getting the width of the portion of the image to crop
        y1 = int(i*blockHeight)
        y2 = int((i+1)*blockHeight)

        # correct last tile
        if(i == ASCIIHeight - 1):
            y2 = imageHeight

        asciiData.append("")

        for j in range(ASCIIWidth):

            # getting the height of the portion of the image to crop
            x1 = int(j*blockWidth)
            x2 = int((j+1)*blockWidth)

            # correct last tile
            if(j == ASCIIWidth - 1):
                x2 = imageWidth

            # cropping the original image at the specified area
            img = image.crop((x1, y1, x2, y2))

            # get a single average grayscale value of the portion
            averageGScaleOG = int(getAverageGrayscale(img, ifVid))
            
            if(detailed):
                averageGScale = gScale70[int((averageGScaleOG * 69)/255)]
            else:
                averageGScale = gScale10[int((averageGScaleOG * 9) / 255)]

            asciiData[i] += averageGScale
	
    # return txt image
    return asciiData

def main():
    parserDescription = "Image to ASCII image converter"
    parser = argparse.ArgumentParser(description = parserDescription)
    parser.add_argument("-name", dest="file_name", required=True)
    parser.add_argument("-resize", dest="multiplyer", required=False) # resizing using pure percentage on h and w
    parser.add_argument("-fit", dest="fit_height", required=False)    # set a specific ascii image height
    parser.add_argument("-s", dest="get_size", action="store_true")
    parser.add_argument("-d", dest="detailed", action="store_true")  # lvl 70 / 10 grayscale
    parser.add_argument("-v", dest="not_image", action="store_true")
    parser.add_argument("-skip", dest="skip", required=False) # skipping frames in vid
    
    args = parser.parse_args()
    
    if not args.not_image:
        # Section for image conversion
        # Main variables
        # imageWidth, imageHeight
        # ASCIIWidth, ASCIIHeight
        # blockWidth,blockHeight
        # blank_image
        # asciiData, newFile
        
        originalImageFile = "assets/images/" + args.file_name
        
        # convert the original image into a grayscale image
        image = Image.open(originalImageFile).convert('L')
        
        finalImage = 'result.txt'
        
        multiplyer = 1
        if args.multiplyer:
            multiplyer = float(args.multiplyer)
  
        print('Generating ASCII image...')
        
        # Calculating dimensions of image, ascii art, and individual ascii block
        imageWidth = image.size[0]
        imageHeight = image.size[1]
        ASCIIWidth = imageWidth
        ASCIIHeight = imageHeight

        # get the size of original image then quit program
        if args.get_size:
            print("Input image dimensions: %d x %d" % (imageHeight, imageWidth))
            print("Quitting...")
            return
            
        # calculates appropriate width to maintain aspect ratio
        # reset multiplyer if value other than 1 exists
        if args.fit_height:
            if multiplyer != 1:
                multiplyer = 1
                print("A fit value was defined, multiplyer value was reset")
            ASCIIHeight = int(args.fit_height)
            ASCIIWidth = int(imageHeight / int(imageHeight / ASCIIHeight))
            
        # resize ascii image using purely percentages
        if(multiplyer != 1):
            ASCIIWidth = int(imageWidth * multiplyer)
            ASCIIHeight = int(imageHeight * multiplyer)
            image = image.resize((imageWidth, imageHeight))
        
        # calculates image dimensions each ascii tile represents
        blockWidth = int(imageWidth / ASCIIWidth)
        blockHeight = int(imageHeight / ASCIIHeight)
        
        # creating a blank image to write the ascii onto
        blank_image = np.zeros((ASCIIHeight, ASCIIWidth, 3), np.uint8)
        
        print("Input image dimensions: %d x %d" % (imageHeight, imageWidth))
        print("ASCII image dimensions: %d x %d" % (ASCIIHeight, ASCIIWidth))
        print("ASCII tile dimensions: %d x %d" % (blockHeight, blockWidth))
        
        # Insufficient ASCII tile dimensions crashes the program
        if blockWidth < 1:
            print("Insufficient width (ASCII tile width < 1)")
            print("Quitting...")
            return
        
        if blockHeight < 1:
            print("Insufficient height (ASCII tile height < 1)")
            print("Quitting...")
            return 
    
        asciiData = covertImageToAscii(image, multiplyer, args.detailed, imageHeight, imageWidth, ASCIIHeight, ASCIIWidth, blockHeight, blockWidth, False)

        newFile = open(finalImage, 'w')

        # write image to file row by row
        for row in asciiData:
        #    print(row)
            newFile.write(row + '\n')

        newFile.close()
        
        print("ASCII image exported as: %s" % finalImage)
        
    else:
        # Section for moviepy
        # Doesn't write to any file. Display result in terminal
        # Main variables: 
        # vidWidth, vidHeight
        # ASCIIWidth, ASCIIHeight
        # blockWidth, blockHeight
        # asciiData, skip
        
        originalClipFile = "assets/motions/" + args.file_name
        clip = VideoFileClip(originalClipFile)
        vidWidth, vidHeight = clip.size
        ASCIIWidth = vidWidth
        ASCIIHeight = vidHeight
        skip = 0
        
        print("Size of input: %d x %d" %(vidHeight, vidWidth))
        
        if args.fit_height:
            fit_height = int(args.fit_height)
            if fit_height >= vidHeight:
                print("No need to change to a new Fit, video height is already smaller or equal to the provided fit height")
            else:
                ASCIIWidth = int(vidWidth / int(vidHeight / fit_height))
                ASCIIHeight = fit_height
                
        clip.write_videofile("generatedVid.mp4", audio=False)
        
        blockWidth = int(vidWidth / ASCIIWidth)
        blockHeight = int(vidHeight / ASCIIHeight)
        
        print("Input video dimensions: %d x %d" % (vidHeight, vidWidth))
        print("ASCII video dimensions: %d x %d" % (ASCIIHeight, ASCIIWidth))
        print("ASCII tile dimensions: %d x %d" % (blockHeight, blockWidth))
        
        # Insufficient ASCII tile dimensions crashes the program
        if blockWidth < 1:
            print("Insufficient width (ASCII tile width < 1)")
            print("Quitting...")
            return
        
        if blockHeight < 1:
            print("Insufficient height (ASCII tile height < 1)")
            print("Quitting...")
            return 
            
        if args.skip:
            skip = int(args.skip)
            print("Applying", skip, " frames skipping intervals")
            
        #Section for OpenCV
        cap = cv2.VideoCapture("generatedVid.mp4")
        frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Note: This function combines cv2 grab() and retreive()
        
        #Goofy ah texts
        time.sleep(1.2)
        print("") #newline
        print("Cooking up the animation...")
        time.sleep(1.5)
        print("Clearing screen in")
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        
        os.system("cls | clear")
        
        # converting each frame then printing them out
        # one by one and 
        # row by row
        for frameCounter in range(frameCount):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frameCounter) # setting the frame number to grab from
            res, frame = cap.read(); 
            image = Image.fromarray(frame);  # opencv returns arrays, use fromarray to convert to PIL image
            asciiData = covertImageToAscii(image, 1, args.detailed, vidHeight, vidWidth, ASCIIHeight, ASCIIWidth, blockHeight, blockWidth, True)
            time.sleep(0.05)
            os.system("cls")
            for row in asciiData:
                print(row)
            # frameCounter += skip
        
        

if __name__ == '__main__':
    main()
