import requests
import re
import os
import sys
import json
import time
import pandas as pd

# bilibili api introduction: https://github.com/Vespa314/bilibili-api/blob/master/api.md

# unique id of the video
aid_list = []

# relevent video list
video_info = []

# reviews list
comment_list = []


def releventVideo(keyword, review_threshold, time_threshold):
    search_url = 'https://api.bilibili.com/x/web-interface/search/type? +\
     jsonp=jsonp&search_type=video&keyword=' + keyword + '&page=1'
    r = requests.get(search_url)
    numtext = r.text
    json_text = json.loads(numtext)
    page = json_text["data"]["numPages"]

    for n in range(1, page + 1):
        url = 'https://api.bilibili.com/x/web-interface/search/type? +\
               jsonp=jsonp&search_type=video&keyword=' + keyword + '&page=' + str(n)
        r = requests.get(url)
        text = r.text
        json_text = json.loads(text)
        # iterate and get aid and topic info
        for m in json_text["data"]["result"]:
            if m['review'] >= review_threshold and time.strftime("%Y-%m-%d %H:%M:%S",
                                                                 time.localtime(m['senddate'])) >= time_threshold:
                aid_list.append(m["aid"])
                video_info.append([m['title'], m['tag'], m['author'], m['play'], m['review'],
                               time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m['senddate'])),
                               m['typename'], m['arcurl']])
        ###########################
        # bilibili doesn't allow scrap users data and will detect the scraping process
        # decrease the IP blocked risk
        # if page%10 == 0:
        #    time.sleep(3)

        ###############


# get all reviews in a specific video... DO not consider replies of the reviews
## sometimes the author of the video modify the video. The video senddate will change, to meet the time threshold
## add the condition in the comment func as well


def getAllCommentList(item, time_threshold):
    # three useful arguments pn: current page oid: the unique index of video  type = 1
    url = "http://api.bilibili.com/x/reply?type=1&oid=" + str(item) + "&pn=1&nohot=1&sort=0"
    r = requests.get(url)
    numtext = r.text
    json_text = json.loads(numtext)
    commentsNum = json_text["data"]["page"]["count"]
    page = commentsNum // 20 + 1
    for n in range(1, page):
        url = "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=" + str(n) + "&type=1&oid=" + str(
            item) + "&sort=1&nohot=1"
        req = requests.get(url)
        text = req.text
        json_text_list = json.loads(text)

        # User name, sex, post time, reviews content, likes, replies
        for i in json_text_list["data"]["replies"]:
            if time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['ctime'])) >= time_threshold:
                comment_list.append([i["member"]["uname"], i["member"]["sex"],
                                     time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i['ctime'])),
                                     i["content"]["message"], i['like'], i['rcount']])


if __name__ == "__main__":

    keyword = '%E5%A4%8D%E8%81%944'
    releventVideo(keyword, 100, '2019-03-14')
    for item in aid_list:
        getAllCommentList(item, '2019-03-14')

    ### covert to df to have a straight forward view
    df_comment = pd.DataFrame(comment_list, columns=['Users Name', 'Sex', 'Post Time', 'Content', 'Likes', 'Replies'])
    df_video = pd.DataFrame(video_info,
                            columns=['Title', 'Tags', 'Author', 'Plays', 'Reviews', 'Post Time', 'Video Type', 'URL'])
