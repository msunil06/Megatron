import multiprocessing
import sys
import time

# To run Megatron Core Application & GUI
def startMegatron():
    print("[Process 1] Megatron Desktop GUI process starting...")
    from main import start
    start()

# To run background Hotword detection ("Megatron", "Alexa")
def listenHotword():
    print("[Process 2] Megatron Hotword listener starting...")
    from engine.features import hotword
    hotword()

if __name__ == '__main__':
    # Ensure Windows multiprocessing compatibility
    multiprocessing.freeze_support()

    p1 = multiprocessing.Process(target=startMegatron, name="Megatron-GUI")
    p2 = multiprocessing.Process(target=listenHotword, name="Megatron-Hotword")

    p1.start()
    p2.start()

    # Wait for GUI process to finish
    p1.join()

    # Terminate background hotword listener on GUI exit
    if p2.is_alive():
        print("[Megatron] Terminating background processes...")
        p2.terminate()
        p2.join(timeout=2)

    print("[Megatron] System successfully shut down.")