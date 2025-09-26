from .app.app import main as app_main
from .configuration import APP_NAME


def main():
    print(f"Hello from {APP_NAME.capitalize()}!")
    app_main()


if __name__ == "__main__":
    main()
