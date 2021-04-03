import asyncio
import common.log as log
from common.state.StateEnum import StateEnum
from dummy_ws_requests import *
from functools import *
logger = log.setup_logger()

async def _callback(f, callback=None, stmgr = None):

    return await callback(await f(), stmgr=stmgr) if callback else await f()

async def toggle_record(stmgr, *args):
    logger.debug(f"Toggle Record {stmgr.state}")
    if stmgr.state == StateEnum.Playing_Idle:
        asyncio.create_task(_callback(partial(dummy_stt_start, [stmgr.microphone_hint]), callback=start_recording_cb, stmgr=stmgr))
    if stmgr.state == StateEnum.Recording:
        asyncio.create_task(_callback(partial(dummy_stt_stop), callback=stop_recording_cb, stmgr=stmgr))

async def start_recording_cb(*args, stmgr=None):
    print(args)
    resp = args[0]
    if resp['resp']:
        stmgr.app.root.ids['generate'].disabled = True
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_started_recording'})
    elif not resp['resp']:
        stmgr.app.root.ids['lab'].text = str(resp)
        logger.info(f"{resp}")
    else:
        logger.info(f"Something unexpected went wrong in STT Start")


async def stop_recording_cb(*args, stmgr=None):
    print(stmgr)
    resp = args[0]
    print(resp)
    resp['resp'] = "A warm guitar sound"
    logger.debug(f"Manually setting resp['resp'] stop_recording_cb ")
    print(resp['resp'])
    if resp['resp']:
        stmgr.text = resp['resp']
        stmgr.app.root.ids['lab'].text = stmgr.text
        stmgr.app.root.ids['generate'].disabled = False
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_stop_recording'})
    elif not resp['resp']:
        stmgr.app.root.ids['lab'].text = str(resp)
        logger.debug(f"There was an error when STT module returned {resp}")
    else:
        logger.info("Something unexpected went wrong in STT Stop")

async def infer_pipeline(stmgr, *args):
    print("Inferring pipeline")
    stmgr.app.root.ids['record'].disabled = True
    if stmgr.text is not None and stmgr.text is not stmgr.last_transcribed_text:
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_start_tts', 'res':args})
    elif stmgr.text == stmgr.last_transcribed_text:
        stmgr.dispatch('on_pipeline_action',  {'action':'pipeline_action_start_sg', 'res':args})


async def tts_transcribe_cb(*args, stmgr=None):
    res = args[0]
    if res['res']:
        stmgr.sound_descriptor = res['res']
        stmgr.app.root.ids['lab'].text = str(stmgr.sound_descriptor)
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_start_sg', 'res':args})

async def sound_gen_cb(*args, stmgr=None):
    res = args[0]
    if res['res']:
        stmgr.app.root.ids['lab'].text = "Received Sound "
        stmgr.dispatch('on_pipeline_action', {'action':'pipeline_action_received_audio', 'res':args})

async def preprocessing_cb(*args, stmgr=None):

    stmgr.app.root.ids['record'].disabled = False
    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_finished_preprocessing', 'res': args})

async def finished_model_setup(*args, stmgr=None):

    stmgr.dispatch('on_pipeline_action', {'action': 'pipeline_action_go_to_playing'})