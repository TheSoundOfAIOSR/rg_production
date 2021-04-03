import asyncio
import common.log as log
from common.state.StateEnum import StateEnum
from dummy_ws_requests import *
from functools import *
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

async def infer_pipeline(stmgr, *args):
    print("Inferring pipeline")
    stmgr.app.root.ids['record'].disabled = True
    print(stmgr.sound_descriptor)
    if stmgr.sound_descriptor:
        print("here")
        latent_sample = [slider.value for slider in stmgr.app.root.ids['some_slider'].children]
        stmgr.sound_descriptor['latent_sample'] = latent_sample

    print(stmgr.sound_descriptor)
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
        logger.log("Something went wrong inferring pipeline ")

async def tts_transcribe_cb(*args, stmgr=None):
    print(tts_transcribe_cb)
    res = args[0]
    if res['resp']:
        stmgr.sound_descriptor = res['resp']
        stmgr.last_transcribed_text = stmgr.text
        stmgr.app.root.ids['lab'].text = str(stmgr.sound_descriptor)
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_descriptor', 'res':args})
    else:
        # TODO
        pass


async def sound_gen_cb(*args, stmgr=None):
    res = args[0]
    if res['resp']:
        stmgr.audio = res['resp']
        stmgr.last_sound_parameters = stmgr.sound_descriptor
        stmgr.app.root.ids['lab'].text = "Received Sound "
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_audio', 'res':args})

async def preprocessing_cb(*args, stmgr=None):

    stmgr.app.root.ids['record'].disabled = False
    logger.debug(f"Finished preprocessing {stmgr.audio}")
    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_finished_preprocessing', 'res': args})

async def play_idle_cb(*args, stmgr=None):
    # reinitialize record button,
    stmgr.app.root.ids['record'].state= 'normal'
    stmgr.app.root.ids['record'].disabled = False
    if stmgr.text is not stmgr.last_transcribed_text or stmgr.sound_descriptor is not stmgr.last_sound_parameters:
        stmgr.app.root.ids['generate'].disabled = False
    else:
        stmgr.app.root.ids['generate'].disabled = True

async def finished_model_setup(*args, stmgr=None):

    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_go_to_playing'})