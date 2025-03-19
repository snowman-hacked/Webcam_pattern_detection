# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# 2가지 기능 추가 :
# 얼굴 감지 시 20초마다 자동 스크린샷 기능
# 감지된 객체 개수 표시 기능

from __future__ import annotations

import os
import sys
import time
import cv2
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)
from datetime import datetime  # 스크린샷 저장용

""" This example uses the video from a webcam to apply pattern
detection from the OpenCV module. e.g.: face, eyes, body, etc."""


def get_haarcascade_path():
    """ PyInstaller 실행 환경에서도 haarcascade 경로를 찾을 수 있도록 설정 """
    if hasattr(sys, '_MEIPASS'):  # PyInstaller 실행 시
        base_path = os.path.join(sys._MEIPASS, "haarcascade")
    elif os.path.exists(cv2.data.haarcascades):  # 일반 Python 실행 환경
        base_path = cv2.data.haarcascades
    else:
        base_path = os.path.join(os.getcwd(), "haarcascade")  # 실행 파일과 같은 폴더

    return base_path


class Thread(QThread):
    updateFrame = Signal(QImage, int)  # 탐지된 개수(int) 추가

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.trained_file = None
        self.status = True
        self.cap = None  # None으로 초기화
        self.last_screenshot_time = None  # 마지막 스크린샷 시간 초기화
        self.object_detected = False  # 객체 탐지 여부

        # 스크린샷 디렉터리 지정
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def set_file(self, fname):
        self.trained_file = os.path.join(get_haarcascade_path(), fname)

    def run(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ 카메라를 열 수 없습니다.")
            return

        cascade = cv2.CascadeClassifier(self.trained_file)
        if cascade.empty():
            print("❌ Haarcascade XML 파일을 로드할 수 없습니다.")
            return

        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Reading frame in gray scale to process the pattern
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detections = cascade.detectMultiScale(gray_frame, scaleFactor=1.1,
                                                  minNeighbors=5, minSize=(30, 30))

            # 탐지된 객체 개수가 1 이상이면 20초마다 스크린샷 저장하기
            if len(detections) > 0:
                current_time = time.time()

                # 처음 감지되었을 때 즉시 저장
                if not self.object_detected:
                    self.save_screenshot(frame)
                    self.last_screenshot_time = current_time  # 시간 저장
                    self.object_detected = True  # 객체가 감지되었음을 표시

                # 동일 객체가 20초 동안 유지되었을 때 한 번 더 저장
                elif self.last_screenshot_time and (current_time - self.last_screenshot_time >= 20):
                    self.save_screenshot(frame)
                    self.last_screenshot_time = current_time  # 마지막 저장 시간 업데이트

            else:
                # 객체가 감지되지 않으면 리셋
                self.object_detected = False
                self.last_screenshot_time = None

            # 탐지된 객체를 표시하는 사각형 그리기
            for (x, y, w, h) in detections:
                pos_ori = (x, y)
                pos_end = (x + w, y + h)
                color = (0, 255, 0)
                cv2.rectangle(frame, pos_ori, pos_end, color, 2)

            # Reading the image in RGB to display it
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Creating and scaling QImage
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

            # Emit signal with detected count
            self.updateFrame.emit(scaled_img, len(detections))  # 탐지 개수 추가

    def save_screenshot(self, frame):
        # 현재 프레임을 스크린 샷으로 저장
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.screenshot_dir, f'screenshot_{timestamp}.png')
        cv2.imwrite(filename, frame)  # OpenCV로 저장
        print(f'✅ 스크린샷 저장 완료: {filename}')


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Patterns detection")
        self.setGeometry(0, 0, 800, 500)

        # Create a label for the display camera
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)

        # 탐지 개수 출력용 QLabel 추가
        self.count_label = QLabel("Detected: 0", self)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Thread in charge of updating the image
        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updateFrame.connect(self.setImage)  # 탐지 개수를 함께 받도록 수정

        # Model group
        self.group_model = QGroupBox("Trained model")
        self.group_model.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        model_layout = QHBoxLayout()

        self.combobox = QComboBox()
        self.populate_models()

        model_layout.addWidget(QLabel("File:"), 10)
        model_layout.addWidget(self.combobox, 90)
        self.group_model.setLayout(model_layout)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop/Close")
        self.button1.clicked.connect(self.start)
        self.button2.clicked.connect(self.kill_thread)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)

        right_layout = QHBoxLayout()
        right_layout.addWidget(self.group_model, 1)
        right_layout.addLayout(buttons_layout, 1)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.count_label)  # 탐지 개수 QLabel 추가
        layout.addLayout(right_layout)

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def populate_models(self):
        cascade_path = get_haarcascade_path()
        if os.path.exists(cascade_path):
            for xml_file in os.listdir(cascade_path):
                if xml_file.endswith(".xml"):
                    self.combobox.addItem(xml_file)
        else:
            print(f"❌ Haarcascade 모델 파일을 찾을 수 없습니다: {cascade_path}")

    @Slot()
    def set_model(self, text):
        self.th.set_file(text)

    @Slot()
    def start(self):
        selected_model = self.combobox.currentText()
        if not selected_model:
            print("❌ 학습된 모델을 선택하세요.")
            return
        self.th.set_file(selected_model)
        self.th.start()

    @Slot()
    def kill_thread(self):
        self.th.status = False
        self.th.quit()
        self.th.wait()

    @Slot(QImage, int)
    def setImage(self, image, count):
        self.label.setPixmap(QPixmap.fromImage(image))
        self.count_label.setText(f"Detected: {count}")

if __name__ == "__main__":
    app = QApplication([])
    w = Window()
    w.show()
    app.exec()
