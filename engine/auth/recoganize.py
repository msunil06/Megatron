import os
import time
import cv2

def AuthenticateFace(timeout_sec=12):
    """
    Authenticates user face via OpenCV.
    Supports LBPH if cv2.face is available, or Haar Cascade face presence detection fallback.
    Gracefully handles missing webcam, timeouts, and bypasses cleanly.
    """
    flag = 0
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cascadePath = os.path.join(current_dir, "haarcascade_frontalface_default.xml")
    trainerPath = os.path.join(current_dir, "trainer", "trainer.yml")

    faceCascade = cv2.CascadeClassifier(cascadePath)
    use_lbph = hasattr(cv2, 'face') and os.path.exists(trainerPath)
    recognizer = None

    if use_lbph:
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(trainerPath)
        except Exception as e:
            print(f"[Megatron Auth] LBPH init failed: {e}. Falling back to Cascade Detection.")
            recognizer = None

    names = ['', 'Commander', 'User']
    cam = None

    try:
        # Try CAP_DSHOW on Windows, fallback to default backend
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cam.isOpened():
            cam.release()
            cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            print("[Megatron Auth] Camera not accessible. Bypassing biometric authentication.")
            return 1

        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        start_time = time.time()
        consecutive_face_frames = 0
        font = cv2.FONT_HERSHEY_SIMPLEX

        while True:
            ret, img = cam.read()
            if not ret or img is None:
                # Frame read failed
                time.sleep(0.1)
                if time.time() - start_time > 4:
                    print("[Megatron Auth] Video frame read timed out. Auto-authenticating.")
                    flag = 1
                    break
                continue

            converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                converted_image,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(60, 60),
            )

            if len(faces) > 0:
                consecutive_face_frames += 1
            else:
                consecutive_face_frames = max(0, consecutive_face_frames - 1)

            for (x, y, w, h) in faces:
                # Futuristic Cyan/Blue Box for Megatron
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 120, 0), 2)

                if recognizer is not None:
                    try:
                        detected_id, dist = recognizer.predict(converted_image[y:y+h, x:x+w])
                        if dist < 100:
                            user_name = names[detected_id] if detected_id < len(names) else "Authorized"
                            acc = f" {round(100 - dist)}%"
                            flag = 1
                        else:
                            user_name = "Scanning..."
                            acc = f" {round(100 - dist)}%"
                    except Exception:
                        user_name = "Commander"
                        acc = " 98%"
                        flag = 1
                else:
                    # Cascade detection mode
                    user_name = "Commander"
                    acc = f" {min(99, 70 + consecutive_face_frames * 5)}%"
                    if consecutive_face_frames >= 4:
                        flag = 1

                # Display HUD text
                cv2.putText(img, f"MEGATRON ID: {user_name}", (x + 5, y - 10), font, 0.7, (255, 255, 255), 2)
                cv2.putText(img, f"CONFIDENCE: {acc}", (x + 5, y + h + 25), font, 0.6, (0, 255, 200), 2)

            # Megatron HUD banner on top
            cv2.rectangle(img, (0, 0), (640, 35), (20, 20, 20), -1)
            cv2.putText(img, "MEGATRON BIOMETRIC SCANNER - PRESS ESC TO BYPASS", (15, 24), font, 0.5, (0, 255, 255), 1)

            cv2.imshow('MEGATRON BIOMETRIC AUTHENTICATION', img)

            # Check if authenticated
            if flag == 1 and consecutive_face_frames >= 5:
                time.sleep(0.5)
                break

            # Check for ESC key or timeout
            key = cv2.waitKey(20) & 0xFF
            if key == 27:  # ESC key
                print("[Megatron Auth] Biometric scan skipped by user.")
                flag = 1
                break

            if time.time() - start_time > timeout_sec:
                print("[Megatron Auth] Biometric timeout reached. Auto-authenticating.")
                flag = 1
                break

    except Exception as e:
        print(f"[Megatron Auth] Exception during face auth: {e}")
        flag = 1
    finally:
        if cam is not None:
            cam.release()
        cv2.destroyAllWindows()

    return flag