
import socket
from icmplib import ping, multiping, resolve, Host, Hop
from icmplib import ICMPv4Socket, ICMPRequest, ICMPReply,PID,TimeExceeded,ICMPLibError
import time
import struct
import select
import random
from time import sleep
import os,webbrowser
import os
import sys
#######################################################################
#Nader Abdul Salam 201902984
#Tool for sending and receiving packets to measure delay and packet loss

import subprocess

#The subprocess module present in Python(both 2.x and 3.x) is used to run
#new applications or programs through Python code by creating new processes.
#It also helps to obtain the input/output/error pipes as well as the exit codes of various commands.

#The pipes module defines a class to abstract the concept of a pipeline —
#a sequence of converters from one file to another

def ping(n, hostname):#Nader

    #we added n as an argument in the function so that we can easily change the number of packets
    #We also added hostname so that we can easily change the target address
    #which we want to ping
    with open('output.txt', 'w') as output:

    #opens text file(output.txt) in direcctory to write in it

        process = subprocess.Popen("ping -n " + str(n) + ' ' + hostname, stdout=output)

        #The popen() function shall execute the command specified by the string command.
        #It shall create a pipe between the calling program and the executed command,
        #and shall return a pointer to a stream that can be used to either read from or write to the pipe.

        #ping is the command used in python to ping a target. Pinging a target sends packets to
        #and receives packets from a target in order to check if host is available and to measure the round trip time (the ping in other words)
        #in milliseconds for the packet to reach the host and for the response to return to the sender.
        #Ping also returns how many packets and how many were received and the percentage of package loss.
        #ping -n 4 "google.com" is the command written in command prompt on Windows to ping "google.com" 4 times
        #the command ping is used in both Windows and Unix-like systems
        #-n is used on Windows and -c on Unix to control the number of packets
        #the number after -n or -c is the number of packets
        #The ping command first sends an echo request packet to an address, then waits for a reply.
        #The ping is successful only if: the echo request gets to the destination, and. the destination is able
        #to get an echo reply back to the source within a predetermined time called a timeout.

        #stdout=output in order to print the output of the ping command in the output text file

        process.communicate()

        #.communicate() writes input, reads all output, and waits for the subprocess to exit.

        pingOutputString = open("output.txt", 'r').read()

        #stores text of output.txt in a string

        #print(pingOutputString)

        #we can use this to print output in terminal
        return pingOutputString

numberOfPackets = int(input("Insert Number of Packets: "))

#user inputs number of packets

hostName = input("Insert Domain Name: ")

#user inputs ip address or domain name

pingOutputString=ping(numberOfPackets, hostName)
filename='output.txt'
with open(filename) as f:
    content = f.readlines()
# you may also want to remove whitespace characters like \n at the end of each line
content = [x.strip() for x in content]
print(content)
#we call the funtion to ping the inputted ip address or domain name.
#we send and receive numberOfPackets packets to measure delay and packet loss.

########################################################################################################
#Hadi Kabrit 201902182
class Hops_Properties(Host):#class to store hop properties of every hop #hadi
    def __init__(self, address,avRTT,packets_sent,packets_received,distance):

        self._address=address
        self._distance = distance
        self.avRTT=avRTT
        self._packets_sent=packets_sent
        self._packets_received=packets_received


    def __repr__(self):
        return f'<Hop {self._distance} [{self._address}]>'
    # def missedHop(self):
    #     self._address="UNKOWN"
    #     self._distance = distance
    #     self.avRTT=avRTT
    #     self._packets_sent=packets_sent
    #     self._packets_received=packets_received

    @property
    def distance(self):
        return self._distance

#tracroute is a function develoved by ValentinBELYN in the icmplib library(Can be found on Github)
#traceroute takes as an input the ip adress of the host

def tracingAlg(address, count=2, interval=0.05, timeout=2, id=PID, #hadi
        hop1=1, max_hops=17, source=None, fast=False, **kwargs):
    address = resolve(address)

    socket = ICMPv4Socket(source)#ICMPv4Socket is a custom socket class
                                #creates a socket(socket.socket(family=socket.AF_INET,type=type,proto=socket.IPPROTO_ICMP))
                               #it sets for that socket a TTL and checks if broadcast support is enabled on the socket

    ttl = hop1
    dest_reached = False #true when we reach final destination
    hopsList = []#empty list

    while not dest_reached and ttl <= max_hops:
        hop_address = None # adress that the hop reached
        sentPackets = 0 #number of packets sent to final host
        recievedPackets = 0 #number of packets recieved by either current or final host

        #initializing round trip times
        #min_rtt = float('inf')#minimum round trip time
        avRTT = 0.0#average round trip time
        #max_rtt = 0.0#maximum round trip time

        for sequence in range(count):#for loop to keep varying packets sent
            req = ICMPRequest( #ICMP echo request
                                    #payload size initialized to 56
                                    #ttl initialized to 64
                destination=address,
                id=id, #id of the request(to match reply with request)
                sequence=sequence,
                ttl=ttl,#initialized in ICMPRequest to 64
                **kwargs)#traffic class

            try:
                socket.send(req)#sending request to host
                                  #raises errors such as socketunavailable and SocketBroadcastError
                sentPackets += 1

                reply = socket.receive(req, timeout)#listening for the reply of current or final hosts
                                                      #takes arguement timeout to set a timer in case socket doesn't recieve confirmation
                reply.raise_for_status()# function to make an exception if reply is not an icmp echo reply
                dest_reached = True

            except TimeExceeded:#icmplib error
                sleep(interval)#wait a given number of seconds

            except ICMPLibError:#Exception class for the icmplib package.
                continue

            hopAddress = reply.source# ip adress of the current or final host
            recievedPackets += 1 #increment packets recieved

            round_trip_time = (reply.time - req.time) * 1000# rtt in milliseconds
            avRTT += round_trip_time
            #min_rtt = min(round_trip_time, min_rtt)
            #max_rtt = max(round_trip_time, max_rtt)

            if fast:
                break

        if recievedPackets:
            avRTT = avRTT/recievedPackets #average rtt

            currentHop = Hops_Properties(#hop class created to store the properties bellow for every hop
                address=hopAddress,
                avRTT=avRTT,
                packets_sent=sentPackets,
                packets_received=recievedPackets,
                distance=ttl)

            hopsList.append(currentHop)#adding current hop to the list of hops
######################################################
        elif recievedPackets==False:
            currentHop = Hops_Properties(#hop class created to store the properties bellow for every hop
                address='Not Responding :/',
                avRTT=avRTT,
                packets_sent=sentPackets,
                packets_received=recievedPackets,
                distance=ttl)

            hopsList.append(currentHop)#adding current hop to the list of hops
########################################################
        ttl += 1#adding hop to reach the next destination

    socket.close()#closing socket

    return hopsList
##########################################################################################################3
#################################################################3
#h=input("Pleae enter a valid URL: ")

#ip_host = socket.gethostbyname(host)#get ip of host
###################################################################
def valid_ip_check(hostName):#nader
    try:
        ip_host = socket.gethostbyname(hostName)#get ip of host
        socket.inet_pton(socket.AF_INET, ip_host)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(ip_host)
        except socket.error:
            return False
        return ip_host.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True
###################################################################
v = valid_ip_check(hostName)
if v==False:
    html_doc4=""" #hadi
    <!DOCTYPE html>
    <html style="font-size: 16px;">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta charset="utf-8">
        <meta name="keywords" content="">
        <meta name="description" content="">
        <meta name="page_type" content="np-template-header-footer-from-plugin">
        <title>Page 4</title>
        <link rel="stylesheet" href="nicepage.css" media="screen">
    <link rel="stylesheet" href="Page-4.css" media="screen">
        <script class="u-script" type="text/javascript" src="jquery.js" defer=""></script>
        <script class="u-script" type="text/javascript" src="nicepage.js" defer=""></script>
        <meta name="generator" content="Nicepage 3.0.9, nicepage.com">
        <link id="u-theme-google-font" rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:100,100i,300,300i,400,400i,500,500i,700,700i,900,900i|Open+Sans:300,300i,400,400i,600,600i,700,700i,800,800i">
        <link id="u-page-google-font" rel="stylesheet" href="https://fonts.googleapis.com/css?family=Oswald:200,300,400,500,600,700">


        <script type="application/ld+json">{
    		"@context": "http://schema.org",
    		"@type": "Organization",
    		"name": "",
    		"url": "index.html"
    }</script>
        <meta property="og:title" content="Page 4">
        <meta property="og:type" content="website">
        <meta name="theme-color" content="#478ac9">
        <link rel="canonical" href="index.html">
        <meta property="og:url" content="index.html">
      </head>
      <body class="u-body"><header class="u-border-1 u-border-grey-25 u-clearfix u-header u-header" id="sec-ee72"><div class="u-clearfix u-sheet u-valign-middle u-sheet-1">
            <p class="u-text u-text-1">Hadi Kabrit&nbsp;<br>Nader Abdul Salam
            </p>
          </div></header>
        <section class="u-align-center u-clearfix u-image u-section-1" id="carousel_9911">
          <div class="u-clearfix u-sheet u-sheet-1">
            <h3 class="u-custom-font u-font-oswald u-text u-text-body-alt-color u-text-default u-text-1">URL NOT VALID</h3>
            <p class="u-custom-font u-heading-font u-text u-text-body-alt-color u-text-2">PLEASE ENTER VALID URL NEXT TIME;p </p>
          </div>
        </section>


        <footer class="u-align-center u-clearfix u-footer u-grey-80 u-footer" id="sec-08d6"><div class="u-clearfix u-sheet u-valign-middle u-sheet-1">
            <p class="u-small-text u-text u-text-variant u-text-1">Contact Us<br>
            </p>
          </div></footer>
        <section class="u-backlink u-clearfix u-grey-80">
          <a class="u-link" href="https://nicepage.com/html-templates" target="_blank">
            <span>Free HTML Templates</span>
          </a>
          <p class="u-text">
            <span>created with</span>
          </p>
          <a class="u-link" href="https://nicepage.com/html-website-builder" target="_blank">
            <span>HTML Website Builder</span>
          </a>.
        </section>
      </body>
    </html>
    """
    handle = open('page4.html',"w")
    handle.write(html_doc4)
    handle.close()
    webbrowser.open('file:///'+os.path.abspath('page4.html'))
    sys.exit("URL NOT VALID")
ip_host = socket.gethostbyname(hostName)#get ip of host
####################################################################
######################################################################################################################
html_doc2 =""" #hadi
<!DOCTYPE html>
<html style="font-size: 16px;">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta charset="utf-8">
    <meta name="keywords" content="INTUITIVE">
    <meta name="description" content="">
    <meta name="page_type" content="np-template-header-footer-from-plugin">
    <title>Page 2</title>
    <link rel="stylesheet" href="nicepage.css" media="screen">
<link rel="stylesheet" href="Page-2.css" media="screen">
    <script class="u-script" type="text/javascript" src="jquery.js" defer=""></script>
    <script class="u-script" type="text/javascript" src="nicepage.js" defer=""></script>
    <meta name="generator" content="Nicepage 3.0.9, nicepage.com">
    <link id="u-theme-google-font" rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:100,100i,300,300i,400,400i,500,500i,700,700i,900,900i|Open+Sans:300,300i,400,400i,600,600i,700,700i,800,800i">


    <script type="application/ld+json">{
		"@context": "http://schema.org",
		"@type": "Organization",
		"name": "",
		"url": "index.html"
}</script>
    <meta property="og:title" content="Page 2">
    <meta property="og:type" content="website">
    <meta name="theme-color" content="#478ac9">
    <link rel="canonical" href="index.html">
    <meta property="og:url" content="index.html">
  </head>
  <body class="u-body"><header class="u-border-1 u-border-grey-25 u-clearfix u-header u-header" id="sec-ee72"><div class="u-clearfix u-sheet u-valign-middle u-sheet-1">
        <p class="u-text u-text-1">Hadi Kabrit&nbsp;<br>Nader Abdul Salam
        </p>
      </div></header>
    <section class="u-align-center u-clearfix u-section-1" id="sec-b1d7">
      <div class="u-clearfix u-sheet u-sheet-1">
        <h2 class="u-text u-text-1">Pinging and Tracing</h2>
        <p class="u-text u-text-2">This process will take a while,Please wait patiently</p>
        <div class="u-expanded-width-sm u-expanded-width-xs u-uploaded-video u-video u-video-1">
          <div class="embed-responsive">
            <video class="embed-responsive-item" loop="" muted="" autoplay="autoplay" playsinline="">
              <source src="files/vidtake2.mp4" type="video/mp4">
              <p>Your browser does not support HTML5 video.</p>
            </video>
          </div>
        </div>
      </div>
    </section>


    <footer class="u-align-center u-clearfix u-footer u-grey-80 u-footer" id="sec-08d6"><div class="u-clearfix u-sheet u-valign-middle u-sheet-1">
        <p class="u-small-text u-text u-text-variant u-text-1">Contact Us<br>
        </p>
      </div></footer>
    <section class="u-backlink u-clearfix u-grey-80">
      <a class="u-link" href="https://nicepage.com/website-templates" target="_blank">
        <span>Website Templates</span>
      </a>
      <p class="u-text">
        <span>created with</span>
      </p>
      <a class="u-link" href="https://nicepage.com/html-website-builder" target="_blank">
        <span>Free WYSIWYG HTML Editor</span>
      </a>.
    </section>
  </body>
</html>
"""
handle = open('page2.html',"w")
handle.write(html_doc2)
handle.close()
webbrowser.open('file:///'+os.path.abspath('page2.html'))
# #################################################################3

hopsList = tracingAlg(ip_host)#hadi
print('Distance/TTL    Address    Average round-trip time')
last_distance = 0
for currentHop in hopsList:

     # See the Hop class for details
     print(f'{currentHop.distance}    {currentHop.address}    {currentHop.avRTT} ms')

     last_distance = currentHop.distance

print(hopsList)
print(hopsList[1].address)
###################################################################################################
html_doc3="""#hadi
<!DOCTYPE html>
<html style="font-size: 16px;">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta charset="utf-8">
    <meta name="keywords" content="The Results, The Results">
    <meta name="description" content="">
    <meta name="page_type" content="np-template-header-footer-from-plugin">
    <title>Page 3</title>
    <link rel="stylesheet" href="nicepage.css" media="screen">
<link rel="stylesheet" href="Page-3.css" media="screen">
    <script class="u-script" type="text/javascript" src="jquery.js" defer=""></script>
    <script class="u-script" type="text/javascript" src="nicepage.js" defer=""></script>
    <meta name="generator" content="Nicepage 3.0.9, nicepage.com">
    <link id="u-theme-google-font" rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:100,100i,300,300i,400,400i,500,500i,700,700i,900,900i|Open+Sans:300,300i,400,400i,600,600i,700,700i,800,800i">



    <script type="application/ld+json">{
		"@context": "http://schema.org",
		"@type": "Organization",
		"name": "",
		"url": "index.html"
}</script>
    <meta property="og:title" content="Page 3">
    <meta property="og:type" content="website">
    <meta name="theme-color" content="#478ac9">
    <link rel="canonical" href="index.html">
    <meta property="og:url" content="index.html">
  </head>
  <body class="u-body"><header class="u-border-1 u-border-grey-25 u-clearfix u-header u-header" id="sec-ee72"><div class="u-clearfix u-sheet u-valign-middle u-sheet-1">
        <p class="u-text u-text-1">Hadi Kabrit&nbsp;<br>Nader Abdul Salam
        </p>
      </div></header>
    <section class="u-clearfix u-section-1" id="sec-978d">
      <div class="u-clearfix u-sheet u-sheet-1">
        <p class="u-text u-text-1">"""+str(content[1])+"""</p>
        <p class="u-text u-text-2">"""+str(content[numberOfPackets+3])+"""</p>
        <p class="u-text u-text-3">"""+str(content[numberOfPackets+4])+"""</p>
        <p class="u-text u-text-4">"""+str(content[numberOfPackets+5])+"""</p>
        <p class="u-text u-text-5">"""+str(content[numberOfPackets+6])+"""</p>
      </div>
    </section>
    <section class="u-align-center u-clearfix u-section-2" id="carousel_3f5d">
      <div class="u-clearfix u-sheet u-sheet-1">
        <h1 class="u-text u-text-1">The Results</h1>
        <div class="u-table u-table-responsive u-table-1">
          <table class="u-table-entity u-table-entity-1">
            <colgroup>
              <col width="33%">
              <col width="33%">
              <col width="34%">
            </colgroup>
            <thead class="u-align-center u-grey-10 u-table-header u-table-header-1">
              <tr style="height: 72px;">
                <th class="u-border-4 u-border-white u-palette-2-light-1 u-table-cell u-table-cell-1">Hop Count</th>
                <th class="u-border-4 u-border-white u-palette-2-base u-table-cell u-table-cell-2">IP Adress</th>
                <th class="u-border-4 u-border-white u-palette-1-base u-table-cell u-table-cell-3">RTT</th>
              </tr>
            </thead>
            <tbody class="u-align-center u-table-alt-grey-10 u-table-body u-table-body-1">
              <tr style="height: 52px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[0].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[0].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[0].avRTT)+"""</td>
              </tr>
              <tr style="height: 52px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[1].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[1].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[1].avRTT)+"""</td>
              </tr>
              <tr style="height: 52px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[2].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[2].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[2].avRTT)+"""</td>
              </tr>
              <tr style="height: 52px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[3].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[3].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[3].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[4].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[4].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[4].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[5].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[5].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[5].avRTT)+"""</td>
              </tr>
              <tr style="height: 64px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[6].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[6].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[6].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[7].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[7].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[7].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[8].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[8].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[8].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[9].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[9].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[9].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[10].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[10].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[10].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[11].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[11].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[11].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[12].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[12].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[12].avRTT)+"""</td>
              </tr>
              <tr style="height: 62px;">
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[13].distance)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[13].address)+"""</td>
                <td class="u-border-4 u-border-white u-table-cell">"""+str(hopsList[13].avRTT)+"""</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>


    <footer class="u-align-center u-clearfix u-footer u-grey-80 u-footer" id="sec-08d6"><div class="u-clearfix u-sheet u-valign-middle u-sheet-1">
        <p class="u-small-text u-text u-text-variant u-text-1">Contact Us<br>
        </p>
      </div></footer>
    <section class="u-backlink u-clearfix u-grey-80">
      <a class="u-link" href="https://nicepage.com/css-templates" target="_blank">
        <span>CSS Templates</span>
      </a>
      <p class="u-text">
        <span>created with</span>
      </p>
      <a class="u-link" href="https://nicepage.com/html-website-builder" target="_blank">
        <span>HTML Website Builder</span>
      </a>.
    </section>
  </body>
</html>


"""

handle = open('page3333.html',"w")
handle.write(html_doc3)
handle.close()
webbrowser.open('file:///'+os.path.abspath('page3333.html'))
