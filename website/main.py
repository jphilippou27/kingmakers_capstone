from flask import Flask 
from flask import g
from flask import jsonify
from flask import request
from flask import render_template 
from flask import url_for 

import backend

app = Flask(__name__)
DATABASE = ''

with app.app_context():
    db = backend.get_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return "pong"

@app.route("/donors", methods=["GET", "PUT"])
def donors():
    if request.method == "GET":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@app.route("/donors/<uuid:donor_id>", methods=["GET", "PUT"])
def donor(donor_id):
    if request.method == "GET":
        db = get_db()
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@app.route("/recipients", methods=["GET", "PUT"])
def recipients():
    if request.method == "GET":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@app.route("/recipients/<uuid:rep_id>", methods=["GET", "PUT"])
def recipient(rep_id):
    if request.method == "GET":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@app.route("/candidates/<cand_id>", methods=["GET", "PUT"])
def candidate(cand_id):
     if request.method == "GET":
         return jsonify(backend.get_candidate(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@app.route("/candidates", methods=["GET"])
def candidate_query():
     if request.method == "GET":
         fn = request.args.get("fn")
         ln = request.args.get("ln")
         return jsonify(backend.get_cands_by_name(ln, fn))
     else:
         return abort(401)


@app.route("/expenditures/<trans_id>", methods=["GET", "PUT"])
def expenditure(trans_id):
     if request.method == "GET":
         return jsonify(backend.get_expends(trans_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@app.route("/expenditures", methods=["GET"])
def expenditures():
     if request.method == "GET":
         max = request.args.get("max")
         min = request.args.get("min")
         return jsonify(backend.get_expends_by_amt(min, max))
     else:
         return abort(401)

@app.route("/filers/", methods=["GET"])
def expenditures_filer():
     if request.method == "GET":
         max = request.args.get("max")
         min = request.args.get("min")
         return jsonify(backend.get_expends_by_amt(min, max))
     else:
         return abort(401)

@app.route("/candidates/amt", methods=["GET"])
def candidates_amt():
     if request.method == "GET":
         return jsonify(backend.get_cands_by_amt())
     else:
         return abort(401)

@app.route("/sums", methods=["GET"])
def sums_all():
    sum_type = request.args.get("type")
    if sum_type == "cmte":
        get_all_sums_by_cmte()
    elif sum_type == "cand":
        get_all_sums_by_cand()
    elif sum_type == "industry":
        get_all_sums_by_industry()
    return None

@app.route("/spending", methods=["GET"])
def spending():
    sum_type = request.args.get("type")
    if sum_type == "cmte":
        return jsonify(backend.get_spending_by_cmte())
    elif sum_type == "cand":
        return jsonify(backend.get_spending_by_cand())
    elif sum_type == "industry":
        return jsonify(backend.get_spending_by_industry())
    return None

@app.route("/income", methods=["GET"])
def income():
    sum_type = request.args.get("type")
    if sum_type == "cmte":
        return jsonify(backend.get_income_by_cmte())
    elif sum_type == "cand":
        return jsonify(backend.get_income_by_cand())
    elif sum_type == "industry":
        return jsonify(backend.get_income_by_industry())
    return None

@app.route("/sankey", methods=["GET"])
def sankey():
    return jsonify(backend.get_simple_sankey_by_industry())
