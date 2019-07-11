from flask import Flask, render_template, request, redirect,Response
from flask_restful import Resource, Api
import json, string, random, os
from urllib import urlencode, quote_plus
from urllib2 import urlopen, Request
from urlparse import urlparse, urlsplit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import razorpay
import pandas as pd
import os
import json

app = Flask(__name__)
api = Api(app)



app.static_folder = 'static'

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/main')
def mai():
    return render_template('main.html')

@app.route('/qr')
def qr():
    return render_template('qr.html')



#################################
@app.route('/nfc')
def nfc():
    return render_template('nfc.html')

@app.route('/nfcpy', methods=["POST","GET"])
def nfcc():
    if request.method == "POST":
        # vpa=request.form['VPA']
        vpa= lview()
        amn=request.form['Amount']
        mer=request.form['Merchant']
        uri="upi://pay?pa="+vpa+"&pn="+mer+"&am="+amn+"&tn=&mam=null&cu=INR"
        os.system('python ndef_url.py -u \"'+uri+'\"')
        return Response(status=200)
    else:
        return Response(status=400)


####################################

@app.route('/preadhaar')
def preadhaar():
    return render_template('preadhaar.html')

@app.route('/adhaar')
def adhaar():
    return render_template('adhaar.html')

@app.route('/gateway')
def gateway():
    return render_template('razor.html')
    
@app.route('/config')
def lconf():
    vpa = request.args.get('vpa')
    with open('config.json', 'r') as f:
        config = json.load(f)

    #edit the data
    config['vpa'] = vpa

    #write it back to the file
    with open('config.json', 'w') as f:
        json.dump(config, f)
    return "1"


@app.route('/configview')
def lview():
     with open('config.json', 'r') as f:
        config = json.load(f)
        vpa= config['vpa']
        return vpa

#Razor Pay Gateway
razorpay_client = razorpay.Client(auth=("rzp_test_KJaS279k3XSHLG", "3L6pkF6GTek6blM6T95cPign"))

@app.route('/charge', methods=['POST'])
def razooor():
    # amount = 5100
    # payment_id = request.form['razorpay_payment_id']
    # razorpay_client.payment.capture(payment_id, amount)
    # return json.dumps(razorpay_client.payment.fetch(payment_id))
    return render_template('success.html')

##################################


########## LOGS File ####
@app.route('/log', methods = ['POST', 'GET'])
def log():
     if request.method == 'POST':

         trx_id = request.form['id']
         lamount = request.form['amount']
         lstatus = request.form['status']
         lmethod = request.form['method']
         import csv
         import datetime
         import time
         ts = time.time()
         st = datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y %I:%M %p')
         fields=[st,trx_id,lamount,lstatus,lmethod]
         with open(r'logs.csv', 'a') as f:
              writer = csv.writer(f)
              writer.writerow(fields)
         return '1'
     if request.method == 'GET':
         df = pd.read_csv('logs.csv')


         pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

         html_string = '''
            <html>
            <head><title>Logs</title></head>
            <link rel="stylesheet" type="text/css" href='/static/stylesheets/logstyle.css'/>
            <body>
            <div style="position:absolute; left:50px;z-index: 10;"> <img src="https://image.flaticon.com/icons/svg/61/61752.svg" alt="" onclick="window.history.go(-1); return false;" width="30vw;"> </div>
            <div title><h1 >Payment Logs</h1></div>
                {table}
            </body>
            </html>.
            '''

         # OUTPUT AN HTML FILE
         with open('templates/myTable.html', 'w') as f:
            f.write(html_string.format(table=df.to_html(classes='mystyle')))

                    #  df.to_html('templates/myTable.html')
         return render_template('myTable.html')



@app.route('/upi')
def upi():
    return render_template('upi.html')


               
            

           
          
            
            


##############################333

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            result = request.form
            fjson = 'data.json'

            if not os.path.isfile(fjson):
                with open(fjson, 'w+') as outfile:
                    json.dump({}, outfile)

            number = '91'+ result['mobile'].strip()
            recipient = result['email'].strip()
            url = result['querystring'].strip()
            
            if len(url) == 0 or len(recipient) == 0 or len(number) == 0:
                errorResp = {}
                errorResp['status'] = 'Empty url or email or number'
                return json.dumps(errorResp)
            shorturl= url_generator()

            with open(fjson) as json_file:
                json_decoded = json.load(json_file)

            for key, value in json_decoded.items():
                 if value == url:
                    emailStatus = send_mail(recipient, request.url_root+key, value)
                    message = "Please pay using this link: " + request.url_root+key
                    smsResp = sendSMS(number, message)
                    exitResp = {}
                    exitResp['status'] = 'success'
                    exitResp['shortURL'] = request.url_root+key
                    exitResp['upiLink'] = value
                    exitResp['emailStatus'] = emailStatus
                    exitResp['smsResp'] = 'smsResp'
                    exitJson = json.dumps(exitResp)
                    return str(exitJson)

            json_decoded[shorturl] = url

            with open(fjson, 'w+') as json_file:
                json.dump(json_decoded, json_file)

            emailStatus = send_mail(recipient, request.url_root+shorturl, json_decoded[shorturl])
            message = "Please pay using this link: " + request.url_root+shorturl
            smsResp = sendSMS(number, message)
            newResp = {}
            newResp['status'] = 'success'
            newResp['shortURL'] = request.url_root+shorturl
            newResp['upiLink'] = json_decoded[shorturl]
            newResp['emailStatus'] = emailStatus
            newResp['smsResp'] = 'smsResp'
            newJson = json.dumps(newResp)
            return str(newJson)
        except:
            errorResp = {}
            errorResp['status'] = 'failed'
            return json.dumps(errorResp)
        

    return render_template('index.html')


class URLSHORT(Resource):
    def get(self, url):
        try:
            with open('data.json') as json_file:
                json_decoded = json.load(json_file)
            if url in json_decoded:
                return redirect(json_decoded[url])
            errorResp = {}
            errorResp['status'] = 'Wrong ShortURLy!'
            return json.dumps(errorResp)
        except:
            errorResp = {}
            errorResp['status'] = 'Something Wrong! Please retry.'
            return json.dumps(errorResp)
        


def url_generator(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def sendSMS(number, message):
    apikey = 'uNrlHnU77Aw-Q0xHYOSoi0WLHxVxNC4tQS8aTAoXD7'
    numbers = number
    data =  urlencode({'apikey': apikey, 'numbers': numbers, 'message' : message})
    data = data.encode('utf-8')
    request = Request("https://api.textlocal.in/send/?")
    f = urlopen(request, data)
    fr = f.read()
    return(fr)


def send_mail(recipient, shorturl, url):

    user="Shubhashree10sep@gmail.com"
    pwd="9415736117"

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = recipient
    msg['Subject'] = "New Payment Request From Blah Blah Blah"
    body = "Please pay using this link {0} ".format(shorturl)
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        message = msg.as_string()
        server.sendmail(msg['From'], msg['To'], message)
        server.close()
        return "Success"
    except:
        return "Failed"


api.add_resource(URLSHORT, '/<url>')

if __name__ == '__main__':
   app.run(host='0.0.0.0',debug=True)
