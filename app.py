from functools import partial

import hivemind
from flask import Flask, jsonify, request
from flask_cors import CORS
from hivemind.proto import crypto_pb2
from hivemind.utils.crypto import Ed25519PrivateKey
from hivemind.utils.auth import POSAuthorizer, POSAuthorizerLive
from cryptography.hazmat.primitives.asymmetric import ed25519
from substrateinterface import SubstrateInterface

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
    authorizer=POSAuthorizer(private_key)
    # authorizer=POSAuthorizerLive(private_key, 1, SubstrateInterface(url='wss://rpc.hypertensor.org:443'))
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