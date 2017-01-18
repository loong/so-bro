#!flask/bin/python
from flask import Flask, jsonify, abort, request

from google.cloud import bigquery

# Instantiates a client
bigquery_client = bigquery.Client()

app = Flask(__name__)



def get_keyword(msg):
    return filter(lambda x: "Error" in x or "Exception" in x, msg.split("\n") )

# put in query param keyword
@app.route('/get')
def get_results():
    message = request.args.get('message', '')

    if not message:
        abort(400)

    keyword = get_keyword(message)

    if not keyword:
        print "Cannot find keyword"
        abort(400)

    param = bigquery.ScalarQueryParameter(None, 'STRING', "%%%s%%" % keyword[-1])

    query_results = bigquery_client.run_sync_query(
        """SELECT id, title, body, view_count, score, tags
        FROM `bigquery-public-data.stackoverflow.posts_questions`
        WHERE
            (title LIKE ?
            OR
            body LIKE ?)
            AND tags LIKE '%python%'
        ORDER BY
            view_count DESC
        LIMIT 10""",
        query_parameters=(param, param))


    # Use standard SQL syntax for queries.
    # See: https://cloud.google.com/bigquery/sql-reference/
    query_results.use_legacy_sql = False

    query_results.run()

    # Drain the query results by requesting a page at a time.
    page_token = None

    result = []
    while True:
        rows, total_rows, page_token = query_results.fetch_data(
            max_results=10,
            page_token=page_token)

        for row in rows:
            dic = {}
            dic["url"] = "http://stackoverflow.com/questions/%s" % row[0]
            dic["title"] = row[1]
            dic["body"] = row[2]
            dic["score"] = row[3]
            dic["tags"] = row[4]
            result.append(dic)

        if not page_token:
            break

    return jsonify({"result":result})

if __name__ == '__main__':
    app.run(debug=True)
