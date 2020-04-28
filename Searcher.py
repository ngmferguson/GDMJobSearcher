from bs4 import BeautifulSoup, SoupStrainer
import requests
import httplib2
import webbrowser

# Input for city/state/province to search
location = input("Enter City/State/Province (MUST be present on www.gamedevmap.com) or nothing will happen: ")
# Making the location string friendly with spaces
location = "%20".join(location.split())

#Getting how many tabs to open at once, I wanna let the user have control over this in case their rig is really beefy or really weak
while True:
    try:
        STUDIOS_TO_OPEN_AT_ONCE = int(input("How many tabs to open at once (number only). \n WARNING: large numbers could overload your browser, try keeping it under 10 or 11: "))
        break
    except:
        print("not an int.")

jobPage = 1
nextURL = ""
studioPages = []
studioPagesWithJobs = []
http = httplib2.Http()
pages = []

# This chunk will look for every link in gamedevmap.com and all the ones starting with 'http:' get added to a list
# This isn't particularly stable but I found every link to a games studio on the site starts with http: and not https:
# so it works for a first pass but maybe isn't scalable?? It spooks me
print("Please wait, could be opening/parsing 100+ pages so it could take a minute...")

while nextURL == "":
    status, response = http.request("https://www.gamedevmap.com/index.php?location=" + location + "&country=&state=&city=&query=&type=&start=" + str(jobPage) + "&count=100")
    # Allows us to go to the next job page
    jobPage += 100
    nextURL = ""
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a'), features="html.parser"):
        if link.has_attr('href'):
            if link['href'][:5] =="http:":
                studioPages.append(link)
            elif link['href'] == "index.php?location=" + location + "&country=&state=&city=&query=&type=&start=" + str(jobPage) + "&count=100":
                nextURL = link['href']
            pages.append(link)

        if "zynga" in link:
            print()
    if nextURL == "":
        break
    else:
        status, response = http.request("https://www.gamedevmap.com/index.php?location=" + location + "&country=&state=&city=&query=&type=&start=" + str(jobPage) + "&count=100")
        # Resets nextURL so we loop through the next job page
        nextURL = ""



# This block opens all the game job pages
for studioPage in studioPages:
    url = studioPage['href']
    headers = {'User-Agent': 'Mozilla/5.0'}

    # We try to open the page
    try:
        r = requests.get(url, headers=headers)

        #Parsing the page and making it pretty
        soup = BeautifulSoup(r.text, 'html.parser')
        prettySoup = soup.prettify().lower()

        #using the keywords "jobs", "join us", "Careers", and "openings" to see if the studio page has that somewhere in the html text
        if ("jobs" in prettySoup or "join us" in prettySoup
                or "careers" in prettySoup or "openings" in prettySoup):
            print("Job page found: " + url)
            studioPagesWithJobs.append(url)
        else:
            print("No jobs found on url: " + url)

    # some pages return exceptions, we print the exception and the URL
    # kinda defensive, since if we saw something like www.ea.com had an error, then we know there's probably an error with us
    except requests.exceptions.RequestException as e:
        print(str(e) + " on url: " + url)


print(str(len(studioPagesWithJobs)) + " studios with possible job pages found.")
if (len(studioPagesWithJobs) == 0):
    print("Exiting")
else:
    #Opens STUDIOS_TO_OPEN_AT_ONCE pages at a time, to prevent crashing a browser by trying to open like 50 tabs
    openedPages = 0
    for i in range(len(studioPagesWithJobs)):
        openedPages += 1
        webbrowser.open(studioPagesWithJobs[i])
        print("Opening: " + studioPagesWithJobs[i])
        if (openedPages % STUDIOS_TO_OPEN_AT_ONCE == 0):
            input("Press Enter to continue...")
