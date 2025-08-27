# Assembly AI

import json 

with open('src/demo_files/assembly_transcript_pt.json', 'r') as f:
    my_file = json.load(f)

def audio_diariazation_demo(audio_file): # should calls api with audio_file (any type)
    return my_file