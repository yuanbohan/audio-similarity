import os
import subprocess
import re

import numpy
import acoustid
import chromaprint


AUDIO_EXTENSION = '.aac'
SPAN = 10
STEP = 1


def get_name_without_extension(filename):
    return os.path.splitext(filename)[0]


def extract_audios(input_file):
    """
    input_file: a file contains a list of videos, one video each line
    output_folder: where to store the audio files
    """
    file_name = os.path.basename(input_file)
    folder_name = get_name_without_extension(file_name)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # TODO:
    # index to display progress
    # check if audio file already exist
    with open(input_file, 'r') as reader:
        FNULL = open(os.devnull, 'w')
        for url in reader:
            url = url.strip()
            matched = re.match(
                r'^http://ark.tubi.video/(.+)/.+.mp4$', url, re.M | re.I)
            if matched:
                audio_file_name = matched.group(1) + AUDIO_EXTENSION
                audio_path = os.path.join(folder_name, audio_file_name)

                # extract audio with first 10 seconds
                command = f"ffmpeg -t 10 -i {url} -vn {audio_path}"
                print(command)
                subprocess.call(command, stderr=FNULL, shell=True)


def check_audio_similarity(audio1, audio2):
    """
    select max correlation with offset between [-span, span]
    """
    fp1, _duration1 = calc_fingerprint(audio1)
    fp2, _duration2 = calc_fingerprint(audio2)
    correlations = []
    for offset in numpy.arange(-SPAN, SPAN + 1, STEP):
        correlations.append(cross_correlation(fp1, fp2, offset))
    return max(correlations)


def cross_correlation(fp1, fp2, offset):
    """
    check similarity of 2 audio files
    """
    if offset > 0:
        fp1 = fp1[offset:]
        fp2 = fp2[:len(fp1)]
    elif offset < 0:
        offset = -offset
        fp2 = fp2[offset:]
        fp1 = fp1[:len(fp2)]

    size = len(fp1)
    covariance = 0
    for i in range(size):
        covariance += 32 - bin(fp1[i] ^ fp2[i]).count('1')
    covariance = covariance / float(size)
    return covariance/32


def is_group_similar(folder):
    """
    check all audios similarity under one folder
    """
    base = None

    similarities = []
    folder = os.path.expanduser(folder)
    for entry in os.scandir(folder):
        path = entry.path
        if not path.endswith(AUDIO_EXTENSION):
            continue

        if not base:
            base = path
            continue
        else:
            similarity = check_audio_similarity(base, path)
            similarities.append(similarity)

    return all(x >= 0.8 for x in similarities)


def calc_fingerprint(audiofile):
    duration, fp_encoded = acoustid.fingerprint_file(audiofile, maxlength=10)
    fingerprint, _version = chromaprint.decode_fingerprint(fp_encoded)
    return (fingerprint, duration)


if __name__ == '__main__':
    files = ["videos_group1.txt", "videos_group2.txt"]
    for filename in files:
        extract_audios(filename)
        folder = get_name_without_extension(filename)
        similar = is_group_similar(folder)
        print(f"{folder} similar={similar}")
