import asyncio
import common.log as log

logger = log.setup_logger()

async def dummy_stt_startup():
    logger.debug("Starting up STT WS")
    await asyncio.sleep(1)
    return {"resp":"True"}

async def dummy_tts_startup():
    logger.debug("Starting up TTS WS")
    await asyncio.sleep(1)
    return {"resp":"True"}

async def dummy_sg_startup():
    logger.debug("Starting up SG WS")
    await asyncio.sleep(1)
    return {"resp":"True"}

async def dummy_stt_start(microphone_name):

    logger.debug(f"Starting to transcribe w/ {microphone_name}")
    await asyncio.sleep(1)
    return {"resp":"True"}

async def dummy_stt_stop():
    from random import randrange

    texts = ["A warm guitar sound with lots of vibratto",
             "long decay guitar sound... that's also bright",
             "weird guitar sound with a twang at the end",
             "something else too"]

    logger.debug("Stopping STT and extracting text")
    await asyncio.sleep(5)
    return {"resp": texts[randrange(3)]}

async def dummy_tts_transcribe(text):
    logger.debug("Starting TTS Transcribe")
    await asyncio.sleep(2)
    outputs = {
        'velocity': 75,
        'pitch': 60,
        'source': 'acoustic',
        'qualities': ['bright', 'percussive'],
        'latent_sample': [0.] * 16
    }
    return {"resp": outputs}

async def dummy_sg_generate(inputs):
    logger.debug("Starting sound generation")
    await asyncio.sleep(2)

    return {"resp":[1, 2, 3, 4]}

async def dummy_preprocessing():

    logger.debug("Doing some preprocessing")
    await asyncio.sleep(5)

    return {"resp":"True"}