import multiprocessing
import os
import threading
from scripts.server import Server, RequestHandler, ReverseProxyHandler
from utils.config_reader import Config
from utils.logger import common_logger


def load_config():
    config = Config.get_config()

    # server settings
    serving_directory = config.get("Server", "serving_directory")
    if "INSIDE_DOCKER" in os.environ:
        host = "0.0.0.0"
    else:
        host = config.get("Server", "host")
    starting_port = config.getint("Server", "starting_port")
    server_count = config.getint("Server", "server_count")
    os.chdir(serving_directory)

    # load balancer settings
    lb_port = config.getint("LB", "port")

    return (host, starting_port, server_count, lb_port)


def start_server(server_address, thread_name):
    with Server(server_address, RequestHandler) as server:
        print(f"Serving on {server_address}")
        common_logger.info(
            f"Server starting on {server_address} (Thread: {thread_name})"
        )
        server.serve_forever()


def start_server_on_threads(host, starting_port, server_count):
    for i in range(server_count):
        port = starting_port + i
        thread_name = f"T_{i+1}"
        thread = threading.Thread(
            target=start_server,
            args=((host, port), thread_name),
            name=thread_name,
        )
        thread.daemon = True
        thread.start()

    print("CTRL+C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Servers stopped.")


def start_load_balancer(host, starting_port, server_count, lb_port):
    with Server(
        (host, lb_port),
        lambda *args, **kwargs: ReverseProxyHandler(
            *args, custom_param=(host, starting_port, server_count), **kwargs
        ),
    ) as server:
        print(f"Load balancer running on port {lb_port}")
        print("CTRL+C to exit.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Load balancer stopped")


def run():
    config = load_config()

    p_load_balancer = multiprocessing.Process(
        target=start_load_balancer, args=config
    )
    p_server = multiprocessing.Process(
        target=start_server_on_threads, args=config[:3]
    )

    p_load_balancer.start()
    p_server.start()

    try:
        p_load_balancer.join()
        p_server.join()
    except KeyboardInterrupt:
        print("Stopping...")


if __name__ == "__main__":
    run()
