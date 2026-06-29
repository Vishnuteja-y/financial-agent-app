import os
import logging

from aiohttp import web
from botbuilder.integration.aiohttp.cloud_adapter import CloudAdapter
from botbuilder.integration.aiohttp import (
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication,
)
from botbuilder.schema import Activity

from config import Config
from bot import FinancialBot, answer_question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Config.validate()

ADAPTER = None
BOT = None


async def health(req: web.Request) -> web.Response:
    return web.json_response({"status": "healthy"})


async def home(req: web.Request) -> web.Response:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial AI RAG Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
            }
            textarea {
                width: 100%;
                height: 100px;
                font-size: 16px;
            }
            button {
                margin-top: 10px;
                padding: 10px 20px;
                font-size: 16px;
            }
            pre {
                background: #f4f4f4;
                padding: 15px;
                white-space: pre-wrap;
            }
            #route {
                background: #e8f4e8;
                padding: 10px;
                font-weight: bold;
                font-size: 15px;
                border-left: 4px solid #4CAF50;
            }
        </style>
    </head>
    <body>
        <h2>Financial AI RAG Demo</h2>
        <textarea id="question" placeholder="Ask a question about the financial data..."></textarea>
        <br />
        <button onclick="ask()">Ask</button>

        <h3>Answer</h3>
        <pre id="answer"></pre>

        <h3>Route Used</h3>
        <pre id="route"></pre>

        <h3>Sources</h3>
        <pre id="sources"></pre>

        <script>
            async function ask() {
                const question = document.getElementById("question").value;
                document.getElementById("answer").textContent = "Loading...";
                document.getElementById("route").textContent = "";
                document.getElementById("sources").textContent = "";

                const response = await fetch("/ask", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({question})
                });

                const data = await response.json();
                document.getElementById("answer").textContent = data.answer || data.error;
                document.getElementById("route").textContent = "Path: " + (data.route || "unknown");
                document.getElementById("sources").textContent = JSON.stringify(data.sources || [], null, 2);
            }
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


async def ask(req: web.Request) -> web.Response:
    try:
        body = await req.json()
        question = body.get("question")

        if not question:
            return web.json_response({"error": "Question is required"}, status=400)

        result = answer_question(question, session_id="web-session")
        return web.json_response(result)

    except Exception as e:
        logger.exception("Web ask endpoint failed")
        return web.json_response({"error": str(e)}, status=500)


async def messages(req: web.Request) -> web.Response:
    global ADAPTER, BOT

    try:
        if ADAPTER is None:
            logger.info("Initializing Bot Framework adapter")
            auth = ConfigurationBotFrameworkAuthentication(Config)
            ADAPTER = CloudAdapter(auth)

        if BOT is None:
            logger.info("Initializing FinancialBot")
            BOT = FinancialBot()

        body = await req.json()
        activity = Activity().from_dict(body)
        auth_header = req.headers.get("Authorization", "")

        await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        return web.Response(status=201)

    except Exception:
        logger.exception("Bot Framework message handling failed")
        return web.Response(status=500)


app = web.Application()
app.router.add_get("/", home)
app.router.add_post("/ask", ask)
app.router.add_get("/health", health)
app.router.add_post("/api/messages", messages)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    web.run_app(app, host="0.0.0.0", port=port)
