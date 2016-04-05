import requests
import requests.auth
import json
import os
import pprint

class RedditAPI :
    client = requests.session()
    headers = {"User-Agent": "Awesome Stuff to Read 1.0 by /u/rajusa"}
    subreddits = []

    def redditAuth(self) :
        username = "rajusa"
        password = os.environ["REDDITPASS"]
        app_id = os.environ["REDDIT_APP_ID"]
        app_secret = os.environ["REDDIT_APP_SECRET"]

        client_auth = requests.auth.HTTPBasicAuth(app_id, app_secret)
        post_data = {"grant_type": "password", "username": username, "password": password}

        response = self.client.post(r"https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=self.headers)
        authResponseJson = response.json()
        self.headers["Authorization"] = authResponseJson["token_type"] + " " + authResponseJson["access_token"]
        return

    def redditRequest(self, url):
        # At some point add error retry for auth
        response = self.client.get(url, headers=self.headers)
        return response

    def redditRequestUserData(self) :
        response = self.redditRequest("https://oauth.reddit.com/api/v1/me")
        pprint.pprint(response.content)
        return

    def redditRequestSubredditDataURLBuilder(self, after):
        requestURL = "https://oauth.reddit.com/subreddits/mine/subscriber.json?limit=10"
        if (len(after) > 0):
            requestURL = requestURL + "&after=" + after
        return requestURL

    def redditRequestSubredditData(self) :
        self.subreddits.clear()
        after = ""
        while True:
            subredditURL = self.redditRequestSubredditDataURLBuilder(after)
            response = self.redditRequest(subredditURL)
            #pprint.pprint(response.content)
            subredditResponseJson = response.json()
            after = subredditResponseJson["data"]["after"]
            #pprint.pprint(after)
            if subredditResponseJson["kind"] == "Listing":
                for subreddit in subredditResponseJson["data"]["children"]:
                    info = subreddit["data"]
                    self.subreddits.append(info["url"])
            if (after is None or len(after) == 0):
                break
        return

    def printSubreddits(self):
        for subreddit in self.subreddits:
            pprint.pprint(subreddit)

redditAPI = RedditAPI()
redditAPI.redditAuth()
#redditAPI.redditRequestUserData()
redditAPI.redditRequestSubredditData()
redditAPI.printSubreddits()