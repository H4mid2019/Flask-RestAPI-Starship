from flask import Flask, jsonify, json, request
import requests

app = Flask('Starships1API')
app.config['JSON_SORT_KEYS'] = False




@app.route('/', methods=['GET', 'POST','PUT',"DELETE"])
def starshipsapi():
    if request.method == 'GET':
        l = []
        ii = 1
        while True:
            url = "https://swapi.co/api/starships/?page="+str(ii)
            try:
                res = requests.get(url)
            except requests.ConnectionError:
                return "Connection Error"
            ii += 1
            l.append(json.loads(res.text)['results'])
            if json.loads(res.text)['next'] == None:
                break

        starships = []
        starships_unknown_hyperdrive = []
        for i in l:
            for ii in i:
                if ii['hyperdrive_rating'] != 'unknown':
                    starships.append(dict({'name':ii['name'] ,'hyperdrive_rating':ii['hyperdrive_rating']}))
                else:
                    starships_unknown_hyperdrive.append(dict({'name':ii['name']}))
        starships_sorted = sorted(starships, key = lambda i: i['hyperdrive_rating'], reverse=False) 
        return jsonify({'starships': starships_sorted,'starships_unknown_hyperdrive':starships_unknown_hyperdrive})
    return jsonify({"message":"The method is NOT allowed."}) , 405


if __name__ == '__main__':
    app.run(debug=True, port=8081)
