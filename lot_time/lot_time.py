import os #needed for path and file existence checks
import datetime as dt
import threading as th
import time



#############################
# functions
#############################

def build_file_name (f_path, f_name):
    # This function returns the path and file name for three different user inputs
    if len(f_name) == 0:     # user hits return to accept test data file tt1.txt
        act_f_name = f_path + test_file
    elif "." not in f_name: # user enters file name with no extension, so .txt assumed
        act_f_name = f_path + f_name + ".txt"
    else:
        act_f_name = f_path + f_name # user enters full file name with extension
    return act_f_name

def Connect2Web(g_type):
    # This function retrieves and returns the web page data
    # Python 3.7 retrieval. It returns bytes, not a string (must be cast to string)

    from urllib.request import urlopen  #needed to read web data in python 3.7

    if g_type == 0:
        aResp = urlopen("https://www.txlottery.org/export/sites/lottery/Games/Powerball/index.html")
    else:
        aResp = urlopen("https://www.txlottery.org/export/sites/lottery/Games/Mega_Millions/index.html")
    web_pg = aResp.read()
    return web_pg

def check_match(t_num, win):
    if t_num in win[0:5]:
        return str(t_num)
    else:
        return "X"
def check_bonus(t_num, win):
    if t_num == win[5]:
        return str(t_num)
    else:
        return "X"

def check_tickets(dr_date, morp, m_plier, t_nums, ltrs, f_path, afn):

    #                         balls matched
    #           without bonusball       with bonusball
    #           0,1,2,3,4,5 match       0,1,2,3,4,5 match
    pay_out = [[[0,0,0,7,100,1000000],[4,4,7,100,50000,-1]],    #Powerball payout
              [[0,0,0,10,500,1000000],[2,4,10,200,10000,-1]]]   #Mega Millions payout 

    #       PAYOUT MATRIX
    #
    #       mega = 1 payout matrix looks like this:
    #				<------- 0 - 5 numbers matched  -------->
    #				0		1		2		3		4		5
    #		0		0		0		0		10		500		1,000,000
    #		1		2		4		10		200		10,000	-1

    #		powerball (mega = 0) payout matrix looks like this:
    #				<------- 0 - 5 numbers matched  -------->
    #				0		1		2		3		4		5
    #		0		0		0		0		7		100		1,000,000
    #		1		4		4		7		100		50,000	-1
		
    #		The jackpot value is variable, so the word 'Jackpot!' is used
    #		in place of an amount. -1 signals to use the word in the ouput instead
    #		of an actual amount.


    #################################################
    # Get winning numbers and multiplier from web
    #################################################

    data = str(Connect2Web(morp))   #urlopen reads byte data, cast to a string

    # Parse web data retrieved

    # get draw date
    loc = data.find("Winning Numbers for")
    drawing_date = data[loc+20:loc+30]

    date_recd = drawing_date[6:] + drawing_date[0:2] + drawing_date[3:5]
    print (" Date received in YYYYMMDD format: "+ date_recd)
    
    print("changeing date requested to 20190820")
    dr_date = "20190820"
    req = 0
    while date_recd != dr_date:
        print (dr_date + " not available, requery in 1 minute:")
        req += 1
        time.sleep(60)
        data = str(Connect2Web(morp))   #urlopen reads byte data, cast to a string

    print ("\nDrawing results for: " + drawing_date)

    # get winning numbers
    winner = [0,0,0,0,0,0]
    for i in range(5):
        loc1 = data.find("<span>", loc)
        # Handle case where winning number is single digit vs 2 digits
        if data[loc1+7] == "<":
            winner[i] = int(data[loc1+6:loc1+7])
        else:
            winner[i] = int(data[loc1+6:loc1+8])
        loc = loc1+5
    loc1 = data.find("ball",loc)
    # Handle case where winning number is single digit vs 2 digits
    if data[loc1+7] == "<":
        winner[5] = int(data[loc1+6:loc1+7])
    else:
        winner[5] = int(data[loc1+6:loc1+8])
    print ("\nWinning numbers: " + \
        str(winner[0]).rjust(4) + str(winner[1]).rjust(4) + \
        str(winner[2]).rjust(4) +str(winner[3]).rjust(4) +\
        str(winner[4]).rjust(4) +str(winner[5]).rjust(4))

    # get multiplier value
    loc = loc1 + 13
    loc1 = data.find("<span class=",loc)
    multiplier = int(data[loc1+24])
    print ("Multiplier: " + str(multiplier))


    ##############################################
    # Check tickets for matches and print results
    ##############################################

    #print("length of ticket_nums: ", len(t_nums))
    print("\n\nRESULTS" + "First 5".rjust(35) + "Bonus".rjust(8) + "Pay Out".rjust(13))
    for i in range(len(t_nums)):
        match5 = 0
        match_bonus = 0
        for j in range(5):
            temp = check_match(t_nums[i][j], winner)
            if temp != "X":
                match5 += 1
        temp = check_bonus(t_nums[i][5], winner)
        if temp != "X":
            match_bonus += 1
        if m_plier:
            result_int = pay_out[mega][match_bonus][match5] * multiplier
        else:
            result_int = pay_out[mega][match_bonus][match5]
        if result_int < 0:
            result = "Jackpot!"
        else:
            if result_int > 2000000 and mega == 0:
                result = "{:,}".format(2000000)
            elif result_int > 5000000 and mega == 1:
                result = "{:,}".format(5000000)
            else:
                result = "{:,}".format(result_int)
        print(ltrs[i % 10] + ":" +\
            check_match(t_nums[i][0], winner).rjust(5) + \
            check_match(t_nums[i][1], winner).rjust(5) + \
            check_match(t_nums[i][2], winner).rjust(5) + \
            check_match(t_nums[i][3], winner).rjust(5) + \
            check_match(t_nums[i][4], winner).rjust(5) + \
            check_bonus(t_nums[i][5], winner).rjust(5) + \
            str(match5).rjust(10) + \
            str(match_bonus).rjust(8) + \
            result.rjust(13))
    if mega == 1:
            save_name = drawing_date[-4:] + \
                drawing_date[0:2] + drawing_date[3:5] + "mm_results.txt"
    else:
        save_name = drawing_date[-4:] + \
            drawing_date[0:2] + drawing_date[3:5] + "pb_results.txt"

    #############################################
    # Save results
    #############################################

    if save_flag == "y":
        if morp == 1:
            #save_name = dr_date[-4:] + \
            #    dr_date[0:2] + dr_date[3:5] + "mm_results.txt"
            save_name = dr_date + "mm_results.txt"
        else:
            #save_name = dr_date[-4:] + \
            #    dr[0:2] + dr_date[3:5] + "pb_results.txt"
            save_name = dr_date + "pb_results.txt"
        save_file = open(file_path + save_name, "w")
        save_file.write("Lottery ticket results for: " + dr_date)
        if morp == 1:
            save_file.write("\n\nGame type: Mega Millions")
        else:
            save_file.write("\n\nGame type: Powerball")
        save_file.write("\n\nTicket data file: " + afn)

        save_file.write("\n\nTicket numbers in play:")
        for i in range(len(t_nums)):
            save_file.write("\nTicket " + ltrs[i % 10] + \
                str(t_nums[i][0]).rjust(5) + \
                str(t_nums[i][1]).rjust(5) + \
                str(t_nums[i][2]).rjust(5) + \
                str(t_nums[i][3]).rjust(5) + \
                str(t_nums[i][4]).rjust(5) + \
                str(t_nums[i][5]).rjust(5))

        save_file.write("\n\nWinning numbers: " +\
            str(winner[0]).rjust(4) + str(winner[1]).rjust(4) + \
            str(winner[2]).rjust(4) +str(winner[3]).rjust(4) +\
            str(winner[4]).rjust(4) +str(winner[5]).rjust(4))
        save_file.write("\n\nMultiplier: " + str(m_plier))
        save_file.write("\n\nRESULTS" + "First 5".rjust(41) + "Bonus".rjust(8) + "Pay Out".rjust(13))
        for i in range(len(t_nums)):
            match5 = 0
            match_bonus = 0
            for j in range(5):
                temp = check_match(ticket_nums[i][j], winner)
                if temp != "X":
                    match5 += 1
            temp = check_bonus(ticket_nums[i][5], winner)
            if temp != "X":
                match_bonus += 1
            #result_int = pay_out[mega][match_bonus][match5] * multiplier
            if m_plier:
                result_int = pay_out[mega][match_bonus][match5] * multiplier
            else:
                result_int = pay_out[mega][match_bonus][match5]
            if result_int < 0:
                result = "Jackpot!"
            else:
                if result_int > 2000000:
                    result = "{:,}".format(2000000)
                else:
                    result = "{:,}".format(result_int)
            save_file.write("\nTicket " + ltrs[i % 10] + \
                check_match(ticket_nums[i][0], winner).rjust(5) + \
                check_match(ticket_nums[i][1], winner).rjust(5) + \
                check_match(ticket_nums[i][2], winner).rjust(5) + \
                check_match(ticket_nums[i][3], winner).rjust(5) + \
                check_match(ticket_nums[i][4], winner).rjust(5) + \
                check_bonus(ticket_nums[i][5], winner).rjust(5) + \
                str(match5).rjust(10) + \
                str(match_bonus).rjust(8) + \
                result.rjust(13))
        save_file.close()
    










####################################################
#
# This part executes before timing starts
#
####################################################

# Declare lists for data
ticket_nums = []                # List to store ticket data
#match = []                      # List to show which ticket numbers matched
                                # 0 is no match, 1 is match
buffer_list = [0,0,0,0,0,0]     # Temp buffer used in building ticket list
letters = ["A","B","C","D","E","F","G","H","I","J"]


###################################
# Get name of file with ticket data
###################################

# Default prompt requesting user to enter file name for ticket data
get_prompt = "Enter name of file containing ticket data: "

# Get appropriate file path for ticket data
if os.path.isdir("k:/onedrive/lottery_data/"): # Gateway path
    file_path = "k:/onedrive/lottery_data/"
elif os.path.isdir("c:/users/William/onedrive/lottery_data/"): # Asus path
    file_path = "c:/users/William/onedrive/lottery_data/"
elif os.path.isdir("c:/users/William Cottingham/onedrive/lottery_data/"): # Surface path
    file_path = "c:/users/William Cottingham/onedrive/lottery_data/"
else:
    file_path = ""  # none of those computers, so full path required
    get_prompt = "Enter name of file (with full path) containing ticket data: "

# Get user input of file name
#print(get_prompt, end="")
file_name = input(get_prompt)
actual_file_name = build_file_name(file_path, file_name)

# Check existence of path and file chosen and reprompt if not found
while not os.path.exists(actual_file_name):
    print("That file doesn't exist, please reenter:", end="")
    file_name = input()
    actual_file_name = build_file_name(file_path, file_name)

####################################################################
# Retrieve game type, multipier status and ticket values from file
####################################################################

f = open(actual_file_name, "r")
buffer_in = f.readline().split(" ")
if buffer_in[0] == "mm":
    mega = 1
else:
    mega = 0
mult = bool(buffer_in[1])

for line in f:
    buffer_in = line.split(" ")
    for i in range(6):
        buffer_list[i] = int(buffer_in[i])
    ticket_nums.append([int(buffer_in[0]),int(buffer_in[1]),\
        int(buffer_in[2]),int(buffer_in[3]),int(buffer_in[4]),int(buffer_in[5])])
    #match.append([0,0,0,0,0,0]) #add a corresponding row to match list as well
print ("\nTicket numbers in play:")
#for i in range(len(ticket_nums)):
#    print (ticket_nums[i])
for i in range(len(ticket_nums)):
    print(letters[i % 10] + ":" +\
        str(ticket_nums[i][0]).rjust(5) + \
        str(ticket_nums[i][1]).rjust(5) + \
        str(ticket_nums[i][2]).rjust(5) + \
        str(ticket_nums[i][3]).rjust(5) + \
        str(ticket_nums[i][4]).rjust(5) + \
        str(ticket_nums[i][5]).rjust(5))
if mega == 0:
    print("\nGame type: Powerball")
else:
    print("\nGame type: Mega Millions")
print("\nMultiplier in play? ", mult)

f.close()

#######################################
# Get drawing date to be checked
#######################################

#print("Date of drawing to be checked (YYYYMMDD: ", end="")
draw_date = input("\nDate of drawing to be checked (YYYYMMDD): ")
timestr = input("\nTrigger time (HHMM): ")
save_flag = input("\nSave results? (y/n)")
while save_flag.lower() != "y" and save_flag.lower() != "n":
    save_flag = input("\nSave results? (y/n)")
mydate = dt.datetime(int(draw_date[0:4]),\
    int(draw_date[4:6]),\
    int(draw_date[6:]),\
    int(timestr[0:2]),\
    int(timestr[2:]))
#print(mydate)
start_val = input("\nCheck for drawing results at " + str(mydate) + "? (y/n) ")
while start_val.lower() != "y" and start_val.lower() != "n":
    start_val = input("\nCheck for drawing results at " + mydate + "? (y/n) ")
if start_val.lower() == "y":
    
    print("Delaying until: ", mydate)
    delay = (mydate - dt.datetime.now()).total_seconds()
    th.Timer(delay, check_tickets,(draw_date, mega, mult, \
        ticket_nums, letters, file_path, actual_file_name)).start()