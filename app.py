from datetime import date
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

DOCUMENTS = {
    "rental": {"name": "Rental Agreement", "fields": [("landlord", "Landlord name"), ("tenant", "Tenant name"), ("property", "Property address"), ("rent", "Monthly rent (₹)"), ("term", "Agreement period") ]},
    "leave": {"name": "Leave Request Letter", "fields": [("employee", "Your name"), ("manager", "Manager name"), ("organization", "Organization"), ("from_date", "Leave from"), ("to_date", "Leave to"), ("reason", "Reason") ]},
    "noc": {"name": "No Objection Certificate", "fields": [("issuer", "Issued by / organization"), ("person", "Name of person"), ("purpose", "Purpose"), ("date", "Date") ]},
}


def generate(kind, data):
    if kind == "rental":
        return (f"RENTAL AGREEMENT\n\nThis rental agreement is made between {data['landlord']} (Landlord) and {data['tenant']} (Tenant) for the property at {data['property']}.\n\nThe tenancy period is {data['term']}. The monthly rent is ₹{data['rent']}, payable as agreed between the parties. The Tenant agrees to use the property responsibly and the Landlord agrees to provide access to the property for the tenancy period. Any changes to these terms should be recorded in writing and signed by both parties.\n\nLandlord signature: ____________________    Date: __________\nTenant signature: ______________________    Date: __________")
    if kind == "leave":
        return (f"LEAVE REQUEST\n\nDate: {date.today().strftime('%d %B %Y')}\n\nTo: {data['manager']}\n{data['organization']}\n\nSubject: Leave request\n\nDear {data['manager']},\n\nI, {data['employee']}, kindly request leave from {data['from_date']} to {data['to_date']} due to {data['reason']}. I will make the necessary arrangements for my responsibilities during this period.\n\nThank you for your consideration.\n\nSincerely,\n{data['employee']}")
    return (f"NO OBJECTION CERTIFICATE\n\nDate: {data['date']}\n\nTo whom it may concern,\n\n{data['issuer']} has no objection to {data['person']} proceeding with the following purpose: {data['purpose']}. This certificate is issued upon request for the stated purpose.\n\nAuthorized signatory: ____________________\nName and designation: ____________________\nOrganization seal: ________________________")


@app.route("/", methods=["GET", "POST"])
def home():
    selected = request.form.get("document", "leave")
    if selected not in DOCUMENTS:
        selected = "leave"
    output = None
    values = {}
    if request.method == "POST":
        values = {key: request.form.get(key, "").strip() for key, _ in DOCUMENTS[selected]["fields"]}
        if all(values.values()):
            output = generate(selected, values)
        else:
            return render_template("index.html", documents=DOCUMENTS, selected=selected, values=values, error="Please complete every field before generating your document.", output=None)
    return render_template("index.html", documents=DOCUMENTS, selected=selected, values=values, output=output, error=None)


@app.post("/download")
def download():
    kind = request.form.get("document", "leave")
    if kind not in DOCUMENTS:
        kind = "leave"
    values = {key: request.form.get(key, "").strip() for key, _ in DOCUMENTS[kind]["fields"]}
    if not all(values.values()):
        return "Complete all fields before downloading.", 400
    response = make_response(generate(kind, values))
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=legalease-{kind}-document.txt"
    return response


if __name__ == "__main__":
    app.run(debug=True)
