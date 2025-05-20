"""
A configuration helper for the Valtiopaivat Corpus.
"""
import json
import os
import warnings




class ValtiopaivatCorpusConfig:
    """
    Config options for the Valtiopaivat Corpus.
    """
    def __init__(self, **kwargs):
        self.ConfigName = None
        self.ConfigPath = None
        self.ValtiopaivatRecordsTEILocation = None
        self.ValtiopaivatRecordsALTOLocation = None
        self.ValtiopaivatRecordsPDFLocation = None
        self.ValtiopaivatRecordsLOMap = None
        self.ValtiopaivatHandlingarTEILocation = None
        self.ValtiopaivatHandlingarALTOLocation = None
        self.ValtiopaivatHandlingarPDFLocation = None
        self.ValtiopaivatHandlingarLOMap = None
        self.ValtiopaivatRegistersTEILocation = None
        self.ValtiopaivatRegistersALTOLocation = None
        self.ValtiopaivatRegistersPDFLocation = None
        self.ValtiopaivatRegistersLOMap = None

        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                warnings.warn(f"The property -- {k} -- from the config file is not a valid property. Ignoring")

    def write(self):
        """
        Write the config to a file
        """
        with open(self.ConfigPath, 'w+') as outf:
            json.dump(self.__dict__, outf, indent=2)

    def update(self, **kwargs):
        """
        Update attrib values and write

        Args

            kwargs: key = val pairs to update
        """
        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                warnings.warm(f"The property -- {k} -- from the config file is not a valid property. Ignoring")
        self.write()




def track_existing_config(name = None, location = None, overwrite_existing=False):
    """
    Assign a name to an existing config file.

    Args

        name: a name for the config
        location: path and filename for the saved config

    Return

        bool (True == OK)
    """
    if name == None or location == None:
        raise Exception("You have to explicitly set the 'name' and 'location' of a new config.")

    try:
        with open(f"{os.path.abspath(os.path.dirname(__file__))}/cfg_list.json", 'r') as cfg_list_file:
            cfg_list = json.load(cfg_list_file)
    except:
        cfg_list = {}

    if name in cfg_list:
        if overwrite_existing == False:
            raise Exception(f"The name -- {name} -- already exists as a named config. (pass overwrite_existing=True to override this error)")

    cfg_list[name] = os.path.abspath(location)

    with open(f"{os.path.abspath(os.path.dirname(__file__))}/cfg_list.json", 'w+') as cfg_list_file:
        json.dump(cfg_list, cfg_list_file, indent=2)

    return True


def create_new_config(name = None, location = None, **kwargs):
    """
    Create and save a new config object ans save it to a file.

    Args

        name: a name for the config
        location: path and filename for the saved config
        **kwargs: key = val pairs to initialize with

    Rrturn

        config object
    """
    if track_existing_config(name=name, location=location):
        if kwargs is None:
            kwarks = {}
        kwargs["ConfigName"] = name
        kwargs["ConfigPath"] = os.path.abspath(location)
        cfg = ValtiopaivatCorpusConfig(**kwargs)
        cfg.write()

    return cfg


def load_config(name = None, location = None):
    """
    Load an existing config from file. If the config wis created with create_new_config, it can be loaded by name, otherwise, pass a file path.

    Args

        name: name of config
        location: path and file name of saved config.

    Return

        config
    """
    if name == None and location == name:
        raise Error("You need to pass either a name or location for the config file you want to load")

    if location is None:
        try:
            with open(f"{os.path.abspath(os.path.dirname(__file__))}/cfg_list.json", 'r') as inf:
                cfg_list = json.load(inf)
                location = cfg_list[name]
        except Exception as e:
            print("oops...something went wrong")
            print(e)

    with open(location, 'r') as cfg_file:
        cfg = ValtiopaivatCorpusConfig(**json.load(cfg_file))

    cfg.write()

    return cfg
