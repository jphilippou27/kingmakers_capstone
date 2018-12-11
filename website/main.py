from flask import Flask
from flask import g
from flask import jsonify
from flask import request
from flask import render_template
from flask import url_for
import sys

#sys.path.insert(0, 'dash')
#import index2
import backend

application = Flask(__name__)
#db = None

@application.route("/")
def home():
    return render_template("home.html")

@application.route("/ping")
def ping():
    return "pong"

@application.route("/api/candidates/<cand_id>", methods=["GET", "PUT"])
def candidate(cand_id):
     if request.method == "GET":
         return jsonify(backend.get_candidate(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/api/candidates/<cand_id>/sk/type")
def get_candidate_tree(cand_id):
    return jsonify(backend.get_candidate_tree(cand_id))

@application.route("/api/candidates/<cand_id>/sk/industry")
def get_candidate_industry_tree(cand_id):
    return jsonify(backend.get_candidate_industry_tree(cand_id))

@application.route("/api/candidates/<cand_id>/wf")
def get_waterfall(cand_id):
    return jsonify(backend.get_waterfall_data(cand_id))

@application.route("/api/candidates/<cand_id>/ts/for", methods=["GET", "PUT"])
def candidate_ts_for(cand_id):
     if request.method == "GET":
         return jsonify(backend.cmte_timeseries_for(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/api/candidates/<cand_id>/ts/against", methods=["GET", "PUT"])
def candidate_ts_against(cand_id):
     if request.method == "GET":
         return jsonify(backend.cmte_timeseries_against(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/api/candidates/<cand_id>/interests/for", methods=["GET", "PUT"])
def candidate_interest_for(cand_id):
     if request.method == "GET":
         return jsonify(backend.interest_spending_for(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/api/candidates/<cand_id>/interests/against", methods=["GET", "PUT"])
def candidate_interest_against(cand_id):
     if request.method == "GET":
         return jsonify(backend.interest_spending_against(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/api/candidates/<cand_id>/indiv/for", methods=["GET", "PUT"])
def candidate_individual_support(cand_id):
     if request.method == "GET":
         return jsonify(backend.get_individual_support_direct(cand_id))
     elif request.method == "PUT":
         pass
     elif request.method == "OPTIONS":
         pass
     else:
         return abort(401)

@application.route("/api/candidates", methods=["GET"])
def all_cands():
    return jsonify(backend.get_all_cands())

@application.route("/candidates/<cand_id>", methods=["GET"])
def candidate_view(cand_id):
    ici = {"I": "Incumbent", "C": "Challenger", "O": "Open Seat"}
    office = {"S": "Senate", "H": "House", "P": "President"}
    if request.method == "GET":
        if cand_id is None:
            render_template("search_cand.html")
        cand_data = backend.get_candidate(cand_id)
        return render_template("candidate.html", 
                cand_id=cand_id, 
                cand_name=cand_data["cand_name"],
                cand_office=office[cand_data["cand_office"]],
                cand_district=cand_data["cand_office_district"],
                cand_state=cand_data["cand_st"],
                cand_party=cand_data["cand_pty_affiliation"],
                cand_status=ici[cand_data["cand_office_ici"]]
                )
    else:
        return abort(401)

@application.route("/candidates", methods=["GET"])
def candidate_query():
    if request.method == "GET":
        return render_template("candlookup.html")
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

@application.route("/industries", methods=["GET"])
def industries():
    return render_template("industries.html")

@application.route("/api/industries", methods=["GET"])
def get_industry_data():
    industryname = request.args.get("industry")
    partyname = request.args.get("party")
    if industryname is not None and partyname is not None:
        return jsonify(backend.get_industry_partycands(industryname, partyname))
    elif industryname is not None and partyname is None:
        return jsonify(backend.get_industry_cands(industryname))
    else:
        return jsonify(backend.get_industries_by_party())

    return jsonify(backend.get_industries_by_party())
@application.route("/sankeydata", methods=["GET"])
def sankeydata():
    return jsonify(backend.get_simple_sankey_by_industry())

@application.route("/network", methods=["GET"])
def network():
    return render_template("network.html")

@application.route("/networkdata/<cand_name>", methods=["GET", "POST"])
def networkdata(cand_name):
    if type(cand_name) is None or cand_name == "":
        text = "Sean Patrick Maloney (D)"
    if request.method == "POST":
        text = request.form['search2']
        print(text)
    else:
        text = str(cand_name)
    return (backend.get_network_by_industry(text))

@application.route("/networkIndividData/<cand_name>", methods=["GET", "POST"])
def networkIndivdData(cand_name):
    if type(cand_name) is None or cand_name == "":
        text = "Sean Patrick Maloney (D)"
    if request.method == "POST":
        text = request.form['search4']
        print(text)
    else:
        text = str(cand_name)
    return (backend.get_network_individ(text))

@application.route("/networkCommitteeData/<cand_name>", methods=["GET", "POST"])
def networkCommitteeData(cand_name):
    if type(cand_name) is None or cand_name == "":
        text = "Chris Collins (R)"
    if request.method == "POST":
        text = request.form['search6']
        print(text)
    else:
        text = str(cand_name)
    return (backend.get_network_committee(text))

@application.route("/networkNodeList", methods=["GET"])
def networkNodedata():
    return (backend.get_network_node_list())

@application.route("/tableau")
def tableau():
    return render_template("tableau.html")

@application.route("/api/superpacs/sankey")
def superpacs_sk_data():
    return jsonify(backend.get_superpac_sankey()) 

@application.route("/superpacs/sankey")
def superpacs_sk_view():
    return render_template("superpacs_sk.html") 


if __name__ == "__main__":
    with application.app_context():
        backend.get_pg()
    if len(sys.argv) > 1:
        application.run(host="0.0.0.0", port=int(sys.argv[1]))
    else:
        application.run(host="0.0.0.0")
    #app = index2.init_dash(application)
    #application.run(host="0.0.0.0")


