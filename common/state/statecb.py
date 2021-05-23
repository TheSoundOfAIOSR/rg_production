import asyncio
import common.log as log
from common.state.StateEnum import StateEnum
from dummy_ws_requests import *
from functools import *
from common.taudio.PreprocessingSample import preprocess
import numpy as np
from sys import platform

logger = log.setup_logger()

async def start_recording_cb(*args, stmgr=None):

    resp = args[0]
    logger.debug(f"{resp}")
    if resp['resp']:
        stmgr.app.ids['generate'].disabled = True
    elif not resp['resp']:
        stmgr.app.ids['lab'].text = str(resp)
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_started_recording_failed'})
        logger.info(f"{resp}")
    else:
        logger.info(f"Something unexpected went wrong in STT Start")
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})


async def stop_recording_cb(*args, stmgr=None):

    resp = args[0]
    logger.debug(f"{resp}")
    if resp['resp']:
        stmgr.text = resp['resp'].lower()
        stmgr.app.ids['lab'].text = stmgr.text
        stmgr.app.ids['generate'].disabled = False
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_text'})
    elif not resp['resp']:
        stmgr.app.ids['lab'].text = str(resp)
        logger.debug(f"There was an error when STT module returned {resp}")
    else:
        logger.info("Something unexpected went wrong in STT Stop")
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})


async def infer_pipeline(stmgr, *args):
    stmgr.app.ids['record'].disabled = True
    stmgr.app.ids['generate'].disabled = True
    if stmgr.sound_descriptor:
        latent_sample = [slider.value for slider in stmgr.app.ids['some_slider'].children]
        stmgr.sound_descriptor['latent_sample'] = latent_sample

    """ 
        if text is the same as previously inferred text and sound descriptor is not none -> call SG
        
        else if text is different from previously inferred text -> call TTS
        
        else error
    """
    if stmgr.text == stmgr.last_transcribed_text and stmgr.text is not stmgr.sound_descriptor: #both could be none

        stmgr.dispatch('on_pipeline_action',  {'action':'pipeline_action_start_sg', 'res':args})

    elif stmgr.text is not stmgr.last_transcribed_text and stmgr.text:
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_start_tts', 'res':args})
    else:
        stmgr.app.ids['lab'].text = "Nothing new to infer"
        stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_nothing_to_infer'})

async def tts_transcribe_cb(*args, stmgr=None):

    resp = args[0]

    logger.debug(f"{resp}")
    if resp['resp']:

        sound_descriptor = {}
        for key, value in resp['resp'].items():
            if key == 'source':
                value = value.lower()
            if key == 'qualities':
                value = [v.lower() for v in value]
            sound_descriptor[key] = value

        stmgr.sound_descriptor = sound_descriptor
        stmgr.last_transcribed_text = stmgr.text
        for num, child in enumerate(stmgr.app.ids['some_slider'].children):
            child.value = resp['resp']['latent_sample'][num]

        stmgr.app.ids['lab'].text = str(stmgr.sound_descriptor)

        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_descriptor', 'res':args})
    else:
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})


async def sound_gen_cb(*args, stmgr=None):

    resp = args[0]
    if resp['resp'] and resp['success']:
        logger.debug("Received Sound successfully")
        stmgr.audio = np.array(resp['resp'][0])
        stmgr.last_sound_parameters = stmgr.sound_descriptor
        stmgr.app.ids['lab'].text = "Received Sound "
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_audio', 'res':args})
    else:
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})

async def setup_preprocessing(*args, stmgr=None):


    folder = stmgr.csound.audio_dir.as_posix()
    preprocess(folder=folder, audio=stmgr.audio, root=60, shifts=48)
    stmgr.app.ids['record'].disabled = False
    logger.debug(f"Finished preprocessing")
    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_finished_preprocessing', 'res': args})


async def play_idle_cb(*args, stmgr=None):
    # reinitialize record button,
    stmgr.app.ids['record'].state= 'normal'
    stmgr.app.ids['record'].disabled = False
    stmgr.app.ids['generate'].disabled = False

    # if stmgr.text is not stmgr.last_transcribed_text or stmgr.sound_descriptor is not stmgr.last_sound_parameters:
    #     stmgr.app.root.ids['generate'].disabled = False
    # else:
    #     stmgr.app.root.ids['generate'].disabled = True

async def finished_model_setup(*args, stmgr=None):

    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_go_to_playing'})