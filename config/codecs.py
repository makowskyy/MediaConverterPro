VIDEO_FORMATS = {
    'MKV': {
        'ffmpeg_name': 'matroska',
        'extension': 'mkv',
        'video': [
            ('H.264 (x264)',  'libx264'),
            ('H.265 (x265)',  'libx265'),
            ('AV1',           'libaom-av1'),
            ('VP9',           'libvpx-vp9'),
            ('MPEG-2',        'mpeg2video'),
            ('XviD',          'libxvid'),
            ('DivX',          'mpeg4'),
        ],
        'audio': [
            ('AAC',   'aac'),
            ('MP3',   'libmp3lame'),
            ('AC3',   'ac3'),
            ('DTS',   'dts'),
            ('FLAC',  'flac'),
            ('Opus',  'libopus'),
        ],
    },
    'MP4': {
        'ffmpeg_name': 'mp4',
        'extension': 'mp4',
        'video': [
            ('H.264 (x264)',  'libx264'),
            ('H.265 (x265)',  'libx265'),
            ('AV1',           'libaom-av1'),
        ],
        'audio': [
            ('AAC',  'aac'),
            ('MP3',  'libmp3lame'),
            ('AC3',  'ac3'),
        ],
    },
    'AVI': {
        'ffmpeg_name': 'avi',
        'extension': 'avi',
        'video': [
            ('H.264 (x264)',  'libx264'),
            ('MPEG-2',        'mpeg2video'),
            ('XviD',          'libxvid'),
            ('DivX',          'mpeg4'),
        ],
        'audio': [
            ('MP3',  'libmp3lame'),
            ('AC3',  'ac3'),
            ('PCM',  'pcm_s16le'),
        ],
    },
    'MOV': {
        'ffmpeg_name': 'mov',
        'extension': 'mov',
        'video': [
            ('H.264 (x264)',  'libx264'),
            ('H.265 (x265)',  'libx265'),
            ('ProRes',        'prores'),
        ],
        'audio': [
            ('AAC',  'aac'),
            ('AC3',  'ac3'),
            ('PCM',  'pcm_s16le'),
        ],
    },
    'WebM': {
        'ffmpeg_name': 'webm',
        'extension': 'webm',
        'video': [
            ('VP8',  'libvpx'),
            ('VP9',  'libvpx-vp9'),
            ('AV1',  'libaom-av1'),
        ],
        'audio': [
            ('Opus',    'libopus'),
            ('Vorbis',  'libvorbis'),
        ],
    },
    'FLV': {
        'ffmpeg_name': 'flv',
        'extension': 'flv',
        'video': [
            ('H.264 (x264)',  'libx264'),
        ],
        'audio': [
            ('AAC',  'aac'),
            ('MP3',  'libmp3lame'),
        ],
    },
    'TS': {
        'ffmpeg_name': 'mpegts',
        'extension': 'ts',
        'video': [
            ('H.264 (x264)',  'libx264'),
            ('H.265 (x265)',  'libx265'),
            ('MPEG-2',        'mpeg2video'),
        ],
        'audio': [
            ('AAC',  'aac'),
            ('AC3',  'ac3'),
            ('MP3',  'libmp3lame'),
        ],
    },
}

AUDIO_FORMATS = {
    'MP3':  {'ffmpeg_name': 'mp3',  'codec': 'libmp3lame', 'extension': 'mp3'},
    'AAC':  {'ffmpeg_name': 'adts', 'codec': 'aac',        'extension': 'aac'},
    'FLAC': {'ffmpeg_name': 'flac', 'codec': 'flac',       'extension': 'flac'},
    'OGG':  {'ffmpeg_name': 'ogg',  'codec': 'libvorbis',  'extension': 'ogg'},
    'WAV':  {'ffmpeg_name': 'wav',  'codec': 'pcm_s16le',  'extension': 'wav'},
    'M4A':  {'ffmpeg_name': 'ipod', 'codec': 'aac',        'extension': 'm4a'},
    'OPUS': {'ffmpeg_name': 'ogg',  'codec': 'libopus',    'extension': 'opus'},
    'WMA':  {'ffmpeg_name': 'asf',  'codec': 'wmav2',      'extension': 'wma'},
}

SAMPLE_RATES = ['44100', '48000', '96000']
CHANNELS = {'Stereo': '2', 'Mono': '1', 'Surround 5.1': '6'}

PRESET_CODECS = {'libx264', 'libx265'}
