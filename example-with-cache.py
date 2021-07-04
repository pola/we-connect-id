import pprint
import wci
from credentials import email_address, password

print('number of vehicles:')
w1 = wci.WeConnectId(email_address, password)
pprint.pprint(len(w1.get('/vehicles')['data']))

access_token = w1.get_access_token()

print('number of vehicles with access token from previous session:')
w2 = wci.WeConnectId(email_address, password, access_token)
pprint.pprint(len(w2.get('/vehicles')['data']))
