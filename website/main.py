from flask import Flask 
from flask import g
from flask import jsonify
from flask import request
from flask import render_template 
from flask import url_for 

import backend

application = Flask(__name__)
DATABASE = ''

with application.app_context():
    db = backend.get_db()

@application.route("/")
def home():
    return render_template("home.html")

@application.route("/ping")
def ping():
    return "pong"

@application.route("/donors", methods=["GET", "PUT"])
def donors():
    if request.method == "GET":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@application.route("/donors/<uuid:donor_id>", methods=["GET", "PUT"])
def donor(donor_id):
    if request.method == "GET":
        db = get_db()
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@application.route("/recipients", methods=["GET", "PUT"])
def recipients():
    if request.method == "GET":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@application.route("/recipients/<uuid:rep_id>", methods=["GET", "PUT"])
def recipient(rep_id):
    if request.method == "GET":
        pass
    elif request.method == "PUT":
        pass
    elif request.method == "OPTIONS":
        pass
    else:
        return abort(401)

@application.route("/candidates/<cand_id>", methods=["GET", "PUT"])
def candidate(cand_id):
     if request.method == "GET":
         return jsonify(backend.get_candidate(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/candidates", methods=["GET"])
def candidate_query():
     if request.method == "GET":
         fn = request.args.get("fn")
         ln = request.args.get("ln")
         return jsonify(backend.get_cands_by_name(ln, fn))
     else:
         return abort(401)


@application.route("/expenditures/<trans_id>", methods=["GET", "PUT"])
def expenditure(trans_id):
     if request.method == "GET":
         return jsonify(backend.get_expends(trans_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/expenditures", methods=["GET"])
def expenditures():
     if request.method == "GET":
         max = request.args.get("max")
         min = request.args.get("min")
         return jsonify(backend.get_expends_by_amt(min, max))
     else:
         return abort(401)

@application.route("/filers/", methods=["GET"])
def expenditures_filer():
     if request.method == "GET":
         max = request.args.get("max")
         min = request.args.get("min")
         return jsonify(backend.get_expends_by_amt(min, max))
     else:
         return abort(401)

@application.route("/candidates/amt", methods=["GET"])
def candidates_amt():
     if request.method == "GET":
         return jsonify(backend.get_cands_by_amt())
     else:
         return abort(401)

@application.route("/sums", methods=["GET"])
def sums_all():
    sum_type = request.args.get("type")
    if sum_type == "cmte":
        get_all_sums_by_cmte()
    elif sum_type == "cand":
        get_all_sums_by_cand()
    elif sum_type == "industry":
        get_all_sums_by_industry()
    return None

@application.route("/spending", methods=["GET"])
def spending():
    sum_type = request.args.get("type")
    if sum_type == "cmte":
        return jsonify(backend.get_spending_by_cmte())
    elif sum_type == "cand":
        return jsonify(backend.get_spending_by_cand())
    elif sum_type == "industry":
        return jsonify(backend.get_spending_by_industry())
    return None

@application.route("/income", methods=["GET"])
def income():
    sum_type = request.args.get("type")
    if sum_type == "cmte":
        return jsonify(backend.get_income_by_cmte())
    elif sum_type == "cand":
        return jsonify(backend.get_income_by_cand())
    elif sum_type == "industry":
        return jsonify(backend.get_income_by_industry())
    return None

@application.route("/sankey", methods=["GET"])
def sankey():
    return render_template("sankey.html")

@app.route("/sankeydata", methods=["GET"])
def sankeydata():
    return jsonify(backend.get_simple_sankey_by_industry())


if __name__ == "__main__":
	application.run(host="0.0.0.0")
