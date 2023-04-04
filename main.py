import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import functions_framework
from flask import Flask, request

# Application Default credentials are automatically created.
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
@functions_framework.http



@app.route('/')
def index():
    return "hello there"


@app.route('/new_voter', methods = ['POST'])
def new_voter():
    data = request.json
    student_id = data['student_id']
    Fname = data['Fname']
    Lname = data['Lname']
    year = data['year']

    voters_ref = db.collection('voters').document(student_id)

    if voters_ref.get().exists:
        return f"{student_id} already exists", 400

    # If user doesn't exist, register them
    voter_data = {
        'student_id': student_id,
        'Fname': Fname,
        'Lname': Lname,
        'year': year
    }
    voters_ref.set(voter_data)

    return f"Successfully registered {Fname}!"


@app.route('/delete_voter/<student_id>', methods=['DELETE'])
def deregister_student(student_id):
    # Delete the document with the provided student_id from the "voters" collection
    doc_name = student_id.strip()
    voters_ref = db.collection('voters').document(doc_name)


    if voters_ref.get().exists:
        db.collection('voters').document(doc_name).delete()
        return f"Successfully deregistered student with ID {doc_name}"
    else:
        return f"No such document with ID {doc_name}"


@app.route('/view_voter/<student_id>', methods=['GET'])
def retrieve_student(student_id):
    doc_name = student_id.strip()
    voters_ref = db.collection('voters').document(doc_name)

    try:
        doc = voters_ref.get()

        if doc.exists:
            return f"Document data: {doc.to_dict()}"
        else:
            return f"No such document with ID {doc_name}"
    except Exception as e:
        print("Error retrieving".format(e))



@app.route('/update_voter/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    Fname = data['Fname']
    Lname = data['Lname']
    year = data['year']
    doc_name = student_id.strip()
    voters_ref = db.collection('voters').document(doc_name)


    doc = voters_ref.get()
    if doc.exists:
        voters_ref.update({
            'Fname': Fname,
            'Lname': Lname,
            'year': year,
        })
        updated_doc = voters_ref.get()
        return f"Document data: {updated_doc.to_dict()}"
    else:
        return f"No such document with ID {doc_name}"


@app.route('/create_election', methods=['POST'])
def create_election():
    elec_data = request.json
    elec_id = elec_data['elec_id']
    elec_name = elec_data['elec_name']
    candidates = elec_data['candidates']
    votes = {candidate: 0 for candidate in candidates}

    elec_ref = db.collection('Elections').document(elec_id)

    if elec_ref.get().exists:
        return f"{elec_id} already exists", 400

    elec_data = {
        'elec_id': elec_id,
        'elec_name': elec_name,
        'candidates': candidates,
        'votes': votes
        }
    elec_ref.set(elec_data)

    return f"Successfully registered {elec_name}!"

@app.route('/view_election/<elec_id>', methods=['GET'])
def view_election(elec_id):
    elec_doc = elec_id.strip()
    elec_ref = db.collection('Elections').document(elec_doc)

    try:
        doc = elec_ref.get()

        if doc.exists:
            return f"Document data: {doc.to_dict()}"
        else:
            return f"No such document with ID {elec_doc}"
    except Exception as e:
        print("Error retrieving".format(e))

@app.route('/delete_election/<elec_id>', methods=['DELETE'])
def delete_election(elec_id):
    # Delete the document with the provided student_id from the "voters" collection
    elec_doc = elec_id.strip()
    elec_ref = db.collection('Elections').document(elec_doc)


    if elec_ref.get().exists:
        db.collection('Elections').document(elec_doc).delete()
        return f"Successfully deleted Election with ID {elec_doc}"
    else:
        return f"No such document with ID {elec_doc}"


@app.route('/update_election/<elec_id>', methods=['PUT'])
def update_election(elec_id):
    elec_data = request.json
    elec_name = elec_data['elec_name']
    candidates = elec_data['candidates']
    elec_doc = elec_id.strip()
    elec_ref = db.collection('Elections').document(elec_doc)


    doc = elec_ref.get()
    if doc.exists:
        elec_ref.update({
            "elec_name":elec_name,
            "candidates": candidates
        })
        updated_doc = elec_ref.get()
        return f"Document data: {updated_doc.to_dict()}"
    else:
        return f"No such document with ID {elec_doc}"


@app.route('/cast_vote/<elec_id>', methods=['POST'])
def cast_vote(elec_id):
    elec_data = request.json
    candidate = elec_data['candidate']
    elec_doc = elec_id.strip()
    elec_ref = db.collection('Elections').document(elec_doc)
    doc = elec_ref.get()

    if not doc.exists:
        return f"No such document with ID {elec_doc}", 404

    elec_data = doc.to_dict()
    candidates = elec_data['candidates']
    votes = elec_data['votes']

    if candidate not in candidates:
        return f"{candidate} is not a valid candidate", 400

    votes[candidate] += 1
    elec_ref.update({'votes': votes})

    return f"Successfully cast vote for {candidate} in {elec_data['elec_name']}"



if __name__ == '__main__':
    app.run(debug=True)