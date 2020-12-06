# Twitch.tv clip downloader
import os
import requests
from urllib.parse import urlparse

REQUEST_URL = "https://gql.twitch.tv/gql"
CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
DEVICE_ID = "AIP5RYCt06KhQDKAuPSSlXN2M0P1WxVJ"

def _getHeader(clientId = CLIENT_ID, deviceId = DEVICE_ID):
  return {
    "Client-Id": clientId, "X-Device-Id": deviceId
  }

def _parseUrl(url):
  return urlparse(url).path[1:]

def _generateGetClipsPayload(username, limit):
  return [{
    "operationName": "ClipsCards__User",
    "variables": {
      "login": username,
      "limit": limit,
      "criteria": {
        "filter": "ALL_TIME"
      }
    },
    "extensions": {
      "persistedQuery": {
        "version": 1,
        "sha256Hash": "b73ad2bfaecfd30a9e6c28fada15bd97032c83ec77a0440766a56fe0bd632777"
      }
    }
  }]

def _convertJsonToClips(json):
  json = json[0]["data"]["user"]["clips"]["edges"]
  clips = []
  for i in json:
    i = i["node"]
    clip = {
      "id": i["id"],
      "slug": i["slug"],
      "title": i["title"],
      "views": i["viewCount"],
      "duration": i["durationSeconds"],
      "broadcaster": i["broadcaster"]["displayName"]
    }

    clips.append(clip)
  return clips

def _generateGetClipSourcesPayload(clip):
  return [{
      "operationName": "VideoAccessToken_Clip",
      "variables": { "slug": clip["slug"] },
      "extensions": {
        "persistedQuery": {
          "version": 1,
          "sha256Hash": "9bfcc0177bffc730bd5a5a89005869d2773480cf1738c592143b5173634b7d15"
        }
      }
    }
  ]

def _convertJsonToClipSources(json):
  json = json[0]["data"]["clip"]["videoQualities"]
  sources = []

  for i in json:
    source = {
      "quality": i["quality"],
      "frameRate": i["frameRate"],
      "url": i["sourceURL"]
    }

    sources.append(source)
  return sources

def getClips(username, limit=20):
  payload = _generateGetClipsPayload(username, limit)

  resp = requests.post(REQUEST_URL, headers=_getHeader(), json=payload).json()
  if resp[0]["data"]["user"] == None:
    return None
    
  return _convertJsonToClips(resp)  

def getClipSources(clip):
  payload = _generateGetClipSourcesPayload(clip)

  resp = requests.post(REQUEST_URL, headers=_getHeader(), json=payload).json()
  return _convertJsonToClipSources(resp)


def downloadClip(url, folder="./videos/"):
  resp = requests.get(url, stream=True)
  totalSizeInBytes = int(resp.headers.get("content-length", 0))
  blockSize = 1024 #kB
  currentBytes = 0

  percentText = "\033[K{:.0f} / {:.0f} :\t{:.0f}%"

  if not os.path.exists(folder):
    os.makedirs(folder)

  with open(folder + _parseUrl(url), "wb") as file:
    for data in resp.iter_content(blockSize):
      file.write(data)
      currentBytes += blockSize
      percent = (currentBytes / totalSizeInBytes) * 100

      print(percentText.format(currentBytes, totalSizeInBytes, percent) , end="\r")
  print()