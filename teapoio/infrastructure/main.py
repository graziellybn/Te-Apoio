import os

from teapoio.infrastructure.flask_app import create_app


app = create_app()


if __name__ == "__main__":
	host = os.getenv("TEAPOIO_HOST", "127.0.0.1")
	port = int(os.getenv("TEAPOIO_PORT", "5000"))
	debug = os.getenv("TEAPOIO_DEBUG", "1") == "1"
	app.run(host=host, port=port, debug=debug)

# py -m teapoio.infrastructure.main