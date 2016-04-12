import requests
import requests.auth
import json
import os
import pprint

class RedditAPI:
    client = requests.session()
    headers = {"User-Agent": "Awesome Stuff to Read 1.0 by /u/rajusa"}
    userData = None
    subreddits = []
    subredditUserCount = {}

    def redditAuth(self) :
        username = "rajusa"
        password = os.getenv("REDDIT_PASS")
        app_id = os.getenv("REDDIT_APP_ID")
        app_secret = os.getenv("REDDIT_APP_SECRET")

        client_auth = requests.auth.HTTPBasicAuth(app_id, app_secret)
        post_data = {"grant_type": "password", "username": username, "password": password}

        response = self.client.post(r"https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=self.headers)
        authResponseJson = response.json()
        if response.status_code == 200:
            if "token_type" in authResponseJson and "access_token" in authResponseJson:
                self.headers["Authorization"] = authResponseJson["token_type"] + " " + authResponseJson["access_token"]
            else:
                pprint.pprint("Auth response does not contain expected keys")
        else:
            pprint.pprint("Auth request returned status code:" + str(response.status_code))
        return

    def redditRequest(self, url):
        # At some point save token expiration and know when to reauth
        retry = 0
        while retry < 3:
            response = self.client.get(url, headers=self.headers)
            if response.status_code == 403:
                retry = retry + 1
                self.redditAuth()
            else:
                return response

    def redditRequestUserData(self) :
        response = self.redditRequest("https://oauth.reddit.com/api/v1/me")
        self.userData = response
        return self.userData

    def redditRequestSubredditDataURLBuilder(self, after):
        requestURL = "https://oauth.reddit.com/subreddits/mine/subscriber.json?limit=10"
        if (len(after) > 0):
            requestURL = requestURL + "&after=" + after
        return requestURL

    def redditRequestSubredditData(self) :
        self.subreddits[:] = []
        after = ""
        while True:
            subredditURL = self.redditRequestSubredditDataURLBuilder(after)
            response = self.redditRequest(subredditURL)
            #pprint.pprint(response.content)
            if response.status_code == 200:
                subredditResponseJson = response.json()
                if "data" in subredditResponseJson:
                    after = subredditResponseJson["data"]["after"]
                    #pprint.pprint(after)
                    if subredditResponseJson["kind"] == "Listing":
                        for subreddit in subredditResponseJson["data"]["children"]:
                            info = subreddit["data"]
                            subredditURL = info["url"]
                            self.subreddits.append(subredditURL)
                            self.subredditUserCount[subredditURL] = info["subscribers"]
                    if (after is None or len(after) == 0):
                        break
                else:
                    break
            else:
                pprint.pprint("Request subreddit data returned status code:" + str(response.status_code))
                break
        return

    def printSubreddits(self):
        for subreddit in self.subreddits:
            pprint.pprint(subreddit)

    def getSubreddits(self):
        return self.subreddits

    def getSubscriberCountToSubreddit(self, subredditURLName):
        subscriberCount = self.subredditUserCount[subredditURLName]
        return subscriberCount

    def getLastYearTopPostsToSubreddit(self, subredditURLName):
        subredditNewPostsURL = "https://oauth.reddit.com" + subredditURLName + "top.json?sort=top&t=year&limit=50"
        response = self.redditRequest(subredditNewPostsURL)
        if response.status_code == 200:
            subredditDataResponseJson = response.json()
            if subredditDataResponseJson["kind"] == "Listing":
                children = subredditDataResponseJson["data"]["children"]
                return children
        else:
            pprint.pprint("Request for new posts returned status code:" + str(response.status_code))

    def getNewTopPostsToSubreddit(self, subredditURLName):
        subredditNewPostsURL = "https://oauth.reddit.com" + subredditURLName + "top.json?sort=top&t=day&limit=10"
        response = self.redditRequest(subredditNewPostsURL)
        if response.status_code == 200:
            subredditDataResponseJson = response.json()
            if subredditDataResponseJson["kind"] == "Listing":
                children = subredditDataResponseJson["data"]["children"]
                return children
        else:
            pprint.pprint("Request for new posts returned status code:" + str(response.status_code))

    def subredditTest(self):
        if len(self.subreddits) > 0:
            self.getNewTopPostsToSubreddit(self.subreddits[-1])
