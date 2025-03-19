# 웹캠을 활용한 얼굴 인식

[webcam_pattern_](https://doc.qt.io/qtforpython-6/examples/example_external_opencv.html#example-external-OpenCV)

sample 코드를 받아와 2가지 기능 추가
- 얼굴 감지 시 자동 스크린샷(같은 객체가 20초 유지되면 20초 간격으로 재 스크린샷)
- 감지된 객체 수를 화면에 표시하느 기능

## 트러블슈팅
- exe파일 배포시 haarcascade 파일이 인식되지 않아 제대로 동작하지 않는 에러
- haarcascade를 파이썬 설치경로에서 복사하여 같은 디렉터리에 위치 시킨 후
- pyinstaller --onefile --noconsole --add-data "haarcascade;haarcascade" wpd_add2.py
- 해당 명령어로 xml파일을 포함시켜 패키징하여 배포 성공
- 예상되는 폴더 경로
```
  C:\Users\USER\Downloads\opencv\
  ├── wpd_add2.py
  ├── haarcascade\    > 이 폴더가 반드시 있어야 함
      ├── haarcascade_frontalface_default.xml
      ├── haarcascade_eye.xml
```
