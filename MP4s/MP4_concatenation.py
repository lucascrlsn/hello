# Forked from rohitrangan at https://gist.github.com/rohitrangan/3841212 for learning purposes

import sys
import time
from subprocess import check_output

for i in range(1, len(sys.argv)):
    print sys.argv[i],
    fname = "Part" + str(i) + ".mpg"
    print fname
    check_output(["ffmpeg", "-i", sys.argv[i], "-sameq", fname])

print "Converted all mp4's to mpg's. Now combining them into a single file."

check_output("cat Part*.mpg > ./Final.mpg", shell=True)
print "Removing all the intermediate files..."
time.sleep(3)
check_output("rm Part*.mpg", shell=True)

print "Now converting mpg back to mp4."
print "The size may be smaller than the original mp4 files.",
print "This is because of a change in the audio and video codec."
time.sleep(3)

check_output(["ffmpeg", "-i", "Final.mpg", "-vcodec", "libx264", "-acodec", "libvorbis", "-sameq", "Final.mp4"])
time.sleep(3)
print "Removing the last remaining mpg file..."
check_output("rm Final.mpg", shell=True)
print "Finished merging the files. The output file is Final.mp4"
