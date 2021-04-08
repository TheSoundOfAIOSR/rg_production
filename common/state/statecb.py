import asyncio
import common.log as log
from common.state.StateEnum import StateEnum
from dummy_ws_requests import *
from functools import *
from common.taudio.PreprocessingSample import preprocess
import numpy as np

logger = log.setup_logger()

async def start_recording_cb(*args, stmgr=None):
    print("Start recording callback")

    print(args)
    resp = args[0]
    if resp['resp']:
        stmgr.app.root.ids['generate'].disabled = True
    elif not resp['resp']:
        stmgr.app.root.ids['lab'].text = str(resp)
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_started_recording_failed'})
        logger.info(f"{resp}")
    else:
        logger.info(f"Something unexpected went wrong in STT Start")
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})


async def stop_recording_cb(*args, stmgr=None):
    print("Stop recording callback")
    resp = args[0]
    print(resp)
    if resp['resp']:
        stmgr.text = resp['resp']
        stmgr.app.root.ids['lab'].text = stmgr.text
        stmgr.app.root.ids['generate'].disabled = False
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_text'})
    elif not resp['resp']:
        stmgr.app.root.ids['lab'].text = str(resp)
        logger.debug(f"There was an error when STT module returned {resp}")
    else:
        logger.info("Something unexpected went wrong in STT Stop")
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})


async def infer_pipeline(stmgr, *args):
    stmgr.app.root.ids['record'].disabled = True
    stmgr.app.root.ids['generate'].disabled = True
    if stmgr.sound_descriptor:
        latent_sample = [slider.value for slider in stmgr.app.root.ids['some_slider'].children]
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
        stmgr.app.root.ids['lab'].text = "Nothing new to infer"
        stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_nothing_to_infer'})

async def tts_transcribe_cb(*args, stmgr=None):
    print(tts_transcribe_cb)
    res = args[0]
    if res['resp']:
        stmgr.sound_descriptor = res['resp']
        stmgr.last_transcribed_text = stmgr.text
        stmgr.app.root.ids['lab'].text = str(stmgr.sound_descriptor)
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_descriptor', 'res':args})
    else:
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})


async def sound_gen_cb(*args, stmgr=None):
    print("sound gen callback")
    res = args[0]
    if res['resp']:
        print("here")
        stmgr.audio = np.array(res['resp'][0])
        stmgr.last_sound_parameters = stmgr.sound_descriptor
        stmgr.app.root.ids['lab'].text = "Received Sound "
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_audio', 'res':args})
    else:
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})

async def setup_preprocessing(*args, stmgr=None):
    print("In setup preprocessing")

    folder = stmgr.app.csound.audio_dir.as_posix()
    preprocess(folder=folder, audio=stmgr.audio, root=60, shifts=48)
    stmgr.app.root.ids['record'].disabled = False
    logger.debug(f"Finished preprocessing")
    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_finished_preprocessing', 'res': args})


async def play_idle_cb(*args, stmgr=None):
    # reinitialize record button,
    stmgr.app.root.ids['record'].state= 'normal'
    stmgr.app.root.ids['record'].disabled = False
    stmgr.app.root.ids['generate'].disabled = False

    # if stmgr.text is not stmgr.last_transcribed_text or stmgr.sound_descriptor is not stmgr.last_sound_parameters:
    #     stmgr.app.root.ids['generate'].disabled = False
    # else:
    #     stmgr.app.root.ids['generate'].disabled = True

async def finished_model_setup(*args, stmgr=None):

    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_go_to_playing'})