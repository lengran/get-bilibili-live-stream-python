import requests
import json

V2API = "https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo"

def GetRealRoomId(roomId):
    api_address = "https://api.live.bilibili.com/room/v1/Room/room_init"
    with requests.Session() as session:
        roomStatus = session.get(api_address + "?id=" + str(roomId)).json()
    code = roomStatus["code"]
    if code == 60004:
        print("直播间不存在")
        return -1
    if code == 0:
        liveStatus = roomStatus["data"]["live_status"]
        if liveStatus != 1:
            print("直播间未开播")
            return -1
    return roomStatus["data"]["room_id"]

def GetAvailableQuality(realRoomId):
    param = {
        "room_id" : realRoomId,
        "platform": "h5",
        "protocol" : "1",
        "format" : "0,1",
        "codec" : "0"
    }
    with requests.Session() as session:
        result = session.get(V2API, params=param).json()
    qn = []
    desc = []
    for quality in result["data"]["playurl_info"]["playurl"]["g_qn_desc"]:
        if quality["hdr_desc"] == "HDR":
            desc.append(quality["desc"] + " HDR")
        else:
            desc.append(quality["desc"])
        qn.append(quality["qn"])
    qualities = (qn, desc)
    return qualities

def GetStreamUrl(realRoomId, qn):
    param = {
        "room_id" : realRoomId,
        "platform": "h5",
        "protocol" : "1",
        "format" : "0,1",
        "codec" : "0",
        "qn" : qn
    }
    with requests.Session() as session:
        result = session.get(V2API, params=param).json()
    baseUrl = result["data"]["playurl_info"]["playurl"]["stream"][0]["format"][0]["codec"][0]["base_url"]
    host = result["data"]["playurl_info"]["playurl"]["stream"][0]["format"][0]["codec"][0]["url_info"][0]["host"]
    extra = result["data"]["playurl_info"]["playurl"]["stream"][0]["format"][0]["codec"][0]["url_info"][0]["extra"]
    url = host + baseUrl + extra
    return url

"""
def PrintToFile(urls):
    content = ""
    for url in urls:
        content += url + "\n"
    content = content[:-1]
    with open("stream_urls.txt", "w") as file:
        file.write(content)
"""

if __name__ == "__main__":
    roomId = input("请输入BiliBili直播间房间号：")
    
    realRoomId = GetRealRoomId(roomId)
    if realRoomId == -1:
        exit(-1)
    
    qualities = GetAvailableQuality(realRoomId)
    print("请选择清晰度并输入对应序号(可能只有直播间网页有的选项才有效)：")
    for i in range(len(qualities[1])):
        print(str(i) + ": " + qualities[1][i])
    strQuality = input()
    try:
        intQuality = int(strQuality)
        if intQuality >= len(qualities[1]) or intQuality < 0:
            raise RuntimeError("Illegal input.")
    except:
        print("请输入合理的清晰度序号")
        exit(-1)

    """
    urls = GetStreamUrls(realRoomId, qualities[0][intQuality])
    for i in range(len(urls)):
        print("线路 " + str(i) + ": ")
        print(urls[i])
    
    needPlaylistFile = input("是否需要输出链接到文件？输入 y 生成，其它则程序退出")
    if needPlaylistFile == "y":
        PrintToFile(urls)
    """
    url = GetStreamUrl(realRoomId, qualities[0][intQuality])
    print(url)