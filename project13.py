import cv2,time
import pandas
import datetime
import imutils
import psycopg2
import  smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from twilio.rest import Client
def recp(path):
    con=psycopg2.connect(database= 'cctv',user='postgres',password='sound',host= 'localhost')
    cur=con.cursor()
    cur.execute(""" SELECT email FROM auth_user""")
    blob = cur.fetchall()
    cur.close()
    con.close()
    for i in blob:
      sendemailto(path,i[0])
'''def callprog():
    account_sid ='AC4ce914de85d4207568ad69be197b7ce4'
    auth_token = 'c533faec459ce956b310a3048a63ca2c'
    client = Client(account_sid, auth_token)
    
    call = client.calls.create(
                        twiml='<Response><Say>Alert Soundarya Have a nice day...</Say></Response>',
                        to='+919698927504',
                        from_='+18304606290'
                    )

    print(call.sid)'''
def sendemailto(filename,receiver):
    subject = "Alert CCTV"
    body = "A person detected kindly login and check"
    sender_email = "cctvsurvillence70@gmail.com"#your mail id
    receiver_email = receiver
    password = "sound0307"#your password
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    # Add body to email
    message.attach(MIMEText(body, "plain"))    
    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download qthis automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        
        # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    # Add header as key/value pair to attachment part
    part.add_header("Content-Disposition",f"attachment; filename= {filename}",)

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
            print("emailsend")
    except Exception as e:
        print("Check the internet",e)
print(__name__)
if True:
    first_frame=None
    status_list=[None,None]
    global times
    times=[]
    lastUploaded = datetime.datetime.now()
    df=pandas.DataFrame(columns=["Start","End"])
    time.sleep(2.5)
    video=cv2.VideoCapture(0)
    motionCounter = 0
    c=0
    while True:
        check,frame=video.read()
        status=0
        timestamp = datetime.datetime.now()
        frame = imutils.resize(frame, width=1080)
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray=cv2.GaussianBlur(gray, (21,21),0)
        if first_frame is None:
            first_frame=gray.copy().astype("float")
            continue
        
        cv2.accumulateWeighted(gray, first_frame, 0.5)
        delta_frame = cv2.absdiff(gray, cv2.convertScaleAbs(first_frame))
        
        thresh_delta=cv2.threshold(delta_frame,5,255,cv2.THRESH_BINARY)[1]
        thresh_frame=cv2.dilate(thresh_delta,None,iterations=2)
        (cnts,image)=cv2.findContours(thresh_frame.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in cnts:
            if cv2.contourArea(contour)<1000:
                continue
            status=1
            (x,y,w,h)=cv2.boundingRect(contour)
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
            
        cv2.imshow('Capturing img',frame)
        cv2.imshow('Capturing',gray)
        cv2.imshow('delta',delta_frame)
        cv2.imshow('thresh_delta',thresh_delta)
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        if status == 1:
            if (timestamp - lastUploaded).seconds >= 3.0:
                motionCounter += 1
                if motionCounter >= 20:
                    path = timestamp.strftime("%b-%d_%H_%M_%S" + ".jpg")
                    cv2.imwrite("media\\"+path,frame)
                    c+=1
                    if c==10:
                        recp("media\\"+path)
                        #callprog()
                        c=0
                    times.append(datetime.datetime.now())
                    lastUploaded = timestamp
                    motionCounter = 0
        else:
            motionCounter = 0
        key=cv2.waitKey(1)& 0xFF
        if key==ord('q'):
            break
    for i in range(0,len(times),2):
        try:
            df=df.append({'Start':times[i],"End":times[i+1]},ignore_index=True)
        except:
            print("one miss")
    print(times)
    df.to_csv("Times.csv")
    video.release()
    cv2.destroyAllWindows()