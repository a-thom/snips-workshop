#!/usr/bin/env python2
# -- coding: utf-8 --
import ConfigParser
from hermes_python.hermes import Hermes
import pyowm
import io


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

INTENT_HOW_ARE_YOU = "a-thom:weather_at_place"

INTENT_FILTER_FEELING = [INTENT_GOOD, INTENT_BAD, INTENT_ALRIGHT]


def main():
    config = read_configuration_file(CONFIG_INI)
    owm = pyowm.OWM(config["secret"]["owm_key"])

    with Hermes("localhost:1883") as h:
        h.owm = owm
        h.subscribe_intent(INTENT_HOW_ARE_YOU, weather_at_place_callback) \
         .start()


def weather_at_place_callback(hermes, intent_message):
    session_id = intent_message.session_id

    # set mood according to weather
    config = read_configuration_file(CONFIG_INI)
    city = intent_message.slots.cities.first().value

    observation = hermes.owm.weather_at_place(city)
    w = observation.get_weather()
    temp = w.get_temperature('celsius')["temp"]
    if temp >= float(15):
        response = "It's freaking shining like a motherfucker outside"
    else:
        response = "It's fucking freezing outside."

    hermes.publish_end_session(session_id, response)

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()


if _name_ == "_main_":
    main()
