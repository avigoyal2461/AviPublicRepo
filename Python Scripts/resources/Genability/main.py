import os


def clear_log():
    log_file_path = os.path.join(os.getcwd(), "logs")
    log_file_path = os.path.join(log_file_path, "customlogging.log")
    if os.path.exists(log_file_path):
        os.remove(log_file_path)


if __name__ == "__main__":
    clear_log()
    from genability_bot import genability_bot

    genability_bot()
