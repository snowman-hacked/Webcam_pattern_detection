# 웹캠을 활용한 얼굴 인식

[webcam_pattern_](https://doc.qt.io/qtforpython-6/examples/example_external_opencv.html#example-external-OpenCV)

sample 코드를 받아와 2가지 기능 추가
- 얼굴 감지 시 자동 스크린샷(같은 객체가 20초 유지되면 20초 간격으로 재 스크린샷)
- 감지된 객체 수를 화면에 표시하는 기능

## 실행 예시 이미지
![스크린샷 2025-03-19 161527](https://github.com/user-attachments/assets/3e3e2f01-129a-4bbf-b70c-d3f8c8ffce62)
![스크린샷 2025-03-19 161537](https://github.com/user-attachments/assets/17950d61-c042-4907-8d07-0f3c48dc65e6)

## 트러블슈팅
- exe파일 배포시 haarcascade 파일이 인식되지 않아 제대로 동작하지 않는 에러
- 필요한 xml파일들을 opencv 설치경로에서 복사하여 wpd_add2와 동일 디렉터리에 (haarcasacde라는 디렉터리를 생성) 위치 시킨 후에
```
def get_haarcascade_path():
    # PyInstaller 실행 환경에서도 haarcascade 경로를 찾을 수 있도록 설정
    if hasattr(sys, '_MEIPASS'):  # PyInstaller 실행 시
        base_path = os.path.join(sys._MEIPASS, "haarcascade")
    elif os.path.exists(cv2.data.haarcascades):  # 일반 Python 실행 환경
        base_path = cv2.data.haarcascades
    else:
        base_path = os.path.join(os.getcwd(), "haarcascade")  # 실행 파일과 같은 폴더

    return base_path
```
- 해당 함수로 경로 찾을 수 있도록 설정 해줬다.
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
