import pprint
import wci
from credentials import email_address, password

w = wci.WeConnectId(email_address, password)

vehicles = w.get('/vehicles')

print('list of vehicles:')
pprint.pprint(vehicles)

print('\n---\n\n')

print('specific vehicle:')
pprint.pprint(w.get('/vehicles/' + vehicles['data'][0]['vin'] + '/selectivestatus?jobs=all'))
