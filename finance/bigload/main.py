from flask import Flask,jsonify
from utils.LoadData import profit_loss_process

app = Flask(__name__)


@app.route("/load-profit-loss", methods=["GET"])
def load_profit_loss():
    try:
        profit_loss_process()
        return jsonify({
            "Status":200,
            "Message":"Success"})
    except:
        return jsonify({
            "Status":404,
            "Message":"Check API Code"})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=3000,
            debug=True)