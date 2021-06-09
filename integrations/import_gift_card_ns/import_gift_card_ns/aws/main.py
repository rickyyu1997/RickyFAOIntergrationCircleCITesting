# -*- coding: utf-8 -*-
# Copyright (C) 2015, 2016 NewStore, Inc. All rights reserved.
import logging
from import_gift_card_ns.aws.sync import run
from lambda_utils.config.config_handler import get_env_variables

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def handler(event, context):
    env_variables = None if not context else get_env_variables(context.function_name)

    LOGGER.info(f'Event: {event}')
    LOGGER.info(f'ENV variables {env_variables}')

    run(env_variables)
