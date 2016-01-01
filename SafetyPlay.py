from PySide import QtCore, QtGui
from PySide.phonon import Phonon
import sys
import pickle
import time
import os
import datetime

###############################################################################
#                                                                             #
#                                 MAIN WINDOW                                 #
#                                                                             #
###############################################################################

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.playing = False
        self.paused = False
        self.played = set()
        self.settings = load()
        self.resize(self.settings['size'][0], self.settings['size'][1])
        self.move(self.settings['pos'][0], self.settings['pos'][1])
        self.movie = Movie()
        self.movie.audioOutput.setVolume(self.settings['volume'])
        
        self.setupUi()
        self.cti_slider.installEventFilter(self)

        self.movie.setWindowTitle('Safety Play - Video')
        self.movie.setWindowIcon(self.icon)
        self.movie.resize(self.settings['videosize'][0],
                          self.settings['videosize'][1])
        self.movie.move(self.settings['videopos'][0],
                        self.settings['videopos'][1])

        self.srt_window = SrtList()
        self.srt_window.setWindowIcon(self.icon)
        self.srt_window.setWindowTitle('Safety Play - SRT')
        self.srt_window.resize(self.settings['srtsize'][0],
                               self.settings['srtsize'][1])
        self.srt_window.move(self.settings['srtpos'][0],
                             self.settings['srtpos'][1])

        self.saf_window = SafDialogue()
        self.saf_window.setWindowIcon(self.icon)
        self.saf_window.setWindowTitle('Safety Play - SAF')
        self.saf_window.resize(self.settings['safsize'][0],
                               self.settings['safsize'][1])
        self.saf_window.move(self.settings['safpos'][0],
                             self.settings['safpos'][1])
        
        self.muter = Muter()
        self.muter.start()

        self.skip_times = []
        self.mute_times = []
        self.image_times = []

        self.toggle_video()
        self.toggle_srt()
        self.toggle_saf()
        self.setupActions()
        self.show()

        if len(sys.argv) > 1:
            self.track_list.add_song([sys.argv[1].replace('\\','/')])
            self.play_button_clicked()

    def volume_up(self):
        if self.movie.audioOutput.volume() < 1.0:
            vol = self.movie.audioOutput.volume()
            self.movie.audioOutput.setVolume(vol + .05)
            
    def volume_down(self):
        if self.movie.audioOutput.volume() > 0.0:
            vol = self.movie.audioOutput.volume()
            self.movie.audioOutput.setVolume(vol - .05)
            
    def skipright(self):
        ct = self.movie.mediaObject.currentTime()
        self.movie.mediaObject.seek(ct + 5000)
        
    def skipleft(self):
        ct = self.movie.mediaObject.currentTime()
        if ct - 5000 > 0:
            self.movie.mediaObject.seek(ct - 5000)
        else:
            self.movie.mediaObject.seek(0)

    def jogright(self):
        ct = self.movie.mediaObject.currentTime()
        self.movie.mediaObject.seek(ct + 334)

    def jogleft(self):
        ct = self.movie.mediaObject.currentTime()
        if ct - 334 > 0:
            self.movie.mediaObject.seek(ct - 334)
        else:
            self.movie.mediaObject.seek(0)
        
    def greenify(self):
        for i in range(self.track_list.count()):
            ar = QtCore.Qt.AccessibleDescriptionRole
            if self.track_list.item(i).data(ar) == 'nowplaying':
                lg = QtGui.QColor('lightgreen')
                self.track_list.item(i).setBackground(lg)
            else:
                self.track_list.item(i).setBackground(QtGui.QColor('white'))

    def get_special_times(self, saf):
        self.skip_times = []
        self.mute_times = []
        self.black_times = []
        self.image_times = []
        file = open(saf, 'r')
        lines = file.readlines()
        file.close()
        for i in range(len(lines)):
            if lines[i].rstrip().endswith('skip'):
                l = lines[i].rstrip().replace('skip','')
                l = l.replace(']','').split('[')
                self.skip_times.append([convert_to_seconds(l[1]),
                                        convert_to_seconds(l[2])])
                
            elif lines[i].rstrip().endswith('mute'):
                l = lines[i].rstrip().replace('mute','')
                l = l.replace(']','').split('[')
                self.mute_times.append([convert_to_seconds(l[1]),
                                        convert_to_seconds(l[2])])
                
            elif lines[i].rstrip().endswith('jpg'):
                l = lines[i].rstrip().replace('[','').split(']')
                d = saf.split('/')
                d2 = ""
                for x in range(len(d) - 1):
                    d2 = d2 + d[x] + '/'
                d2 = d2 + l[2]
                self.image_times.append([convert_to_seconds(l[0]),
                                         convert_to_seconds(l[1]), d2])
        return self.skip_times, self.mute_times, self.image_times
         
    def play_doubleclicked(self, item):
        for i in range(self.track_list.count()):
            ar = QtCore.Qt.AccessibleDescriptionRole
            self.track_list.item(i).setData(ar, 'notplaying')
        self.movie.mediaObject.stop()
        self.movie.mediaObject.clear()
        self.movie.mediaObject.setQueue([item.data(QtCore.Qt.UserRole)])
        self.played.add(item.data(QtCore.Qt.UserRole))
        item.setData(QtCore.Qt.AccessibleDescriptionRole, 'nowplaying')
        self.movie.mediaObject.play()
        self.movie.audioOutput.setMuted(True)
        self.muter.start()
        self.playing = True
        nm = QtGui.QIcon.Normal
        pause = os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/pause.png'
        self.play_icon.addPixmap(pause, nm, QtGui.QIcon.Off)
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QtCore.QSize(48, 48))
        self.greenify()
        it = item.data(QtCore.Qt.UserRole)
        
        saf = item.data(QtCore.Qt.UserRole)[:len(it) - 3] + 'saf'
        if os.path.isfile(saf) and self.saf_window.text_edited == False:
            skp, mut, img = self.get_special_times(saf)
            self.skip_times = skp
            self.mute_times = mut
            self.image_times = img
            self.saf_window.add_file(saf)
        else:
            self.skip_times = []
            self.mute_times = []
            self.image_times = []

        srt = item.data(QtCore.Qt.UserRole)[:len(it) - 3] + 'srt'
        if os.path.isfile(srt):
            self.srt_window.add_srt(srt)
        
    def play_button_clicked(self):
        self.track_list.setFocus()
        if self.track_list.count() > 0:
            item = self.get_current_playing()
            it = item.data(QtCore.Qt.UserRole)
            if not self.playing and not self.paused:
                if item.text() == '':
                    item = self.track_list.item(0)
                self.movie.mediaObject.setQueue([it])
                self.played.add(item.data(QtCore.Qt.UserRole))
                item.setData(QtCore.Qt.AccessibleDescriptionRole, 'nowplaying')
                self.movie.mediaObject.play()
                self.movie.audioOutput.setMuted(True)
                self.muter.start()
                self.playing = True
                nm = QtGui.QIcon.Normal
                ico = os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/pause.png'
                self.play_icon.addPixmap(ico, nm, QtGui.QIcon.Off)
                self.play_button.setIcon(self.play_icon)
                self.play_button.setIconSize(QtCore.QSize(48, 48))
                self.greenify()

                srt = item.data(QtCore.Qt.UserRole)[:len(it) - 3] + 'srt'
                if os.path.isfile(srt):
                    self.srt_window.add_srt(srt)         
                    
            elif self.playing and not self.paused:
                self.movie.mediaObject.pause()
                self.paused = True
                nm = QtGui.QIcon.Normal
                ico = os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/play.png'
                self.play_icon.addPixmap(ico, nm, QtGui.QIcon.Off)
                self.play_button.setIcon(self.play_icon)
                self.play_button.setIconSize(QtCore.QSize(48, 48))
                self.show_time()
            elif self.playing and self.paused:
                self.movie.mediaObject.play()
                self.paused = False
                nm = QtGui.QIcon.Normal
                ico = os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/pause.png'
                self.play_icon.addPixmap(ico, nm, QtGui.QIcon.Off)
                self.play_button.setIcon(self.play_icon)
                self.play_button.setIconSize(QtCore.QSize(48, 48))

            saf = item.data(QtCore.Qt.UserRole)[:len(it) - 3] + 'saf'
            if os.path.isfile(saf) and self.saf_window.text_edited == False:
                skp, mut, img = self.get_special_times(saf)
                self.skip_times = skp
                self.mute_times = mut
                self.image_times = img
                self.saf_window.add_file(saf)
            else:
                self.skip_times = []
                self.mute_times = []
                self.image_times = []
            

    def revert_music(self):
        self.track_list.setFocus()
        if self.track_list.count() > 1:
            item_found = False
            for i in range(self.track_list.count()):
                ar = QtCore.Qt.AccessibleDescriptionRole
                if self.track_list.item(i).data(ar) == 'nowplaying':
                    if i > 0:
                        item = self.track_list.item(i - 1)
                        item_found = True
            if item_found:
                self.play_doubleclicked(item)

    def stop_music(self):
        self.track_list.setFocus()
        self.movie.mediaObject.stop()
        self.playing = False
        self.paused = False
        ico = os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/play.png'
        self.play_icon.addPixmap(ico, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QtCore.QSize(48, 48))

    def skip_music(self):
        self.track_list.setFocus()
        if self.track_list.count() > 1:
            item_found = False
            for i in range(self.track_list.count()):
                it = QtCore.Qt.AccessibleDescriptionRole
                if self.track_list.item(i).data(it) == 'nowplaying':
                    if i < self.track_list.count() - 1:
                        item = self.track_list.item(i + 1)
                        item_found = True
            if item_found:
                self.play_doubleclicked(item)

    def jump_to(self, time):
        seconds = convert_to_seconds(time)
        self.movie.mediaObject.seek(seconds * 1000)

    def check_deleted_playing(self, item):
        if item.data(QtCore.Qt.AccessibleDescriptionRole) == 'nowplaying':
            self.stop_music()

    def end_of_song(self):
        item = QtGui.QListWidgetItem()
        item.setText('')
        self.playing = False
        for i in range(self.track_list.count()):
            if self.track_list.item(i).data(QtCore.Qt.AccessibleDescriptionRole) == 'nowplaying':
                if i < self.track_list.count() - 1 and not self.shuffle_button.isChecked():
                    item = self.track_list.item(i+1)
                elif i == self.track_list.count() - 1 and self.loop_button.isChecked() and not self.shuffle_button.isChecked():
                    item = self.track_list.item(0)
                elif self.shuffle_button.isChecked():
                    all_songs = set()
                    for z in range(self.track_list.count()):
                        all_songs.add(self.track_list.item(z).data(QtCore.Qt.UserRole))
                    not_played = list(all_songs - self.played)
                    if not_played == []:
                        not_played = list(all_songs)
                        self.played = set()
                    song = not_played[random.randint(0, len(not_played) - 1)]
                    for x in range(self.track_list.count()):
                        if self.track_list.item(x).data(QtCore.Qt.UserRole) == song:
                            item = self.track_list.item(x)
        if not item.text() == '':
            self.play_doubleclicked(item)
        else:
            self.stop_music()
            
    def get_current_playing(self):
        item = QtGui.QListWidgetItem()
        item.setText('')
        for i in range(self.track_list.count()):
            if self.track_list.item(i).data(QtCore.Qt.AccessibleDescriptionRole) == 'nowplaying':
                return self.track_list.item(i)
        return item

    def show_time(self):
        t = self.movie.mediaObject.currentTime()/1000
        self.current_time.setText(sec_to_minutes_seconds(t))

        for i in range(len(self.skip_times)):
            if t > self.skip_times[i][0] and t < self.skip_times[i][1]:
                self.movie.mediaObject.seek(self.skip_times[i][1] * 1000)

        mute_found = False
        for i in range(len(self.mute_times)):
            if t > self.mute_times[i][0] and t < self.mute_times[i][1]:
                mute_found = True
                self.movie.audioOutput.setMuted(True)

        if mute_found == False:
            self.movie.audioOutput.setMuted(False)

        image_found = False
        for i in range(len(self.image_times)):
            if t > self.image_times[i][0] and t < self.image_times[i][1]:
                image_found = True
                self.movie.overlay.draw(self.image_times[i][2])
                self.movie.overlay.show()
        if image_found == False:
            self.movie.overlay.hide()

    def toggle_video(self):
        if self.video_checkbox.isChecked():
            self.movie.show()
        else:
            self.movie.hide()

    def toggle_srt(self):
        if self.subtitles_checkbox.isChecked():
            self.srt_window.show()
        else:
            self.srt_window.hide()

    def toggle_saf(self):
        if self.saf_checkbox.isChecked():
            self.saf_window.show()
        else:
            self.saf_window.hide()

    def send_save(self):
        if self.playing:
            vid_file = self.get_current_playing().data(QtCore.Qt.UserRole)
            saf = vid_file[0:len(vid_file)-3] + 'saf'
            self.saf_window.current_file = saf
            self.saf_window.check_errors()

    def uncheck_video(self):
        self.video_checkbox.setChecked(False)

    def uncheck_srt(self):
        self.subtitles_checkbox.setChecked(False)

    def uncheck_saf(self):
        self.saf_checkbox.setChecked(False)

    def unmute(self):
        self.movie.audioOutput.setMuted(False)

    def record_time(self):
        if self.playing:
            t = self.movie.mediaObject.currentTime()/1000
            time = '[' + sec_to_minutes_seconds(t) + ']'
            self.saf_window.plainTextEdit.insertPlainText(time)

    def refocus(self):
        self.track_list.setFocus()

    def eventFilter(self, obj, event):
        if obj is self.cti_slider and event.type() == QtCore.QEvent.ShortcutOverride:
            # Send the event up the hierarchy
            event.ignore()
            # Stop obj from treating the event itself
            return True

        # Events which don't concern us get forwarded
        return super(MainWindow, self).eventFilter(obj, event)
        
    def closeEvent(self, event):
        self.muter.terminate()
        self.movie.mediaObject.stop()
        self.movie.close()
        self.srt_window.close()
        self.saf_window.close()

    def moveEvent(self, event):
        self.save()

    def resizeEvent(self, event):
        self.save()

    def save(self):
        size = [self.width(), self.height()]
        pos = [self.x(), self.y()]
        srt = self.subtitles_checkbox.isChecked()
        srtsize = [self.srt_window.width(), self.srt_window.height()]
        srtpos = [self.srt_window.x(), self.srt_window.y()]
        video = self.video_checkbox.isChecked()
        videosize = [self.movie.width(), self.movie.height()]
        videopos = [self.movie.x(), self.movie.y()]
        saf = self.saf_checkbox.isChecked()
        safsize = [self.saf_window.width(), self.saf_window.height()]
        safpos = [self.saf_window.x(), self.saf_window.y()]
        volume = self.movie.audioOutput.volume()
        loop = self.loop_button.isChecked()
        shuffle = self.shuffle_button.isChecked()

        dictionary = {'size' : size,
                      'pos' : pos,
                      'srt' : srt,
                      'srtsize' : srtsize,
                      'srtpos' : srtpos,
                      'video' : video,
                      'videosize' : videosize,
                      'videopos' : videopos,
                      'saf' : saf,
                      'safsize' : safsize,
                      'safpos' : safpos,
                      'volume' : volume,
                      'loop' : loop,
                      'shuffle' : shuffle}
                
        pickle.dump(dictionary, open(os.path.abspath(os.path.dirname(sys.argv[0])) + '/save.p', 'wb'))
        
    def setupActions(self):
        self.track_list.vol_up.connect(self.volume_up)
        self.track_list.vol_down.connect(self.volume_down)
        self.track_list.skipright.connect(self.skipright)
        self.track_list.skipleft.connect(self.skipleft)
        self.track_list.jogright.connect(self.jogright)
        self.track_list.jogleft.connect(self.jogleft)
        self.track_list.play_pause.connect(self.play_button_clicked)
        self.track_list.revert.connect(self.revert_music)
        self.track_list.stop.connect(self.stop_music)
        self.track_list.jump.connect(self.skip_music)
        self.track_list.itemDoubleClicked.connect(self.play_doubleclicked)
        self.track_list.greenify.connect(self.greenify)
        self.track_list.deleted.connect(self.check_deleted_playing)

        self.movie.mediaObject.tick.connect(self.show_time)
        self.movie.mediaObject.finished.connect(self.end_of_song)

        self.play_button.clicked.connect(self.play_button_clicked)
        self.revert_button.clicked.connect(self.revert_music)
        self.stop_button.clicked.connect(self.stop_music)
        self.skip_button.clicked.connect(self.skip_music)

        self.video_checkbox.clicked.connect(self.toggle_video)
        self.movie.movie_exit.connect(self.uncheck_video)
        self.subtitles_checkbox.clicked.connect(self.toggle_srt)
        self.saf_checkbox.clicked.connect(self.toggle_saf)

        self.subtitles_checkbox.clicked.connect(self.save)
        self.subtitles_checkbox.clicked.connect(self.refocus)
        self.video_checkbox.clicked.connect(self.save)
        self.video_checkbox.clicked.connect(self.refocus)
        self.saf_checkbox.clicked.connect(self.save)
        self.saf_checkbox.clicked.connect(self.refocus)
        self.loop_button.clicked.connect(self.save)
        self.loop_button.clicked.connect(self.refocus)
        self.shuffle_button.clicked.connect(self.save)
        self.shuffle_button.clicked.connect(self.refocus)
        self.movie.audioOutput.volumeChanged.connect(self.save)
        self.movie.moving.connect(self.save)
        self.movie.resizing.connect(self.save)

        self.muter.time_up.connect(self.unmute)

        self.movie.skipright.connect(self.skipright)
        self.movie.skipleft.connect(self.skipleft)
        self.movie.jogright.connect(self.jogright)
        self.movie.jogleft.connect(self.jogleft)
        self.movie.vol_up.connect(self.volume_up)
        self.movie.vol_down.connect(self.volume_down)
        self.movie.play_pause.connect(self.play_button_clicked)
        self.movie.revert.connect(self.revert_music)
        self.movie.stop.connect(self.stop_music)
        self.movie.jump.connect(self.skip_music)

        self.srt_window.time_clicked.connect(self.jump_to)
        self.srt_window.srt_exit.connect(self.uncheck_srt)
        self.srt_window.moving.connect(self.save)
        self.srt_window.resizing.connect(self.save)

        self.saf_window.record_request.connect(self.record_time)
        self.saf_window.moving.connect(self.save)
        self.saf_window.resizing.connect(self.save)
        self.saf_window.saf_exit.connect(self.uncheck_saf)
        self.saf_window.save_request.connect(self.send_save)

        self.cti_slider.play_pause.connect(self.play_button_clicked)
        self.cti_slider.revert.connect(self.revert_music)
        self.cti_slider.stop.connect(self.stop_music)
        self.cti_slider.jump.connect(self.skip_music)
        self.cti_slider.jogright.connect(self.jogright)
        self.cti_slider.jogleft.connect(self.jogleft)
        
    def setupUi(self):
        #ICON
        self.icon_img = os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/icon.ico'
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(self.icon_img, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)
        
        #Window Settings
        self.setWindowTitle('Safety Play - Playlist')
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        #Track List
        self.track_list = SongList(self)
        self.track_list.setObjectName("track_list")
        self.verticalLayout.addWidget(self.track_list)

        #CTI Slider
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cti_slider = CTI()#Phonon.SeekSlider(self)
        self.cti_slider.setMediaObject(self.movie.mediaObject)
        self.cti_slider.setOrientation(QtCore.Qt.Horizontal)
        self.cti_slider.setObjectName("cti_slider")
        self.cti_slider.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.cti_slider.setSingleStep(5000)
        self.horizontalLayout_2.addWidget(self.cti_slider)

        #Current Time
        self.current_time = QtGui.QLabel(self)
        self.current_time.setObjectName("current_time")
        self.current_time.setText("00:00:00,000")
        self.horizontalLayout_2.addWidget(self.current_time)

        #More Layouts
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        #SAF Checkbox
        self.saf_checkbox = QtGui.QCheckBox(self)
        self.saf_checkbox.setObjectName("saf_checkbox")
        self.saf_checkbox.setText("SAF Dialogue")
        self.saf_checkbox.setChecked(self.settings['saf'])
        self.saf_checkbox.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout_3.addWidget(self.saf_checkbox)

        #subtitles Checkbox
        self.subtitles_checkbox = QtGui.QCheckBox(self)
        self.subtitles_checkbox.setObjectName("subtitles_checkbox")
        self.subtitles_checkbox.setText("SRT Dialogue")
        self.subtitles_checkbox.setChecked(self.settings['srt'])
        self.subtitles_checkbox.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout_3.addWidget(self.subtitles_checkbox)

        #Video Checkbox
        self.video_checkbox = QtGui.QCheckBox(self)
        self.video_checkbox.setObjectName("visualizer_checkbox")
        self.video_checkbox.setText("Video Window")
        self.video_checkbox.setChecked(self.settings['video'])
        self.video_checkbox.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout_3.addWidget(self.video_checkbox)

        #More Layouts
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")

        #Play Button
        self.play_button = QtGui.QPushButton(self)
        self.play_icon = QtGui.QIcon()
        self.play_icon.addPixmap(os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/play.png', QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QtCore.QSize(48, 48))
        self.play_button.setMinimumSize(QtCore.QSize(48, 48))
        self.play_button.setMaximumSize(QtCore.QSize(48, 48))
        self.play_button.setText("")
        self.play_button.setObjectName("play_button")
        self.play_button.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout.addWidget(self.play_button)

        #Revert Button
        self.revert_button = QtGui.QPushButton(self)
        self.revert_icon = QtGui.QIcon()
        self.revert_icon.addPixmap(os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/revert.png', QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.revert_button.setIcon(self.revert_icon)
        self.revert_button.setIconSize(QtCore.QSize(48, 48))
        self.revert_button.setMinimumSize(QtCore.QSize(48, 48))
        self.revert_button.setMaximumSize(QtCore.QSize(48, 48))
        self.revert_button.setText("")
        self.revert_button.setObjectName("revert_button")
        self.revert_button.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout.addWidget(self.revert_button)
        #self.revert_button.setEnabled(False)
        
        #Stop Button
        self.stop_button = QtGui.QPushButton(self)
        self.stop_icon = QtGui.QIcon()
        self.stop_icon.addPixmap(os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/stop.png', QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.setIconSize(QtCore.QSize(48, 48))
        self.stop_button.setMinimumSize(QtCore.QSize(48, 48))
        self.stop_button.setMaximumSize(QtCore.QSize(48, 48))
        self.stop_button.setText("")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout.addWidget(self.stop_button)
        #self.stop_button.setEnabled(False)

        #Skip Button
        self.skip_button = QtGui.QPushButton(self)
        self.skip_icon = QtGui.QIcon()
        self.skip_icon.addPixmap(os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/skip.png', QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.skip_button.setIcon(self.skip_icon)
        self.skip_button.setIconSize(QtCore.QSize(48, 48))
        self.skip_button.setMinimumSize(QtCore.QSize(48, 48))
        self.skip_button.setMaximumSize(QtCore.QSize(48, 48))
        self.skip_button.setText("")
        self.skip_button.setObjectName("skip_button")
        self.skip_button.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout.addWidget(self.skip_button)
        #self.skip_button.setEnabled(False)

        #Loop Button
        self.loop_button = QtGui.QPushButton(self)
        self.loop_icon = QtGui.QIcon()
        self.loop_icon.addPixmap(os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/loop.png', QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loop_button.setIcon(self.loop_icon)
        self.loop_button.setIconSize(QtCore.QSize(48, 48))
        self.loop_button.setMinimumSize(QtCore.QSize(48, 48))
        self.loop_button.setMaximumSize(QtCore.QSize(48, 48))
        self.loop_button.setText("")
        self.loop_button.setObjectName("loop_button")
        self.loop_button.setCheckable(True)
        self.loop_button.setChecked(self.settings['loop'])
        self.loop_button.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout.addWidget(self.loop_button)
        
        #Shuffle Button
        self.shuffle_button = QtGui.QPushButton(self)
        self.shuffle_icon = QtGui.QIcon()
        self.shuffle_icon.addPixmap(os.path.abspath(os.path.dirname(sys.argv[0])) + '/images/shuffle.png', QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.shuffle_button.setIcon(self.shuffle_icon)
        self.shuffle_button.setIconSize(QtCore.QSize(48, 48))
        self.shuffle_button.setMinimumSize(QtCore.QSize(48, 48))
        self.shuffle_button.setMaximumSize(QtCore.QSize(48, 48))
        self.shuffle_button.setText("")
        self.shuffle_button.setObjectName("shuffle_button")
        self.shuffle_button.setCheckable(True)
        self.shuffle_button.setChecked(self.settings['shuffle'])
        self.shuffle_button.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.horizontalLayout.addWidget(self.shuffle_button)

        #Volume Slider
        self.volume_slider = Phonon.VolumeSlider(self)
        self.volume_slider.setAudioOutput(self.movie.audioOutput)
        self.volume_slider.setObjectName("volume_slider")
        self.volume_slider.setMinimumSize(QtCore.QSize(100, 0))
        self.volume_slider.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.volume_slider.setMuteVisible(False)
        self.horizontalLayout.addWidget(self.volume_slider)
        

        self.verticalLayout.addLayout(self.horizontalLayout)

###############################################################################
#                                                                             #
#                                 CTI SLIDER                                  #
#                                                                             #
###############################################################################

class CTI(Phonon.SeekSlider):
    play_pause = QtCore.Signal()
    revert = QtCore.Signal()
    stop = QtCore.Signal()
    jump = QtCore.Signal()
    jogright = QtCore.Signal()
    jogleft = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(CTI, self).__init__(parent)
        shortcut_r = QtGui.QShortcut(QtGui.QKeySequence('Right'), self)
        shortcut_r.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_r.activated.connect(self.test)

        shortcut_l = QtGui.QShortcut(QtGui.QKeySequence('Left'), self)
        shortcut_l.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_l.activated.connect(self.test)

        shortcut_u = QtGui.QShortcut(QtGui.QKeySequence('Up'), self)
        shortcut_u.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_u.activated.connect(self.test)

        shortcut_d = QtGui.QShortcut(QtGui.QKeySequence('Down'), self)
        shortcut_d.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_d.activated.connect(self.test)

        shortcut_cr = QtGui.QShortcut(QtGui.QKeySequence('ctrl+Right'), self)
        shortcut_cr.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_cr.activated.connect(self.test)

        shortcut_cl = QtGui.QShortcut(QtGui.QKeySequence('ctrl+Left'), self)
        shortcut_cl.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_cl.activated.connect(self.test)

        shortcut_cu = QtGui.QShortcut(QtGui.QKeySequence('ctrl+Up'), self)
        shortcut_cu.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_cu.activated.connect(self.test)

        shortcut_cd = QtGui.QShortcut(QtGui.QKeySequence('ctrl+Down'), self)
        shortcut_cd.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_cd.activated.connect(self.test)

        shortcut_su = QtGui.QShortcut(QtGui.QKeySequence('Shift+Up'), self)
        shortcut_su.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_su.activated.connect(self.test)

        shortcut_sd = QtGui.QShortcut(QtGui.QKeySequence('Shift+Down'), self)
        shortcut_sd.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_sd.activated.connect(self.test)

        shortcut_au = QtGui.QShortcut(QtGui.QKeySequence('alt+Up'), self)
        shortcut_au.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_au.activated.connect(self.test)

        shortcut_ad = QtGui.QShortcut(QtGui.QKeySequence('alt+Down'), self)
        shortcut_ad.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_ad.activated.connect(self.test)

        shortcut_sr = QtGui.QShortcut(QtGui.QKeySequence('Shift+Right'), self)
        shortcut_sr.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_sr.activated.connect(self.jogright_fxn)

        shortcut_sl = QtGui.QShortcut(QtGui.QKeySequence('Shift+Left'), self)
        shortcut_sl.setContext(QtCore.Qt.ApplicationShortcut)
        shortcut_sl.activated.connect(self.jogleft_fxn)   

    def test(self):
        pass

    def jogright_fxn(self):
        self.jogright.emit()

    def jogleft_fxn(self):
        self.jogleft.emit()
            
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_P:
            self.play_pause.emit()

        elif event.key() == QtCore.Qt.Key_R:
            self.revert.emit()

        elif event.key() == QtCore.Qt.Key_S:
            self.stop.emit()

        elif event.key() == QtCore.Qt.Key_J:
            self.jump.emit()
        
###############################################################################
#                                                                             #
#                                  PLAYLIST                                   #
#                                                                             #
###############################################################################

class SongList(QtGui.QListWidget):
    #Creates a playlist window
    #Drag and drop Mp3, Mp4, or wmv files
    #Use mouse wheel to control volume
    #Use delete key to remove an item
    #Use keys: P, R, S, or J to Play, revert, stop, jump
    file_dropped = QtCore.Signal(list)
    greenify = QtCore.Signal()
    deleted = QtCore.Signal(object)
    skipright = QtCore.Signal()
    skipleft = QtCore.Signal()
    jogright = QtCore.Signal()
    jogleft = QtCore.Signal()
    vol_up = QtCore.Signal()
    vol_down = QtCore.Signal()
    play_pause = QtCore.Signal()
    revert = QtCore.Signal()
    stop = QtCore.Signal()
    jump = QtCore.Signal()
    
    
    def __init__(self, parent=None):
        super(SongList, self).__init__(parent)
        self.safelist = ['.mp3', '.mp4', '.wmv', '.mkv', '.mov', '.ogv', '.flv', '.avi']
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)
        self.file_dropped.connect(self.add_song)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            path = str(event.mimeData().urls()[0].toLocalFile())
            ending = path[len(path)-4::]
            if ending in self.safelist:
                event.accept()
            else:
                event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            files = []
            for i in range(len(event.mimeData().urls())):
                files.append(str(event.mimeData().urls()[i].toLocalFile()))
            self.file_dropped.emit(files)
        else:
            event.ignore()

    def add_song(self, files):
        for file in files:
            new_item = QtGui.QListWidgetItem()
            new_item.setData(QtCore.Qt.UserRole, file)
            new_item.setData(QtCore.Qt.AccessibleDescriptionRole, 'notplaying')
            new_item.setText(file.split('/')[len(file.split('/'))-1])
            self.addItem(new_item)

    def wheelEvent(self, event):
        if event.delta() < 0:
            self.vol_down.emit()
        elif event.delta() > 0:
            self.vol_up.emit()
            
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete and len(self.selectedItems()) > 0:
            for i in self.selectedItems():
                self.deleted.emit(self.takeItem(self.row(i)))
                
        #Moving items up and down in the list
        elif event.key() == QtCore.Qt.Key_Up and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier and len(self.selectedItems()) > 0:
            items = self.ordered(self.selectedItems())
            top_row = self.row(items[0])
            new_items = []
            if top_row > 0:
                for i in items:
                    new_items.append(i.data(QtCore.Qt.UserRole) + '*' + i.data(QtCore.Qt.AccessibleDescriptionRole))
                    self.takeItem(self.row(i))
                self.insertItems(top_row-1, new_items)
            for i in range(len(new_items)):
                item = self.item((top_row-1) + i)
                item.setData(QtCore.Qt.UserRole, item.text().split('*')[0])
                item.setData(QtCore.Qt.AccessibleDescriptionRole, item.text().split('*')[1])
                item.setText(item.text().split('*')[0].split('/')[len(item.text().split('*')[0].split('/'))-1])
                item.setSelected(True)
            self.greenify.emit()

        elif event.key() == QtCore.Qt.Key_Down and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier and len(self.selectedItems()) > 0:
            items = self.ordered(self.selectedItems())
            new_items = []
            bottom_row = self.row(items[-1]) + 1
            if bottom_row < self.count():
                for i in items:
                    new_items.append(i.data(QtCore.Qt.UserRole) + '*' + i.data(QtCore.Qt.AccessibleDescriptionRole))
                    self.takeItem(self.row(i))
                    bottom_row -= 1
                bottom_row += 1
                self.insertItems(bottom_row, new_items)
            for i in range(len(new_items)):
                item = self.item((bottom_row) + i)
                item.setData(QtCore.Qt.UserRole, item.text().split('*')[0])
                item.setData(QtCore.Qt.AccessibleDescriptionRole, item.text().split('*')[1])
                item.setText(item.text().split('*')[0].split('/')[len(item.text().split('*')[0].split('/'))-1])
                item.setSelected(True)
            self.greenify.emit()
            
        #Seeking
        elif event.key() == QtCore.Qt.Key_Right and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
            self.skipright.emit()

        elif event.key() == QtCore.Qt.Key_Left and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
            self.skipleft.emit()

        elif event.key() == QtCore.Qt.Key_Left and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.jogleft.emit()

        elif event.key() == QtCore.Qt.Key_Right and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.jogright.emit()
            
        #Pause/Play, revert, stop, jump
        elif event.key() == QtCore.Qt.Key_P:
            self.play_pause.emit()

        elif event.key() == QtCore.Qt.Key_R:
            self.revert.emit()

        elif event.key() == QtCore.Qt.Key_S:
            self.stop.emit()

        elif event.key() == QtCore.Qt.Key_J:
            self.jump.emit()
            

    def ordered(self, i_list):
        #Orders the list by the item's row, instead of selection order
        numbers = []
        o_list = []

        #Get the row numbers of the items and sort them
        for i in range(len(i_list)):
            numbers.append(self.row(i_list[i]))
        numbers = sorted(numbers)

        #Create a list of items in the order
        for i in range(len(numbers)):
            for x in i_list:
                if self.row(x) == numbers[i]:
                    o_list.append(x)
        return o_list

###############################################################################
#                                                                             #
#                               UNMUTER THREAD                                #
#                                                                             #
###############################################################################

class Muter(QtCore.QThread):
    time_up = QtCore.Signal()
    def run(self):
        time.sleep(.5)
        self.time_up.emit()

###############################################################################
#                                                                             #
#                                VIDEO WINDOW                                 #
#                                                                             #
###############################################################################

class Movie(Phonon.VideoWidget):
    movie_exit = QtCore.Signal()
    moving = QtCore.Signal()
    resizing = QtCore.Signal()

    skipright = QtCore.Signal()
    skipleft = QtCore.Signal()
    jogright = QtCore.Signal()
    jogleft = QtCore.Signal()
    vol_up = QtCore.Signal()
    vol_down = QtCore.Signal()
    play_pause = QtCore.Signal()
    revert = QtCore.Signal()
    stop = QtCore.Signal()
    jump = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(Movie, self).__init__(parent)
        self.audioOutput = Phonon.AudioOutput(Phonon.VideoCategory)
        self.mediaObject = Phonon.MediaObject(self)
        Phonon.createPath(self.mediaObject, self)
        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.overlay = DrawWidge(self)
        self.overlay.resize(self.width(), self.height())
        self.overlay.hide()
        

    def fullscreen(self):
        screen_width = QtGui.QDesktopWidget().screenGeometry().width()
        screen_height = QtGui.QDesktopWidget().screenGeometry().height()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.resize(screen_width, screen_height)
        self.move(0, 0)
        self.show()
        
    def normal_size(self):
        self.resize(600, 400)
        self.setWindowFlags(QtCore.Qt.WindowMinMaxButtonsHint)
        self.show()

    def wheelEvent(self, event):
        if event.delta() < 0:
            self.vol_down.emit()
        elif event.delta() > 0:
            self.vol_up.emit()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.normal_size()

        if event.key() == QtCore.Qt.Key_F:
            self.fullscreen()

        #Seeking
        elif event.key() == QtCore.Qt.Key_Right and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
            self.skipright.emit()

        elif event.key() == QtCore.Qt.Key_Left and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
            self.skipleft.emit()

        elif event.key() == QtCore.Qt.Key_Left and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.jogleft.emit()

        elif event.key() == QtCore.Qt.Key_Right and QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.jogright.emit()

        #Pause/Play, revert, stop, jump
        elif event.key() == QtCore.Qt.Key_P:
            self.play_pause.emit()

        elif event.key() == QtCore.Qt.Key_R:
            self.revert.emit()

        elif event.key() == QtCore.Qt.Key_S:
            self.stop.emit()

        elif event.key() == QtCore.Qt.Key_J:
            self.jump.emit()

    def moveEvent(self, event):
        self.moving.emit()

    def resizeEvent(self, event):
        self.resizing.emit()
        self.overlay.resize(self.width(), self.height())

    def closeEvent(self, event):
        self.movie_exit.emit()

###############################################################################
#                                                                             #
#                            VIDEO COVERUP WIDGET                             #
#                                                                             #
###############################################################################

class DrawWidge(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DrawWidge, self).__init__(parent)
        self.setStyleSheet("background-color: \'black\'")
        self.pic = QtGui.QPixmap("")
        self.source = ""

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), self.pic)

    def draw(self, source):
        self.source = source
        self.pic = QtGui.QPixmap(source)
        self.update()

###############################################################################
#                                                                             #
#                                 SRT WINDOW                                  #
#                                                                             #
###############################################################################

class SrtList(QtGui.QListWidget):
    moving = QtCore.Signal()
    resizing = QtCore.Signal()
    srt_exit = QtCore.Signal()
    time_clicked = QtCore.Signal(str)
    def __init__(self, parent=None):
        super(SrtList, self).__init__(parent)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)
        self.safelist = ['.srt']

        file = open(os.path.abspath(os.path.dirname(sys.argv[0])) + '/' + 'vulgar.txt', 'r')
        lines = file.readlines()
        file.close()
        self.vulgars = []
        for i in range(len(lines)):
            if not lines[i].rstrip() == '':
                self.vulgars.append(lines[i].rstrip())

        self.itemDoubleClicked.connect(self.goto)

    def goto(self, item):
        self.time_clicked.emit(item.text().split(' ')[0].replace('[','').replace(']',''))

    def add_srt(self, srt):
        self.clear()
        segments = parse_srt(srt)
        for i in range(len(segments)):
            start = '[' + sec_to_minutes_seconds(segments[i].start_time) + '] '
            if not segments[i].topline == '':
                words = segments[i].topline + ' ' + segments[i].bottomline
            else:
                words = segments[i].bottomline

            new_item = QtGui.QListWidgetItem()
            new_item.setText(start + words)
            if check_vulgar(self.vulgars, words):
                new_item.setBackground(QtGui.QColor('pink'))
            self.addItem(new_item)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            path = str(event.mimeData().urls()[0].toLocalFile())
            ending = path[len(path)-4::]
            if ending in self.safelist:
                event.accept()
            else:
                event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            #self.file_dropped.emit(str(event.mimeData().urls()[0].toLocalFile()))
            self.add_srt(str(event.mimeData().urls()[0].toLocalFile()))
        else:
            event.ignore()

    def moveEvent(self, event):
        self.moving.emit()

    def resizeEvent(self, event):
        self.resizing.emit()

    def closeEvent(self, event):
        self.srt_exit.emit()

###############################################################################
#                                                                             #
#                                 SRT SEGMENT                                 #
#                                                                             #
###############################################################################

class Segment():
    def __init__(self):
        self.segment_number = 0
        self.start_time = 0.0
        self.end_time = 0.0
        self.topline = ''
        self.bottomline = ''

###############################################################################
#                                                                             #
#                                 SAF WINDOW                                  #
#                                                                             #
###############################################################################

class SafDialogue(QtGui.QWidget):
    moving = QtCore.Signal()
    resizing = QtCore.Signal()
    record_request = QtCore.Signal()
    save_request = QtCore.Signal()
    saf_exit = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(SafDialogue, self).__init__(parent)
        self.setAcceptDrops(True)
        self.safelist = ['.saf']

        self.current_file = ""
        self.text_edited = False
        
        self.vl = QtGui.QVBoxLayout(self)
        self.plainTextEdit = QtGui.QPlainTextEdit()
        self.vl.addWidget(self.plainTextEdit)

        self.hl = QtGui.QHBoxLayout()

        self.record_button = QtGui.QPushButton()
        self.record_button.setText('Record Time')
        self.hl.addWidget(self.record_button)

        self.sort_button = QtGui.QPushButton()
        self.sort_button.setText('Sort')
        self.hl.addWidget(self.sort_button)

        self.save_button = QtGui.QPushButton()
        self.save_button.setText('Save')
        self.hl.addWidget(self.save_button)

        self.vl.addLayout(self.hl)

        self.save_closer = SaveCloser()
        self.save_closer.start()
        
        self.save_message = Saved(self)
        self.save_message.hide()

        self.save_button.clicked.connect(self.check_errors)
        self.sort_button.clicked.connect(self.sort)
        self.record_button.clicked.connect(self.record)
        self.save_closer.time_up.connect(self.hide_save)
        self.plainTextEdit.textChanged.connect(self.text_was_changed)

    def text_was_changed(self):
        self.text_edited = True

    def record(self):
        self.record_request.emit()

    def write_record(self, line):
        self.plainTextEdit.appendPlainText(line)

    def check_errors(self):
        lines = self.plainTextEdit.toPlainText().split('\n')
        checked = []
        for i in range(len(lines)):
            if not lines[i] == '' and not lines[i].startswith('#'):
                checked.append(lines[i])
        lines = checked
        
        for i in range(len(lines)):
            if not lines[i].endswith('skip') and not lines[i].endswith('mute') and not lines[i].endswith('.jpg') and not lines[i] == '':
                self.highlight(self.get_index(lines, i), i)
                return False
        
        for i in range(len(lines)):
            words = lines[i].replace('[', '').split(']')
            try:
                t = datetime.datetime.strptime(words[0], "%H:%M:%S,%f")
                t = datetime.datetime.strptime(words[1], "%H:%M:%S,%f")
            except IndexError:
                
                self.highlight(self.get_index(lines, i), i)
                return False
            except ValueError:
                self.highlight(self.get_index(lines, i), i)
                return False
            if len(words) != 3:
                self.highlight(self.get_index(lines, i), i)
                return False
            if ' ' in words[2]:
                self.highlight(self.get_index(lines, i), i)
                return False
        try:
            file = open(self.current_file, 'w')
            text = self.plainTextEdit.toPlainText()
            file.write(text)
            file.close()
            self.show_save_message()
        except FileNotFoundError:
            self.save_request.emit()

    def get_index(self, lines, line_number):
        total = 0
        for i in range(0, line_number):
            total = total + len(lines[i]) + 1
        return total      

    def show_save_message(self):
        self.save_message.resize(self.width(), self.height())
        self.save_message.show()
        self.save_closer.start()
        self.text_edited = False

        lines = self.plainTextEdit.toPlainText().split('\n')
        index = 0
        for i in range(len(lines)):
            cursor = self.plainTextEdit.textCursor()
            format = QtGui.QTextCharFormat()
            format.setBackground(QtGui.QBrush(QtGui.QColor("white")))
            cursor.setPosition(index)
            cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor, 1)
            cursor.mergeCharFormat(format)
            index = index + len(lines[i]) + 1

    def hide_save(self):
        self.save_message.hide()

    def highlight(self, index, line):
        cursor = self.plainTextEdit.textCursor()
        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QBrush(QtGui.QColor("pink")))
        cursor.setPosition(index)
        cursor.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor, 1)
        cursor.mergeCharFormat(format)

        cursor.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.MoveAnchor, 1)
        self.plainTextEdit.verticalScrollBar().setValue(line)
        
    def sort(self):
        lines = self.plainTextEdit.toPlainText().split('\n')
        cleaned = []
        for i in range(len(lines)):
            if not lines[i] == '':
                cleaned.append(lines[i])
        self.plainTextEdit.clear()
        string = ""
        cleaned = sorted(cleaned)
        for i in range(len(cleaned)):
            if not i == len(cleaned) - 1:
                string = string + cleaned[i] + '\n'
            else:
                string = string + cleaned[i]
        self.plainTextEdit.appendPlainText(string)
            

    def add_file(self, file):
        self.current_file = file
        self.plainTextEdit.clear()
        try:
            f = open(file, 'r')
            lines = f.readlines()
            f.close()
            string = ""
            for i in range(len(lines)):
                string = string + lines[i]
            self.plainTextEdit.appendPlainText(string)
        except FileNotFoundError:
            pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            try:
                path = str(event.mimeData().urls()[0].toLocalFile())
                ending = path[len(path)-4::]
                if ending in self.safelist:
                    event.accept()
                else:
                    event.ignore()
            except IndexError:
                pass
            

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            self.add_file(str(event.mimeData().urls()[0].toLocalFile()))
        else:
            event.ignore()

    def moveEvent(self, event):
        self.moving.emit()

    def resizeEvent(self, event):
        self.resizing.emit()

    def closeEvent(self, event):
        self.saf_exit.emit()

###############################################################################
#                                                                             #
#                                SAVED MESSAGE                                #
#                                                                             #
###############################################################################

class Saved(QtGui.QLabel):
    def __init__(self, parent=None):
        super(Saved, self).__init__(parent)
        self.setText('Saved')
        self.setFont(QtGui.QFont("MS Shell Dlg 2", 24, QtGui.QFont.Bold))
        self.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

###############################################################################
#                                                                             #
#                         SAVE MESSAGE CLOSER THREAD                          #
#                                                                             #
###############################################################################

class SaveCloser(QtCore.QThread):
    time_up = QtCore.Signal()
    def run(self):
        time.sleep(1)
        self.time_up.emit()

###############################################################################
#                                                                             #
#                              UTILITY FUNCTIONS                              #
#                                                                             #
###############################################################################

def default_dictionary():
    screen_width = QtGui.QDesktopWidget().screenGeometry().width()
    screen_height = QtGui.QDesktopWidget().screenGeometry().height()
    
    dictionary = {'size' : [454, 442],
                  'pos' : [screen_width/2, screen_height/2],
                  'srt' : False,
                  'srtsize' : [454, 442],
                  'srtpos' : [screen_width/3, screen_height/3],
                  'video' : False,
                  'videosize' : [600, 400],
                  'videopos' : [0, 0],
                  'saf' : False,
                  'safsize' : [454, 442],
                  'safpos' : [screen_width/4, screen_height/4],
                  'volume' : 1.0,
                  'loop' : False,
                  'shuffle' : False}
    return dictionary

def load():
    try :
        dictionary = pickle.load(open(os.path.abspath(os.path.dirname(sys.argv[0])) + '/save.p', 'rb'))
    except FileNotFoundError:
        dictionary = default_dictionary()
    return dictionary

def convert_to_seconds(timecode):
    #convert a timecode '00:00:00,000' to seconds
    t = datetime.datetime.strptime(timecode, "%H:%M:%S,%f")
    seconds = (60 * t.minute) + (3600 * t.hour) + t.second
    fraction = t.microsecond/1000000
    combo = seconds + fraction
    return combo

def sec_to_minutes_seconds(seconds):
    #returns '00:00:00.000 format
    h = int(seconds/3600)
    m = int((seconds % 3600) / 60)
    s = int((seconds % 3600) % 60) 
    ms = int((seconds - int(seconds))*1000)
    h = to_2_str(h)
    m = to_2_str(m)
    s = to_2_str(s)

    if ms < 100 and ms > 10:
        ms = '0' + str(ms)
    elif ms < 10 and ms > 0:
        ms = '00' + str(ms)
    elif ms == 0:
        ms = '000'
    else:
        ms = str(ms)

    end = ''.join([h, ':', m,':',s,',',ms])
    return end

def to_2_str(number):
    #For converting a number to a string with at least 2 digits
    if number < 10:
        number = '0' + str(number)
    else:
        number = str(number)
    return number

def parse_srt(file):
    #Open an srt file and convert its sections into segments
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    separated = []
    temp = []
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
        if not lines[i] == '':
            temp.append(lines[i])
        else:
            separated.append(temp)
            temp = []
    separated.append(temp)

    for s in separated:
        if s == []:
            separated.pop(separated.index([]))
            
    segments = []
    for i in range(len(separated)):
        seg = i + 1
        start = convert_to_seconds(separated[i][1].split(' --> ')[0])
        end = convert_to_seconds(separated[i][1].split(' --> ')[1])
        try:
            line_1 = separated[i][2]
        except IndexError:
            line_1 = ''
        if len(separated[i]) > 3:
            line_2 = separated[i][3]
        segments.append(Segment())
        segments[i].segment_number = seg
        segments[i].start_time = start
        segments[i].end_time = end
        if len(separated[i]) > 3:
            segments[i].topline = line_1
            segments[i].bottomline = line_2
        else:
            segments[i].bottomline = line_1

    return segments

def remove_punc(s):
    #Removes the punctuation marks in a string
    s = s.replace(',', '')
    s = s.replace('.','')
    s = s.replace('!','')
    s = s.replace('?','')
    s = s.replace(';','')
    s = s.replace('-',' ')
    s = s.replace(':',' ')
    s = s.replace('*', ' * ')
    s = s.replace("'", ' ')
    s = s.replace('<i>','')
    s = s.replace('</i>','')
    s = s.lower()
    return s

def check_vulgar(vulgars, s):
    s = remove_punc(s).split(' ')
    for i in range(len(vulgars)):
        if vulgars[i] in s:
            return True
    return False

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Media Player")
    app.setQuitOnLastWindowClosed(True)
    window = MainWindow()

    sys.exit(app.exec_())
