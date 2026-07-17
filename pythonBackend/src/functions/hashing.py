import hashlib

FAN_VALUE = 5
MIN_TIME_DELTA = 0
MAX_TIME_DELTA = 200

def generate_hashes(peaks, fan_value=FAN_VALUE):
    hashes = []
    for i in range(len(peaks)):
        anchor_time, anchor_freq = peaks[i]
        for j in range(1, fan_value + 1):
            if (i + j) < len(peaks):
                target_time, target_freq = peaks[i + j]
                time_delta = target_time - anchor_time
                if MIN_TIME_DELTA <= time_delta <= MAX_TIME_DELTA:
                    hash_input = f"{anchor_freq}|{target_freq}|{time_delta}"
                    h = hashlib.sha1(hash_input.encode()).hexdigest()[0:20]
                    hashes.append((h, int(anchor_time)))
    return hashes