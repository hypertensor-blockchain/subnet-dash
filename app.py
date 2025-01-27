from functools import partial

import hivemind
from flask import Flask, jsonify, request, send_file, render_template_string
from flask_cors import CORS
from hivemind.proto import crypto_pb2
from hivemind.utils.crypto import Ed25519PrivateKey
from hivemind.utils.auth import POSAuthorizerLive
from cryptography.hazmat.primitives.asymmetric import ed25519
from substrateinterface import SubstrateInterface
from pyppeteer import launch
from io import BytesIO
import asyncio
from asgiref.wsgi import WsgiToAsgi

# from flask_socketio import SocketIO, send, emit

import config
from p2p_utils import check_reachability
from state_updater import StateUpdaterThread

logger = hivemind.get_logger(__name__)

identity_path = "private_key.key"
with open(f"{identity_path}", "rb") as f:
    data = f.read()
    key_data = crypto_pb2.PrivateKey.FromString(data).data
    raw_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(key_data[:32])
    private_key = Ed25519PrivateKey(private_key=raw_private_key)

logger.info("Connecting to DHT")
dht = hivemind.DHT(
    initial_peers=config.INITIAL_PEERS, 
    client_mode=True, 
    num_workers=32, 
    start=True,
    # authorizer=POSAuthorizer(private_key)
    authorizer=POSAuthorizerLive(private_key, 1, SubstrateInterface(url='wss://rpc.hypertensor.org:443'))
)

logger.info("Starting Flask app")
app = Flask(__name__)
CORS(app)

logger.info("Starting updater")
updater = StateUpdaterThread(dht, app, daemon=True)
updater.start()
updater.ready.wait()

app.config['SECRET_KEY'] = 'secret!'

@app.route("/")
def main_page():
    return updater.state_html

@app.route("/api/v1/state")
def api_v1_state():
    return app.response_class(response=updater.state_json, status=200, mimetype="application/json")

@app.route("/api/v1/is_reachable/<peer_id>")
def api_v1_is_reachable(peer_id):
    peer_id = hivemind.PeerID.from_base58(peer_id)
    rpc_info = dht.run_coroutine(partial(check_reachability, peer_id, use_cache=False))
    return jsonify(
        success=rpc_info["ok"],
        message=rpc_info.get("error"),
        your_ip=request.remote_addr,
    )

@app.route("/metrics")
@app.route("/api/prometheus")
def metrics():
    return app.response_class(response=updater.prometheus_metrics, status=200, mimetype="text/plain")

@app.route('/preview.png')
async def generate_preview():
    model = {
        "name":"Orenguteng/Llama-3.1-8B-Lexi-Uncensored-V2",
        "short_name":"Llama-3.1-8B-Lexi-Uncensored-V2",
        "state":"healthy",
        "server_rows": [
            {
                "short_peer_id":"...wLKfLa",
                "peer_id":"12D3KooWGmoSHnvRsktrGzNTfCEwzY2TKAYPRtdaA9AwxHwLKfLa",
                "state":"online",
                "span": {
                    "peer_id": "12D3KooWGmoSHnvRsktrGzNTfCEwzY2TKAYPRtdaA9AwxHwLKfLa",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
            {
                "short_peer_id":"...eM9vtZ",
                "peer_id":"12D3KooWJ18uU5QcZ6orkFg6ARRMH2RjghuGN7gHnWhbuqeM9vtZ",
                "state":"online",
                "span": {
                    "peer_id": "12D3KooWJ18uU5QcZ6orkFg6ARRMH2RjghuGN7gHnWhbuqeM9vtZ",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
            {
                "short_peer_id":"...Vk9tmr",
                "peer_id":"12D3KooWJLtnzinNqvzCwYaNJZs2X75hEdvj5H2wX5PgvPVk9tmr",
                "state":"online",
                "span": {
                    "peer_id": "12D3KooWJLtnzinNqvzCwYaNJZs2X75hEdvj5H2wX5PgvPVk9tmr",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
            {
                "short_peer_id":"...55Er7p",
                "peer_id":"12D3KooWJtcAh8wjssYAmw1r1hn67oGXVA8wYCMrKvf8Dk55Er7p",
                "state":"online",
                "span": {
                    "peer_id": "12D3KooWJtcAh8wjssYAmw1r1hn67oGXVA8wYCMrKvf8Dk55Er7p",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
            {
                "short_peer_id":"...5buezF",
                "peer_id":"12D3KooWNTY4D5narNZpxxgSCz2NdkwisZFcWDsRruCGAZ5buezF",
                "state":"online",
                "span": {
                    "peer_id": "12D3KooWNTY4D5narNZpxxgSCz2NdkwisZFcWDsRruCGAZ5buezF",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
            {
                "short_peer_id":"...HqM6ux",
                "peer_id":"12D3KooWNzm66Qkd7tM3kqzJ3aVw5CAxQHEA14dVFJjcY9HqM6ux",
                "state":"online",
                "span": { 
                    "peer_id":"12D3KooWNzm66Qkd7tM3kqzJ3aVw5CAxQHEA14dVFJjcY9HqM6ux",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
            {
                "short_peer_id":"...535oaY",
                "peer_id":"12D3KooWSsz2RFzy6MvP62aQTb7NnbFdgX6FnaNZ5BQ5sZ535oaY",
                "state":"online",
                "span": {
                    "peer_id": "12D3KooWSsz2RFzy6MvP62aQTb7NnbFdgX6FnaNZ5BQ5sZ535oaY",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                },
            },
            {
                "short_peer_id":"...CDLpES",
                "peer_id":"12D3KooWT1XwWtkzeNsBbTzBEQJrmLjHPzpqy4B6HqwGwLCDLpES",
                "state":"online",
                "span": { 
                    "peer_id": "12D3KooWT1XwWtkzeNsBbTzBEQJrmLjHPzpqy4B6HqwGwLCDLpES",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
            {
                "short_peer_id":"...Cw11FV",
                "peer_id":"12D3KooWT3FtG37cuPiMkAKzg3FmsFMASZer2ZVHJ7Ly7gCw11FV",
                "state":"online",
                "span": {
                    "peer_id": "12D3KooWT3FtG37cuPiMkAKzg3FmsFMASZer2ZVHJ7Ly7gCw11FV",
                    "start": 0,
                    "end": 32,
                    "server_info": 2,
                }
            },
        ],
        "num_blocks":32,
        "repository":"https://huggingface.co/Orenguteng/Llama-3.1-8B-Lexi-Uncensored-V2",
        "dht_prefix":"Llama-3-1-8B-Lexi-Uncensored-V2-hf",
        "official":True,
        "limited":False
    }

    html_content = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100..900;1,100..900&display=swap');

                    #preview {
                        width: 800px;
                        height: 418px;
                        padding: 5px;
                        border-radius: 10px;
                    }

                    body {
                        font-family: 'Roboto', sans-serif;
                        font-size: 9pt;
                        padding: 20px;
                    }

                    section {
                        padding: 0 5px 0 5px;
                    }

                    header {
                        text-align: center;
                    }

                    section {
                        margin: 15px 0;
                    }

                    section p {
                        margin: 7px 0;
                        font-weight: bold;
                    }

                    table {
                        border-spacing: 1px;
                        margin-top: 15px;
                        margin-bottom: 10px;
                        white-space: nowrap;
                    }

                    thead td {
                        padding: 10px;
                        padding-left: 10px;
                        padding-right: 10px;
                        text-align: center;
                    }

                    thead th {
                        padding: 10px;
                        padding-left: 10px;
                        padding-right: 10px;
                        text-align: center;
                        font-weight: normal;
                        font-family: 'Roboto', sans-serif;
                    }

                    tbody, .bootstrap-map {
                        font-family: 'Courier', monospace;
                        font-size: 7.75pt;
                    }

                    .non-server-layer {
                        padding-left: 10px;
                        padding-right: 10px;
                        text-align: left;
                    }

                    thead th:first-child {
                        border-radius: 0.28rem 0 0 0.28rem;
                    }

                    table th:last-child {
                        border-radius: 0 0.28rem 0.28rem 0;
                    }

                    .bm-test-header-2 {
                        text-align: center;
                        font-family: 'Roboto', sans-serif;
                        font-size: 14px;
                    }

                    .bm-test-2 {
                        height: 17.4px !important;
                        width: 17.4px !important;
                        min-height: 17.4px !important;
                        min-width: 17.4px !important;
                        max-height: 17.4px !important;
                        max-width: 17.4px !important;
                        border-radius: 0.015625rem;
                    }

                    tbody td {
                        text-align: center;
                    }

                    .bg-neutral-50 {
                        background-color: rgb(250, 250, 250, 1.0);
                    }

                    .bg-neutral-900 {
                        background-color: rgb(23, 23, 23, 1.0);
                    }

                    .flex {
                        display: flex;
                    }

                    .flex-row {
                        flex-direction: row;
                    }

                    .items-center {
                        align-items: center;
                    }

                    .gap-2\.5 {
                        gap: 0.625rem;
                    }

                    .py-0\.5 {
                        padding-top: 0.125rem;
                        padding-bottom: 0.125rem;
                    }

                    .px-2\.5 {
                        padding-left: 0.625rem;
                        padding-right: 0.625rem;
                    }

                    .font-medium {
                        font-weight: 500;
                    }

                    .text-xs {
                        font-size: 0.75rem;
                        line-height: 1rem;
                    }

                    .rounded-lg {
                        border-radius: 0.5rem;
                    }

                    .relative {
                        position: relative;
                    }

                    .w-2 {
                        width: 0.5rem;
                    }

                    .h-2 {
                        height: 0.5rem;
                    }

                    .bg-emerald-200 {
                        background-color: rgb(167, 243, 208, 1.0);
                    }

                    .text-neutral-100 {
                        color: rgb(245, 245, 245, 1.0);
                    }

                    .text-neutral-950 {
                        color: rgb(10, 10, 10, 1.0);
                    }

                    .bg-neutral-950 {
                        background-color: rgb(10, 10, 10, 1.0);
                    }

                    .text-center {
                        text-align: center;
                    }

                    .text-8 {
                        font-size: 8pt;
                    }

                    .text-neutral-50 {
                        color: rgb(250, 250, 250, 1.0);
                    }

                    .opacity-75 {
                        opacity: 0.75;
                    }

                    .bg-green-400 {
                        --tw-bg-opacity: 1;
                        background-color: rgb(74 222 128 / var(--tw-bg-opacity, 1));
                    }

                    .rounded-full {
                        border-radius: 9999px;
                    }

                    .w-full {
                        width: 100%;
                    }

                    .w-full {
                        max-width: 100%;
                    }

                    .h-full {
                        height: 100%;
                    }

                    .inline-flex {
                        display: inline-flex;
                    }

                    .absolute {
                        position: absolute;
                    }
                    .me-2 {
                        margin-inline-end: 0.5rem;
                    }
                    .text-neutral-800 {
                        --tw-text-opacity: 1;
                        color: rgb(38 38 38 / var(--tw-text-opacity, 1));
                    }
                    .bg-neutral-100 {
                        --tw-bg-opacity: 1;
                        background-color: rgb(245 245 245 / var(--tw-bg-opacity, 1));
                    }
                    .dsn-1 {
                        margin: 15px 0;
                    }

                    .mx-auto { 
                        margin-right: auto; 
                        margin-left: auto; 
                    }
                </style>
            </head>
            <body>
                <div id="preview" class=" bg-neutral-950 text-neutral-100 flex justify-center items-center mx-auto">
                    <div class="mx-auto">
                        <div class="text-neutral-50 flex flex-row gap-2.5 items-center">
                            <span class="bg-neutral-50 text-neutral-950 text-xs font-medium px-2.5 py-0.5 rounded-lg">Subnet</span>
                            <span>{{ model.name }}</span>
                            <span class="relative flex h-2 w-2">
                                <span class="absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            </span>    
                        </div>
                        <table class="servers text-8">
                            <thead class="bg-neutral-900 text-neutral-100">
                                <tr class="bg-neutral-900">
                                    <th class="bm-test-header-2">Validators</th>
                                    <th class="bm-test-header-2" colspan="{{ model.num_blocks + 1 }}">Served blocks</th>
                                </tr>
                                <tbody class="text-neutral-100">
                                    {% for row in model.server_rows %}
                                        <tr>
                                            <td class="non-server-layer">
                                                <span class="peer-id">
                                                    {{ row.short_peer_id }}
                                                </span>
                                            </td>
                                            <span>
                                                {% for _ in range(row.span.start, row.span.end) %}
                                                    <td class="bm-td-test-2 text-center">
                                                        <div class="bm-test-2 bg-emerald-200 text-center">
                                                        </div>
                                                    </td>
                                                {% endfor %}
                                            </span>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </thead>
                        </table>

                    </div>
                </div>
            </body>
        </html>
    """

    # Render the template with the token data
    rendered_html = render_template_string(html_content, model=model)

    # Launch a headless browser
    browser = await launch(headless=True)
    page = await browser.newPage()

    # await page.setViewport({"width": 800, "height": 418, "deviceScaleFactor": 2})
    await page.setViewport({"width": 1200, "height": 628, "deviceScaleFactor": 2})

    # Set the rendered HTML content
    await page.setContent(rendered_html)

    # Take a screenshot of the specific div
    element = await page.querySelector('#preview')
    screenshot = await element.screenshot(type="png")

    # Close the browser
    await browser.close()

    # Return the image as a response
    return send_file(
        BytesIO(screenshot),
        mimetype='image/png',
        as_attachment=False,
        download_name=f"model_servers_preview.png"
    )

app = WsgiToAsgi(app)
