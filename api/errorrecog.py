import traceback
import datetime

def log_error(error):
    error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = f"{error_time} - {error}\n{traceback.format_exc()}\n"

    with open('logs/error_log.txt', 'a') as f:
        f.write(error_message)
