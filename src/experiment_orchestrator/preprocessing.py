#!/usr/bin/env python
# -*- coding: utf-8 -*-




# import yaml
# with open("config.yaml") as f:
#   config = yaml.safe_load(f)
# config = comm.bcast(config, root=0)

def load_config():
    # Load config (read YAML)
    config = {
            "SBML" : "somewhere",
            "seed": 42,
            "info": "foo"
            }

    # VALIDATE the config before sending it to all cores!!
    # required = ["sbml_file", "output_dir"]
    # for key in required:
    #   if key not in config:
    #       raise ValueError(f"Missing configuration key: {key}.")

    return config

