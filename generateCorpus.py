import pandas as pd
from selenium import webdriver
import time
from tqdm import tqdm
import numpy as np

def getNeurIPS2021All():
    # NeurIPS 2021 Benchmark Track
    homepage = "https://openreview.net/group?id=NeurIPS.cc/2021/Track/Datasets_and_Benchmarks/Round2#accepted"
    accepted_num = 108
    browser = webdriver.Firefox()
    browser.get(homepage)
    time.sleep(3)
    papers_url = []
    for i in range(1,accepted_num+1):
        papers_url.append(browser.find_element_by_css_selector("#accepted > ul > li:nth-child("+str(i)+") > h4 > a:nth-child(1)").get_attribute('href'))
    # one rejected
    papers_url.append("https://openreview.net/forum?id=m5rEiGxOGiL")
    browser.close()
    return papers_url

def generate21Corpus(papers_url):
    browser = webdriver.Firefox()
    df = pd.DataFrame()
    types = []
    contents = []
    ids = []
    track_url = []
    for i in tqdm(range(len(papers_url))):
        link = papers_url[i]
        browser.get(link)
        time.sleep(3)
        browser.execute_script('''
                var element = document.querySelectorAll("div.note_with_children.comment-level-even"), index;
                for (index = element.length - 1; index >= 0; index--) {
                    element[index].parentNode.removeChild(element[index]);
                }
            ''')
        reviewBox = browser.find_elements_by_css_selector("div.note_with_children.comment-level-odd")
        for box in reviewBox:
            blocks = box.find_elements_by_css_selector("div.note_contents")
            for b in blocks:
                comment_type = b.find_element_by_css_selector("span.note_content_field").text[:-1]
                types.append(comment_type)
                review = b.find_element_by_css_selector("span:nth-child(2)").text 
                contents.append(review)
                ids.append(i)
                track_url.append(link)
    browser.close()
    df["type"] = types
    df["review"] = contents
    df["paper_id"] = ids
    df["track_url"] = track_url
    df.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21.txt",index=False)


def getNeurIPS2019All():
    # NeurIPS 2019 Challenge Review
    accept_pages = "https://openreview.net/group?id=NeurIPS.cc/2019/Reproducibility_Challenge#accept"
    reject_pages = "https://openreview.net/group?id=NeurIPS.cc/2019/Reproducibility_Challenge#reject"
    accepted_num = 11
    rejected_num = 73
    browser = webdriver.Firefox()
    papers_url = []
    browser.get(accept_pages)
    time.sleep(3) 
    for i in range(1,accepted_num+1):
        papers_url.append(browser.find_element_by_css_selector("li.note:nth-child("+str(i)+") > h4:nth-child(1) > a:nth-child(1)").get_attribute('href'))
    browser.close()
    browser = webdriver.Firefox()
    browser.get(reject_pages)
    time.sleep(3)
    for i in range(1,rejected_num+1):
        papers_url.append(browser.find_element_by_css_selector("li.note:nth-child("+str(i)+") > h4:nth-child(1) > a:nth-child(1)").get_attribute('href'))
    browser.close()
    return papers_url


def generate19Corpus(papers_url):
    browser = webdriver.Firefox()
    df = pd.DataFrame()
    types = []
    contents = []
    ids = []
    track_url = []
    for i in tqdm(range(len(papers_url))):
        link = papers_url[i]
        browser.get(link)
        time.sleep(3)
        browser.execute_script('''
                var element = document.querySelectorAll("div.note_with_children.comment-level-even"), index;
                for (index = element.length - 1; index >= 0; index--) {
                    element[index].parentNode.removeChild(element[index]);
                }
            ''')
        reviewBox = browser.find_elements_by_css_selector("div.note_with_children.comment-level-odd")
        for box in reviewBox:
            blocks = box.find_elements_by_css_selector("div.note_contents")
            for b in blocks:
                comment_type = b.find_element_by_css_selector("span.note_content_field").text[:-1]
                types.append(comment_type)
                review = b.find_element_by_css_selector("span.note_content_value").text 
                contents.append(review)
                ids.append(i)
                track_url.append(link)
    browser.close()
    df["type"] = types
    df["review"] = contents
    df["paper_id"] = ids
    df["track_url"] = track_url
    df.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19.txt",index=False)

def cleaning():
    #df19 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19.txt")
    #df21 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21.txt")
    df19.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19.csv",index=False)
    df21.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21.csv",index=False)
    # manually deleted authors' Comments

def keepstrlong(check):
    i = 0
    if isinstance(check,str):
        check = [check]
    while i < len(check):
        cand = check[i]
        if (not (isinstance(cand,str))) or len(cand.split(" ")) < 25 :
            check.pop(i)
        else:
            i += 1
    return ("\n".join(check))

def labelReviewer():
    df19 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19.csv")
    row = df19.shape[0]
    reviewers19 = [-1] * row
    counter = 0
    reviewIdx = list(df19.loc[df19["type"] == "Review", "review"].index)
    for i in reviewIdx:
        reviewers19[i] = counter
        counter += 1
    curr = 0
    for ci in range(len(reviewers19)):
        if reviewers19[ci] < 0 :
            reviewers19[ci] = curr
        elif reviewers19[ci] != curr:
            curr = reviewers19[ci]
    df19["reviewers"] = reviewers19
    df19.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19.csv",index=False)
    
    
    df21 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21.csv")
    row = df21.shape[0]
    reviewers21 = [-1] * row
    counter = 0
    reviewIdx = list(df21.loc[(df21["type"] == "Comment") | (df21["type"] == "Additional Feedback"), "review"].index)
    for i in reviewIdx:
        reviewers21[i] = counter
        counter += 1
    reviewers21 = list(reversed(reviewers21))
    curr = reviewers21[0]
    for ci in range(len(reviewers21)):
        if reviewers21[ci] < 0 :
            reviewers21[ci] = curr
        elif reviewers21[ci] != curr:
            curr = reviewers21[ci]
    df21["reviewers"] = list(reversed(reviewers21))
    df21.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21.csv",index=False)


def transform19():
    df19 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19.csv")
    # Columns: 
    # id, 
    # url, 
    # Decision(0-Rej, 1-Accept), 
    # Ratings(1:bad-10:good)
    # Confidence(1:guess-5:confident)
    # Text(Review 
    #     + Comment)[included if word count >= 20]
    tableL = []
    for i in tqdm(range(84)):
        ratingsL = df19.loc[(df19["paper_id"] == i) & (df19["type"] == "Rating"),"review"].values
        ratingsL = list(map(lambda x : int(x[0]), ratingsL))
        
        confidenceL = df19.loc[(df19["paper_id"] == i) & (df19["type"] == "Confidence"),"review"].values
        confidenceL = list(map(lambda x : int(x[0]), confidenceL))
        
        rcL = df19.loc[(df19["paper_id"] == i) & ((df19["type"] == "Review") | (df19["type"] == "Comment"))].values
        reviewersL = [[arr[1],arr[-1]] for arr in rcL]
        txtL = []
        prev_rev = reviewersL[0][1]
        prev_cont = ""
        for ii in range(len(reviewersL)):
            rev = reviewersL[ii][1]
            content = reviewersL[ii][0]
            if rev == prev_rev and prev_cont != "":
                txtL[-1] = [prev_cont,content]
            else:
                prev_rev = rev
                prev_cont = content
                txtL.append(content)
        txtL  = list(filter((lambda x: x != ""), [keepstrlong(c) for c in txtL]))
        num_reviewers = len(txtL)
        paperL = []
        if len(ratingsL) < num_reviewers:
            ratingsL.insert(0,sum(ratingsL)//len(ratingsL))
        if len(confidenceL) < num_reviewers:
            confidenceL.insert(0,sum(confidenceL)//len(confidenceL))
        for di in range(num_reviewers):
            d = dict()
            d["id"] = str(i)
            d["url"] = df19.loc[df19["paper_id"] == i,"track_url"].values[0]
            d["decision"] = df19.loc[(df19["paper_id"] == i) & (df19["type"] == "Decision"),"review"].values[0]
            if d["decision"] == "Accept":
                d["decision"] = 1
            else:
                d["decision"] = 0
            d["ratings"] = ratingsL[di]
            d["confidence"] = confidenceL[di]
            d["text"] = txtL[di]
            paperL.append(d)
        #import pdb
        #pdb.set_trace()
        tableL.extend(paperL)
    df = pd.DataFrame(tableL)
    df.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19-clean.csv",index=False)


def transform21():
    df21 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21.csv")
    # Columns:
    # id,
    # url,
    # Decision(0-Rej, 1-Accept),
    # Ratings(1:bad-10:good)
    # Confidence(1:guess-5:confident)
    # Text(Additional Feedback + Clarity + 
    #      Comment + Correctness + 
    #      Documentation + Ethics + 
    #      Relation to Prior Work + Strengths + 
    #      Summary and Contributions + 
    #      Weaknesses) [included if word count >= 20]
    df21 = df21.fillna("")
    tableL = []
    for i in tqdm(range(109)):
        ratingsL = df21.loc[(df21["paper_id"] == i) & (df21["type"] == "Rating"),"review"].values
        ratingsL = list(map(lambda x : int(x[0]), ratingsL))
        ratingsL = list(map(lambda x : 10 if x == 1 else x , ratingsL))
        confidenceL = df21.loc[(df21["paper_id"] == i) & (df21["type"] == "Confidence"),"review"].values
        confidenceL = list(map(lambda x : int(x[0]), confidenceL))
        rcL = df21.loc[(df21["paper_id"] == i) 
                    & ((df21["type"] == "Additional Feedback") 
                        | (df21["type"] == "Clarity")
                        | (df21["type"] == "Comment")
                        | (df21["type"] == "Correctness")
                        | (df21["type"] == "Documentation")
                        | (df21["type"] == "Ethics")
                        | (df21["type"] == "Relation To Prior Work")
                        | (df21["type"] == "Strengths")
                        | (df21["type"] == "Summary And Contributions")
                        | (df21["type"] == "Weaknesses"))].values
        reviewersL = [[arr[1],arr[-1]] for arr in rcL]
        txtL = []
        prev_rev = reviewersL[0][1]
        prev_cont = ""
        for ii in range(len(reviewersL)):
            rev = reviewersL[ii][1]
            content = reviewersL[ii][0]
            if rev == prev_rev and prev_cont != "":
                txtL[-1] = [txtL[-1]]
                txtL[-1].append(content)
            else:
                prev_rev = rev
                prev_cont = content
                txtL.append(content)
        txtL  = list(filter((lambda x: x != ""), [keepstrlong(c) for c in txtL]))
        num_reviewers = len(txtL)
        paperL = []
        while len(ratingsL) < num_reviewers:
            ratingsL.insert(0,sum(ratingsL)//len(ratingsL))
        while len(confidenceL) < num_reviewers:
            confidenceL.insert(0,sum(confidenceL)//len(confidenceL))
        for di in range(num_reviewers):
            d = dict()
            d["id"] = str(i)
            d["url"] = df21.loc[df21["paper_id"] == i,"track_url"].values[0]
            d["decision"] = df21.loc[(df21["paper_id"] == i) & (df21["type"] == "Decision"),"review"].values[0]
            if d["decision"] == "Accept":
                d["decision"] = 1
            else:
                d["decision"] = 0
            d["ratings"] = ratingsL[di]
            d["confidence"] = confidenceL[di]
            d["text"] = txtL[di]
            paperL.append(d)
        #import pdb
        #pdb.set_trace()
        tableL.extend(paperL)
    df = pd.DataFrame(tableL)
    df.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21-clean.csv",index=False)

def totxt():
    df19 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19-clean.csv")
    for i in range(df19.shape[0]):
        s = df19.loc[i,"text"]
        with open("/Users/zengzh/Desktop/36468Final/NeurIPS19txt/19-"+str(i)+".txt", "w") as text_file:
            text_file.write(s)

    df21 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21-clean.csv")
    for i in range(df21.shape[0]):
        s = df21.loc[i,"text"]
        with open("/Users/zengzh/Desktop/36468Final/NeurIPS21txt/21-"+str(i)+".txt", "w") as text_file:
            text_file.write(s)

def addFileName():
    df19 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19-clean.csv")
    df19["Filename"] = [ "19-"+str(i)+".txt" for i in range(df19.shape[0])]
    df19.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS19-clean.csv",index=False)
    df21 = pd.read_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21-clean.csv")
    df21["Filename"] = [ "21-"+str(i)+".txt" for i in range(df21.shape[0])]
    df21.to_csv("/Users/zengzh/Desktop/36468Final/NeurIPS21-clean.csv",index=False)

def helpAcc():
    df = pd.read_csv("/Users/zengzh/Desktop/36468Final/helpfulacc.csv")
    correct = 0
    r,_ = df.shape
    for i in range(r):
        if df.iloc[i,0] == df.iloc[i,1]:
            correct += 1
    print(correct/r*100)

#papers_url19 = getNeurIPS2019All()
#generate19Corpus(papers_url19)
#papers_url21 = getNeurIPS2021All()
#generate21Corpus(papers_url21)
#labelReviewer()
#transform19()
#transform21()
#totxt()
#addFileName()
helpAcc()
