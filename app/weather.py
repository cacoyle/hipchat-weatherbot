from flask import Flask, render_template, request
import json
import requests
import urllib2

wunderground_key = ""
hipchat_url = ""
headers = {"content-type": "application/json"}

def get_temp_by_zip(requestor, zip_code):
	from pyzipcode import ZipCodeDatabase

	zcdb = ZipCodeDatabase()

	zipcode = zcdb[zip_code]

	city = zipcode.city

	if " " in city:
		city = "_".join(city.split())

	wunderground = "http://api.wunderground.com/api/%s/geolookup/conditions/q/%s/%s.json" % (wunderground_key, zipcode.state, city)

	f = urllib2.urlopen(wunderground)
	json_string = f.read()
	parsed_json = json.loads(json_string)
	location = parsed_json['location']['city']
	temp_f = parsed_json['current_observation']['temp_f']
	f.close()

	return "@%s: Current temperature in %s, %s is: %s" % (requestor, location, zipcode.state, temp_f)

app = Flask(__name__)
app.debug = True
app.host = '0.0.0.0'

@app.route("/", methods=['GET','POST'])
def main():
	data = request.get_json()
	requestor = data["item"]["message"]["from"]["mention_name"]
	zipcode = data["item"]["message"]["message"].split()[1]

	result = {
		"color": "green",
		"message": get_temp_by_zip(requestor, zipcode),
		"notify": False,
		"message_format": "text"
	}

	resp = requests.post(hipchat_url, data=json.dumps(result), headers=headers)

	return("OK")

if __name__ == "__main__":
	app.run(host='0.0.0.0')
