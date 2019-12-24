from flask import Flask, json
from flask_restful import Resource, Api
import requests
import time
import threading


app = Flask('StarshipsAPI')
api = Api(app)




starships_sorted = 0
starships_unknown_hyperdrive = 0

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
    threading.Timer(15, retriever).start()
    return True 



class StartshipsRestful(Resource):
    def get(self):
        return {'starships': starships_sorted,'starships_unknown_hyperdrive':starships_unknown_hyperdrive}


api.add_resource(StartshipsRestful, '/')

if __name__ == '__main__':
    t1 = threading.Thread(name="retriever", target=retriever) 
    t1.start()
    app.run(debug=True, port=8082)

    
    
    