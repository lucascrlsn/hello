
# https://medium.com/saarthi-ai/who-spoke-when-build-your-own-speaker-diarization-module-from-scratch-e7d725ee279
from resemblyzer import preprocess_wav, VoiceEncoder
from pathlib import Path

# D Vector Clusteroring
from spectralcluster import SpectralClusterer

# give the file path to your audio file
audio_file_path = '****************************************'
wav_fpath = Path(audio_file_path)

wav = preprocess_wav(wav_fpath)

encoder = VoiceEncoder("cpu")
_, cont_embeds, wav_splits = encoder.embed_utterance(wav, return_partials=True, rate=16)

print(cont_embeds.shape)

####################################################################################################
# D vector clustering


clusterer = SpectralClusterer(
    min_clusters=2,
    max_clusters=100,
    p_percentile=0.90,
    gaussian_blur_sigma=1)

labels = clusterer.predict(cont_embeds)

####################################################################################################
# Create Continuous Segments


def create_labelling(labels, wav_splits):
    from resemblyzer import sampling_rate
    times = [((s.start + s.stop) / 2) / sampling_rate for s in wav_splits]
    labelling = []
    start_time = 0

    for i, time in enumerate(times):
        if i > 0 and labels[i] != labels[i - 1]:
            temp = [str(labels[i - 1]), start_time, time]
            labelling.append(tuple(temp))
            start_time = time
        if i == len(times) - 1:
            temp = [str(labels[i]), start_time, time]
            labelling.append(tuple(temp))

    return labelling


labelling = create_labelling(labels, wav_splits)

create_labelling()