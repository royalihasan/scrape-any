from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from scraper_facade import ScraperFacade

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

@app.route('/scrape-any/api/start', methods=['GET'])
def start_scraping():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        facade = ScraperFacade()
        result = facade.start(url=url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def stream_logs():
    spider_url = request.args.get('url')
    if not spider_url:
        return jsonify({"error": "URL parameter is required"}), 400

    def generate():
        facade = ScraperFacade()
        logs_generator = facade.get_logs(spider_url)
        try:
            for log_line in logs_generator:
                yield f"data: {log_line}\n\n"
        except GeneratorExit:
            print("Client disconnected")

    return Response(generate(), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)
