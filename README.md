###############################################################################
#                                                                             #
#                                 SAFETY PLAY                                 #
#                                                                             #
###############################################################################

A player that reads a text file for instructions on how to censor media for small children.

# Open a media file
To play a media file, drag it into the main window's playlist and double click or press play. On windows machines, you will need install a codec pack like K-Lite Mega in order to play file types like Mp4.

# .srt files
.srt files are text files that hold the subtitles for a movie. For most movies, they can be easily downloaded online. Upon opening a video file, SafetyPlay will look for a .srt file in the same folder as the video file and will attempt to load a .srt file into the SRT dialogue window. To be loaded automatically, the srt file must have the same file name as the video. To open the srt dialogue, check the box near the playlist window. You may notice some of the lines in the .srt window are pink. SafetyPlay automatically searches through the words in a .srt file and compares them to a library of vulgar words located in a .txt file in the same directory as SafetyPlay.exe. When a match is found, the line is highlighted. You can jump to any spot on the video timeline by doubleclicking the line in the SRT dialogue. You can add or remove vulgar words from the vulgar.txt to match your own preferences.

# .saf files 
.saf files hold information that enables SafetyPlay to censor media. They are text files and can be opened and edited using any text editor. The built in text editor can be enabled by checking the box 'srt dialogue'. Drag and drop the .saf file you want to edit or load a video and begin editing the saf file for that video. Each line in a saf file must have a beginning time code, an end timecode, and an instruction. for example:

[00:00:08,000][00:00:10,600]skip

In this example, the player will skip the video from 8 seconds to 10.6 seconds. Other functions include muting and showing a .jpg image. See the 'example' folder in the same directory as SafetyPlay.exe for more examples.

# filetypes
SafetyPlay can play .mp3, .mp4, .wmv, .mkv, .mov, .ogv, .flv, .avi files. Windows users may need to install a codec pack such as K-Lite Mega in order to play all of these filetypes.

