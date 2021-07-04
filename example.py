import pprint
import wci

w = wci.WeConnectId('email address', 'password')

vehicles = w.get('/vehicles')

print('list of vehicles:')
pprint.pprint(vehicles)

print('\n---\n\n')

print('specific vehicle:')
pprint.pprint(w.get('/vehicles/' + vehicles['data'][0]['vin'] + '/status'))