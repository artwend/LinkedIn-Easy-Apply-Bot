import logging
import os
import yaml

from easyapplybot import EasyApplyBot

log = logging.getLogger(__name__)


if __name__ == '__main__':

    config_absolute_path = os.path.expandvars("%USERPROFILE%/Documents/jobserach/config.yaml")
    with open(config_absolute_path, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0
    assert parameters['username'] is not None
    assert parameters['password'] is not None
    assert parameters['phone_number'] is not None


    if 'uploads' in parameters.keys() and type(parameters['uploads']) == list:
        raise Exception("uploads read from the config file appear to be in list format" +
                        " while should be dict. Try removing '-' from line containing" +
                        " filename & path")

    log.info({k: parameters[k] for k in parameters.keys() if k not in ['username', 'password']})

    output_filename: list = [f for f in parameters.get('output_filename', ['output.csv']) if f is not None]
    output_filename: list = output_filename[0] if len(output_filename) > 0 else 'output.csv'
    blacklist = parameters.get('blacklist', [])
    blackListTitles = parameters.get('blackListTitles', [])

    uploads = {} if parameters.get('uploads', {}) is None else parameters.get('uploads', {})
    for key in uploads.keys():
        assert uploads[key] is not None

    locations: list = [l for l in parameters['locations'] if l is not None]
    positions: list = [p for p in parameters['positions'] if p is not None]

    bot = EasyApplyBot(parameters['username'],
                       parameters['password'],
                       parameters['phone_number'],
                       parameters['salary'],
                       parameters['rate'], 
                       uploads=uploads,
                       filename=os.path.expandvars(output_filename),
                       blacklist=blacklist,
                       blackListTitles=blackListTitles,
                       experience_level=parameters.get('experience_level', [])
                       )
    bot.start_apply(positions, locations)
