# audio similarity

check similarity by acoustic fingerprint

## prerequisites

- ffmpeg
- chromaprint
- pipenv

## setup

- `pipenv install`
- `pipenv shell`
- `python app.py`

## steps

- extract all videos to aac audio files with first 10 seconds
- extract acoustic fingerprint
- check if audios in each group are similar

## resources

- https://willdrevo.com/fingerprinting-and-audio-recognition-with-python/
- https://en.wikipedia.org/wiki/Acoustic_fingerprint
- https://docs.acrcloud.com/docs/acrcloud/introduction/audio-fingerprinting/
- https://oxygene.sk/2011/01/how-does-chromaprint-work/
- https://github.com/worldveil/dejavu
- https://medium.com/intrasonics/a-fingerprint-for-audio-3b337551a671
- https://yohanes.gultom.me/2018/03/24/simple-music-fingerprinting-using-chromaprint-in-python/
- https://acoustid.org/
- https://github.com/worldveil/dejavu
