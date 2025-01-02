import multiprocessing
from scripts.server import run as start_server
from scripts.load_balancer import run as start_lb


if __name__ == "__main__":
    process1 = multiprocessing.Process(target=start_server)
    process2 = multiprocessing.Process(target=start_lb)

    process1.start()
    process2.start()

    try:
        process1.join()
        process2.join()
    except KeyboardInterrupt:
        print("Stopping...")
