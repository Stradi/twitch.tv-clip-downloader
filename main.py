import os
import pandas as pd
import twitchDownloader as twitch

FILENAME = "urls.csv"

def createFile(filename):
  if not os.path.exists(filename):
    print("{0} file not found. Creating one.".format(filename))
    file = open(filename, "w+")
    file.write("id,slug,title,views,duration,game,broadcaster,url,isDone\n")
    file.close()

def findCurrentIDs(filename):
  df = pd.read_csv(filename)
  return df["id"]

def removeDuplicates(filename, clips):
  currents = findCurrentIDs(filename)
  newArr = []
  totalDuplicates = 0

  for clip in clips:
    if int(clip["id"]) in currents.values:
      totalDuplicates += 1
      print("\033[KDuplicates: {0}/{1}".format(totalDuplicates, len(clips)), end="\r")
      continue

    newArr.append(clip)
  print()
  return newArr

def writeToFile(filename, clips):
  df = pd.DataFrame(clips)
  df.to_csv(filename, mode="a", header=False, index=False)

def addUrlToClips(clips):
  for idx, clip in enumerate(clips):
    clips[idx]["url"] = twitch.getClipSources(clip)[0]["url"]
    clips[idx]["isDone"] = False
    print("\033[KAdding URLs: {0}/{1}".format(idx + 1, len(clips)), end="\r")
  print()

def main():
  createFile(FILENAME)
  username = input("Enter a Twitch.tv username: ")
  print("Getting clips of '{0}'.".format(username))
  clips = twitch.getClips(username)
  if clips == None:
    print("I think this user does not exists.")
    exit()

  clips = removeDuplicates(FILENAME, clips)

  if(len(clips) == 0):
    print("There is no new clips I think.")
    print("Exiting program.")
    exit(0)

  addUrlToClips(clips)
  writeToFile(FILENAME, clips)
  print("DONE. Open {0}".format(FILENAME))

if __name__ == "__main__":
  main()