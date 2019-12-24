from flask import Flask, json
from flask_restful import Resource, Api
import requests
import time
import threading


app = Flask('StarshipsAPI')
api = Api(app)

starships_sorted = [{'message':'Updating...please retry after 15 seconds.'}]
starships_unknown_hyperdrive = [{'message':'Updating...please retry after 15 seconds.'}]

def retriever():
    global starships_sorted
    global starships_unknown_hyperdrive
    l = []
    ii = 1
    while True:
        url = "https://swapi.co/api/starships/?page="+str(ii)
        try:
            res = requests.get(url)
        except requests.ConnectionError:
            starships_sorted = [{'message':'There is an issue with connecting to the server.'}]
            starships_unknown_hyperdrive = [{'message':'There is an issue with connecting to the server.'}]
            return "Connection Error"            
        ii += 1
        l.append(json.loads(res.text)['results'])
        if json.loads(res.text)['next'] == None:
            break

    starships = []
    for i in l:
        for ii in i:
            if ii['hyperdrive_rating'] != 'unknown':
                starships.append(dict({'name':ii['name'] ,'hyperdrive_rating':ii['hyperdrive_rating']}))
            else:
                starships_unknown_hyperdrive.append(dict({'name':ii['name']}))
    starships_sorted = sorted(starships, key = lambda i: i['hyperdrive_rating'], reverse=False)
    threading.Timer(500, retriever).start()
    return True 


threading.Thread(name="retriever", target=retriever).start()

class StartshipsRestful(Resource):
    def get(self):
        return {'starships': starships_sorted,'starships_unknown_hyperdrive':starships_unknown_hyperdrive}


api.add_resource(StartshipsRestful, '/')

if __name__ == '__main__':
    app.run(debug=True, port=8082)

    
    
    