import threading
import os
import time


def run():
    os.system("streamlit run Stream_lit_Chat.py --server.headless true")

thread = threading.Thread(target=run)
thread.start()
time.sleep(5)
print("Streamlit app is live at:","http://localhost:8501")
