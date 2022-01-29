# we-connect-id in Python
This is a Python wrapper around the API used by We Connect ID, used in Volkwagen's ID.4 cars.

Look in `example.py` or `example-with-cache.py` to see how `wci.py` is used. The latter shows how you can use the API without explicitly signing in every single time, by saving a previous session in a text/cache file.

There is unfortunately no reference of the endpoints and/or HTTP methods, but what's provided in the examples should help you to at least retrieve some data from your Volkswagen ID.4 car.