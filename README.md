# Peer2Peer-DI
Elementary Peer 2 Peer System with distributed index.

-----
SETUP
-----

This project is best used with a VirtualEnv. Please use this if you wish by running in your terminal(bash):
    source ./bin/activate



When you start the registration server(RS), nothing will happen but it is running; it will print out respective messages
when a peer contacts it. 

For the RFC server, you must provide the hostname, location of the peer's RFC files, and the port number when you run 
the python code. Be sure that the RFC files are in the folder before running the file. On startup, the server will create an RFC index based off of what RFC files are in its folder. Once the server is running it will prompt the user for a command with the inviting words: "Enter command: ". 

After running this program to download the RFC files, you will find that in the designated folder for each peer, it will have two csv files: "singleTimes.csv" and totalTimes.csv", these two files hold time records of the download times. 

The singleTimes file holds the time it takes to download each file, it will be in the format: "<rfc num>,<time to download>\n"

The totalTimes file holds the cumulative time it takes to download the files. It will be in the format: "<num of files downloaded>, <time total>"

To run the registration server: 
	python reg_server.py
To run a peer server:
    python rfc_server.py <hostname> <RFC location> <port>

   	Example: python rfc_server.py localhost ./peers/P0 1234

------
INPUTS
------
Once the registration server is running, it will not take any inputs from the user, but will respond to the RFC servers.
THe user will interact only with the RFC servers and registration server will regulate on its own. 

Below are the commands a user can enter:

"Register" - the RFC server will automatically register itself with the RS by sending "Register: <port>" and the RFC server should print "Peer recieved" and "Cookie: <cookie num>"

"PQuery" - the RFC server will request from the RS a list of all active peers by sending "PQuery". It will print out the query for the user to see

"KeepAlive" - the RFC server will tell the RS to reset its TTL to 7200 by sending "KeepAlive: <cookie>". It will print "Refreshed" for confirmation

"Leave" - the RFC server will tell the RS that it wants to be turned inactive by sending "Leave: <cookie>". The RFc server will print "Left"

"RFCQuery: <hostname> <port>" - the RFC server will reach out to another peer with the specified hostname and port to request its RFC index, it will then merge it with its own. The peer that is giving the index will print "RFC Query Request" and then "RFC Query Sent"

"GetRFC: <hostname> <port> <rfc_num>" - the RFC server will contact the given peer to get its RFC file. It will add the file to its folder and add to its own RFC index.

"Search: <rfc_num>" - this command allows for the user to have the RFC server run through the above commands to get the RFC file. It will perform a PQuery, then RFCQuery until it finds the right peer and use GetRFC.

"Search: <start>-<end>" - this commands lets you search for a whole array of RFC files from a start number to an ending number inclusively. 

--------
Analysis
--------

You will find that we have a folder called "times", it contains all the time records we had for both tasks. The naming convention we went with was: "<task>_<peer num>_<single or total time> "

So for example, for task 2, peer 3, single times is: t2_p3_st.cvs

We found through performing Task 1 and Task 2, the times in Task 2 are all around better for every peer except for peer 0. In the first task, peer 0 had all the RFC files already so the download time for peer 0 was 0. In the second task, because all peers had 10 of the 60 files, they each download as many files but at the same time they had to find the files in each of the other peers rather than in task 1 where they were like in P0. But because of the less amount of files one must download,the times were smaller.
