import asyncio

async def dummy_stt_startup():
    print("Starting up STT WS")
    await asyncio.sleep(1)
    return True

async def dummy_tts_startup():
    print("Starting up TTS WS")
    await asyncio.sleep(1)
    return True

async def dummy_sg_startup():
    print("Starting up SG WS")
    await asyncio.sleep(1)
    return True

async def dummy_stt_start(microphone_name):

    print("Starting to transcribe w/ ", microphone_name)
    await asyncio.sleep(1)
    return True

async def dummy_stt_stop():
    print("Stopping STT and extracting text")
    await asyncio.sleep(5)
    return {"res":"A warm guitar sound with lots of vibratto"}

async def dummy_tts_transcribe(text):
    print("Starting TTS Transcribe")
    await asyncio.sleep(2)
    outputs = {
        'velocity': 75,
        'pitch': 60,
        'source': 'acoustic',
        'qualities': ['bright', 'percussive'],
        'latent_sample': [0.] * 16
    }
    return {"res": outputs}

async def dummy_sg_generate(inputs):
    print("Starting sound generation")
    await asyncio.sleep(2)

    return [1, 2, 3, 4]