import asyncio
import common.log as log
from common.state.StateEnum import StateEnum
from dummy_ws_requests import *
from functools import *
logger = log.setup_logger()

def updating(stmgr):
    if INITIALIZED and stmgr.state & StateEnum.RECORDING:
        stmgr.stt.stop()
        stmgr.state = ...

def dispatch_slider_set(stmgr, response):
    for slider in app.root.sliders.list:
        ...
def playing_idle(stmgr):
    pass
    # if stmgr.source == ... and stmgr.recording_status == ...:
    #     ...
    #     app.sliders ...
    # elif ...:
    #     ...
    #     return {"resp": False}

async def _callback(f, callback=None, stmgr = None):

    return await callback(await f(), stmgr=stmgr) if callback else await f()

async def toggle_record(stmgr, *args):
    logger.debug(f"Toggle Record {stmgr.state}")
    if stmgr.state == StateEnum.Playing_Idle:
        asyncio.create_task(_callback(partial(dummy_stt_start, [stmgr.microphone_hint]), callback=start_recording_cb, stmgr=stmgr))
    if stmgr.state == StateEnum.Recording:
        asyncio.create_task(_callback(partial(dummy_stt_stop), callback=stop_recording_cb, stmgr=stmgr))

async def start_recording_cb(*args, stmgr=None):
    if args[0] == True:
        stmgr.app.root.ids['generate'].disabled = True
        stmgr.dispatch('on_enter_state', {'action':'state_change_toggle_record'})
    elif args[0] == False:
        error_message = "Error: stt_start"
        stmgr.app.root.ids['lab'].text = str(error_message)
        logger.info(f"{error_message}")
    else:
        logger.info(f"Something went wrong in STT Start ")


async def stop_recording_cb(*args, stmgr=None):
    res = args[0]
    if res['res']:
        stmgr.text = res['res']
        stmgr.app.root.ids['lab'].text = str(stmgr.text)
        stmgr.app.root.ids['generate'].disabled = False
        stmgr.dispatch('on_enter_state', {'action':'state_change_toggle_record', 'res':args})
    else:
        error_message = "Error: stt_stop"
        stmgr.app.root.ids['lab'].text = str(error_message)
        logger.info(f"{error_message}")

async def infer_pipeline(stmgr, *args):
    stmgr.app.root.ids['record'].disabled = True
    if stmgr.text is not None and stmgr.text is not stmgr.last_transcribed_text:
        # TTS first if new text needs to be transcribed
        asyncio.create_task\
            (_callback(partial(dummy_tts_transcribe, [stmgr.text]), callback=tts_transcribe_cb, stmgr=stmgr))
    elif stmgr.text == stmgr.last_transcribed_text:
        start_sound_gen()

        pass
    stmgr.app.root.ids['record'].disabled = False


    logger.debug(f"Infer Pipeline {stmgr.state}")

async def tts_transcribe_cb(*args, stmgr=None):
    res = args[0]
    print("tts_trasncribe_cb")
    # if res['res']:
    #     stmgr.sound_descriptor = res['res']
    #     stmgr.app.root.ids['lab'].text = str(stmgr.sound_descriptor)
    #     await start_sound_gen(stmgr)

async def start_sound_gen(stmgr):
    await asyncio.create_task(_callback(partial(dummy_sg_transcribe, [stmgr.sound_descriptor]), callback=sound_gen_cb, stmgr=stmgr))

async def sound_gen_cb(*args, stmgr):
    print(args)
