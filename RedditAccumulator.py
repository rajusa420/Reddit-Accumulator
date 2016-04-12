import pprint
import math
from datetime import date

from RedditAccumulatorDatabase import RedditAccumulatorDatabase
from RedditAPI import RedditAPI

class RedditAccumulator:
    redditAPI = RedditAPI()
    redditDB = RedditAccumulatorDatabase()

    def __init__(self):
        self.redditAPI.redditAuth()
        self.redditAPI.redditRequestSubredditData()
        self.redditDB.connect()

    def saveAverageScoreOfTopPostsIfState(self):
        subReddits = self.redditAPI.getSubreddits()
        for subReddit in subReddits:

            score = self.redditDB.getAverageScore(subReddit)
            lastUpdated = self.redditDB.getAverageScoreLastUpdated(subReddit)
            today = date.today()
            diff = today - lastUpdated
            if diff.days > 30:
                topPostsThisYear = self.redditAPI.getLastYearTopPostsToSubreddit(subReddit)
                totalScore = 0
                count = 0
                for post in topPostsThisYear:
                    data = post["data"]
                    score = data["score"]
                    totalScore = totalScore + score
                    count = count + 1
                averageScore = 0
                if count > 0:
                    averageScore = math.floor(totalScore / count)

                self.redditDB.saveAverageScore(averageScore, subReddit)

    def saveInterestingPostsToDB(self):
        subReddits = self.redditAPI.getSubreddits()
        postCounter = 0
        for subReddit in subReddits:
            requiredScore = self.redditDB.getAverageScore(subReddit)
            if requiredScore == 0:
                continue
            subscriberCount = self.redditAPI.getSubscriberCountToSubreddit(subReddit)
            topPosts = self.redditAPI.getNewTopPostsToSubreddit(subReddit)
            if topPosts:
                for post in topPosts:
                    data = post["data"]
                    score = data["score"]
                    if (score >= requiredScore):
                        postCounter = postCounter + 1
                        title = data["title"]
                        url = data["url"]
                        name = data["name"]
                        pprint.pprint(data["title"] + ": " + str(score) + "(" + subReddit + ")")
                        self.redditDB.saveArticle(name, title, url, score, subReddit)
            else:
                pprint.pprint("Failed to get top posts for subreddit: " + subReddit)
        pprint.pprint("Total posts Found: " + str(postCounter))

redditAccumulator = RedditAccumulator()
redditAccumulator.saveAverageScoreOfTopPostsIfState()
redditAccumulator.saveInterestingPostsToDB()
#redditAccumulator.redditDB.deleteAllArticles()