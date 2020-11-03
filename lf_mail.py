#!/usr/bin/python3
import smtplib
import argparse

EPILOG = '''\ 
Text message via email:

T-Mobile – number@tmomail.net
Virgin Mobile – number@vmobl.com
AT&T – number@txt.att.net
Sprint – number@messaging.sprintpcs.com
Verizon – number@vtext.com
Tracfone – number@mmst5.tracfone.com
Ting – number@message.ting.com
Boost Mobile – number@myboostmobile.com
U.S. Cellular – number@email.uscc.net
Metro PCS – number@mymetropcs.com
'''

def usage():
    print("-u  | --user:   email account address   --user <sender>@gmail.com required = True")
    print("-pw | --passwd  email password  --passwd <password for email account>  required = True")
    print("-t  | --to      email send to   --to <reciever>@gmail.com required = True")
    print("-su | --subject email subject   --subject <title>  default Lanforge Report default = Lanforge Report")
    print("-b  | --body    email body      --body <body text> required = True")
    print("-s  | --smtp    smtp server     --smtp <smtp server>  default  smtp.gmail.com  default=smtp.gmail.com")
    print("-p  | --port    smtp port       --port <port>  default 465 (SSL)  default=465")


def main():

    parser = argparse.ArgumentParser(description="lanforge email",epilog=EPILOG,
    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-u", "--user",      type=str, help="email account   --user <sender>@gmail.com", required = True)
    parser.add_argument("-pw", "--passwd",   type=str, help="email password  --passwd <password for email account>", required = True)
    parser.add_argument("-t", "--to",        type=str, help="email send to   --to <reciever>@gmail.com", required = True)
    parser.add_argument("-su", "--subject",  type=str, help="email subject   --subject <title>  default Lanforge Report", default="Lanforge Report")
    parser.add_argument("-b", "--body",      type=str, help="email body      --body <body text>", required = True)
    parser.add_argument("-s,", "--smtp",     type=str, help="smtp server     --smtp <smtp server>  default  smtp.gmail.com ", default="smtp.gmail.com")
    parser.add_argument("-p,", "--port",     type=str, help="smtp port       --port <port>  default 465 (SSL)", default="465")


    args = None
    try:
       args = parser.parse_args()
    except Exception as e:
      print(e)
      usage()
      exit(2)        

    email_text = 'Subject: {}\n\n{}'.format(args.subject, args.body )
    try:
        server = smtplib.SMTP_SSL(args.smtp, int(args.port))
        server.ehlo()
        server.login(args.user,args.passwd)
        server.sendmail(args.user, args.to, email_text)
        server.close()

        print('email Sent!  smtp server: {} port: {}'.format(args.smtp, args.port))
    except:
        print('email failed')
        print("Is access for less secure apps setting has been turned on for the email account?")

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()
    print("Lanforge send email via smtp server")
