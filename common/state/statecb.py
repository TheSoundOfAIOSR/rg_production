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
        stmgr.text = resp['resp']
        stmgr.app.ids['lab'].text = 'voice command received'
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

    # if stmgr.sound_descriptor:
    latent_sliders = [box.children[1] for box in stmgr.app.ids['some_slider'].children]
    latent_sample = [slider.value for slider in latent_sliders]

    heuristic_sliders = [box.children[1] for box in stmgr.app.ids['some_slider1'].children]
    heuristic_measures = [slider.value for slider in heuristic_sliders[1:]]
    velocity = heuristic_sliders[0].value

    stmgr.sound_descriptor['load_preset'] = stmgr.load_preset
    stmgr.sound_descriptor['velocity'] = velocity
    stmgr.sound_descriptor['latent_sample'] = latent_sample
    stmgr.sound_descriptor['heuristic_measures'] = heuristic_measures

    if stmgr.last_generated_note:
        stmgr.sound_descriptor['pitch'] = stmgr.last_generated_note+1
    else:
        stmgr.sound_descriptor['pitch'] = stmgr.root_note

    """ 
    
        if audition audio and no audition audio yet, call sg
        if audition audio and audition audio, nothing new to infer
    
        if text is the same as previously inferred text and sound descriptor is not none -> call SG
        
        else if text is different from previously inferred text -> call TTS
        
        else error
    """

    # if stmgr.text == stmgr.last_transcribed_text and not stmgr.sound_descriptor:
    #     stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_nothing_to_infer'})
    if stmgr.text is not stmgr.last_transcribed_text and stmgr.text:
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_start_tts', 'res':args})
    elif stmgr.audition_audio and not type(stmgr.audition_audio_sample) == type(None):
        stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_finish_sg'})
    elif stmgr.audition_audio and type(stmgr.audition_audio_sample) == type(None):
        stmgr.sound_descriptor['pitch'] = 52
        stmgr.dispatch('on_pipeline_action',  {'action':'pipeline_action_start_sg', 'res':args})
    elif stmgr.last_generated_note == stmgr.root_note + 48:

        stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_finish_sg'})
    elif stmgr.text == stmgr.last_transcribed_text and stmgr.text is not stmgr.sound_descriptor: #both could be none
        stmgr.dispatch('on_pipeline_action',  {'action':'pipeline_action_start_sg', 'res':args})
    else:
        stmgr.app.ids['lab'].text = "Nothing new to infer"
        stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_nothing_to_infer'})

async def tts_transcribe_cb(*args, stmgr=None):

    resp = args[0]

    logger.debug(f"{resp}")
    if resp['resp']:

        sound_descriptor = {}
        for key, value in resp['resp'].items():
            # if key == 'pitch':
            #     stmgr.root_note = value
            #     stmgr.csound.root = value
            if key == 'source':
                value = value.lower()
            if key == 'qualities':
                value = [v.lower() for v in value]
            sound_descriptor[key] = value

        stmgr.load_preset = True
        stmgr.sound_descriptor = sound_descriptor
        stmgr.last_transcribed_text = stmgr.text
        # for num, child in enumerate(stmgr.app.ids['some_slider'].children):
        #     val = resp['resp']['latent_sample'][num]
        #     child.children[1].value = val
        #     child.children[0].text = str(val)

        stmgr.app.ids['lab'].text = str(stmgr.sound_descriptor)

        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_descriptor', 'res':args})
    else:
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})


async def sound_gen_cb(*args, stmgr=None):

    logger.debug(f"{args[0].keys()}")
    resp = args[0]

    if resp['resp'] and resp['success']:
        logger.debug(f"Received Sound successfully for pitch {stmgr.sound_descriptor['pitch']}")
        if stmgr.audition_audio:
            logger.debug(f"Received audition audio")
            stmgr.audition_audio_sample = np.array(resp['resp'])
        else:
            stmgr.last_generated_note = stmgr.sound_descriptor['pitch']
            stmgr.samples[stmgr.last_generated_note] = np.array(resp['resp'])
        # update sliders

        stmgr.last_sound_parameters = stmgr.sound_descriptor
        stmgr.app.ids['lab'].text = "Received Sound "
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_audio', 'res':args})
    else:
        stmgr.dispatch('on_pipeline_action', {'action':'handle_errors', 'res':args})

async def setup_preprocessing(*args, stmgr=None):
    folder = stmgr.csound.audio_dir.as_posix()
    logger.debug(f"Setup preprocessing w/ state {stmgr.state}")

    if stmgr.audition_audio:
        logger.debug(f"Audition audio preprocess")
        preprocess(csound=stmgr.csound,folder=folder, audio=stmgr.audition_audio_sample, audition=True, stmgr=stmgr)
        stmgr.audition_audio = False
    else:
        for note in stmgr.samples.keys():
            logger.debug(f"{stmgr.samples[note]}")
            preprocess(csound=stmgr.csound,folder=folder, audio=stmgr.samples[note], note=note, stmgr=stmgr)
    # Call update function here
    stmgr.app.ids['record'].disabled = False
    logger.debug(f"Finished preprocessing")
    logger.debug(f"{stmgr.state}")
    stmgr.last_generated_note = None
    stmgr.load_preset = False
    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_finished_preprocessing', 'res': args})


async def play_idle_cb(*args, stmgr=None):
    stmgr.app.ids['record'].disabled = False
    stmgr.app.ids['generate'].disabled = False

async def finished_model_setup(*args, stmgr=None):

    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_go_to_playing'})