import os
import subprocess
import re

import acoustid
import chromaprint


SPAN = 10
AUDIO_EXTENSION = '.aac'
SIMILARITY_THRESHOLD = 0.9


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

    with open(input_file, 'r') as reader:
        FNULL = open(os.devnull, 'w')
        for _cnt, url in enumerate(reader):
            url = url.strip()
            matched = re.match(
                r'^http://ark.tubi.video/(.+)/.+.mp4$', url, re.M | re.I)
            if matched:
                audio_file_name = matched.group(1) + AUDIO_EXTENSION
                audio_path = os.path.join(folder_name, audio_file_name)
                if not os.path.exists(audio_path):
                    # extract audio with first 10 seconds
                    command = f"ffmpeg -t 15 -i {url} -vn {audio_path}"
                    subprocess.call(command, stderr=FNULL, shell=True)


def check_audio_similarity(audio1, audio2):
    fp1, _duration1 = calc_fingerprint(audio1)
    fp2, _duration2 = calc_fingerprint(audio2)
    return correlation(fp1, fp2)


def correlation(fp1, fp2):
    """
    check similarity of 2 audio files
    """
    covariances = []
    for offset in range(-SPAN, SPAN):
        length = min(len(fp1), len(fp2)) - abs(offset)
        if offset > 0:
            fp1 = fp1[offset:(offset + length)]
            fp2 = fp2[offset:(offset + length)]
        else:
            fp1 = fp1[:length]
            fp2 = fp2[:length]

        covariance = 0
        for i in range(length):
            covariance += 32 - bin(fp1[i] ^ fp2[i]).count('1')
        covariance = covariance / float(length)
        covariances.append(covariance / 32)
    return max(covariances)


def is_group_similar(filename):
    """
    check all audios similarity under one folder
    """
    folder = get_name_without_extension(filename)

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

    print(similarities)
    similar = all(x >= SIMILARITY_THRESHOLD for x in similarities)
    return (len(similarities), similar)


def calc_fingerprint(audiofile):
    duration, fp_encoded = acoustid.fingerprint_file(audiofile)
    fingerprint, _version = chromaprint.decode_fingerprint(fp_encoded)
    return (fingerprint, duration)


if __name__ == '__main__':
    files = ["videos_group1.txt", "videos_group2.txt", "mix.txt"]
    for filename in files:
        extract_audios(filename)
        count, similar = is_group_similar(filename)
        print(f"{filename} count={count} similar={similar}")
