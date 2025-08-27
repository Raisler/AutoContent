import json
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional

class TranscriptMatcher:
    def __init__(self, viral_segments_json: Dict, audio_transcript_json: Dict):
        self.viral_segments = viral_segments_json
        self.audio_transcript = audio_transcript_json
        
    def clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def find_best_match_in_utterance(self, viral_transcript: str, utterance_text: str) -> float:
        return SequenceMatcher(None, self.clean_text(viral_transcript), self.clean_text(utterance_text)).ratio()
    
    def find_partial_match_in_utterance(self, viral_transcript: str, utterance_text: str) -> float:
        clean_viral = self.clean_text(viral_transcript)
        clean_utterance = self.clean_text(utterance_text)
        
        if clean_viral in clean_utterance:
            return 1.0
        
        viral_words = clean_viral.split()
        utterance_words = clean_utterance.split()
        if not viral_words:
            return 0.0
        matches = sum(1 for word in viral_words if word in utterance_words)
        return matches / len(viral_words)
    
    def find_timestamp_for_segment(self, viral_segment: Dict, similarity_threshold: float = 0.6) -> Optional[Dict]:
        viral_transcript = viral_segment.get('transcript', '')
        if not viral_transcript:
            return None
        
        best_match = None
        best_score = 0.0
        
        for utterance in self.audio_transcript.get('utterances', []):
            partial_score = self.find_partial_match_in_utterance(viral_transcript, utterance.get('text', ''))
            similarity_score = self.find_best_match_in_utterance(viral_transcript, utterance.get('text', ''))
            score = max(partial_score, similarity_score)
            
            if score > best_score and score >= similarity_threshold:
                best_score = score
                best_match = {
                    'start_seconds': utterance.get('start', 0) // 1000,
                    'end_seconds': utterance.get('end', 0) // 1000
                }
        
        return best_match
    
    def match_all_segments(self, similarity_threshold: float = 0.6) -> List[Dict]:
        results = []
        
        for i, segment in enumerate(self.viral_segments.get('viral_segments', []), start=1):
            timestamp_match = self.find_timestamp_for_segment(segment, similarity_threshold)
            if timestamp_match:
                results.append({
                    "segment": i,
                    "start_time": timestamp_match['start_seconds'],
                    "end_time": timestamp_match['end_seconds']
                })
        
        return results


def load_and_match_from_files(viral_segments_file: str, audio_transcript_file: str, similarity_threshold: float = 0.6):
    with open(viral_segments_file, 'r', encoding='utf-8') as f:
        viral_segments = json.load(f)
    with open(audio_transcript_file, 'r', encoding='utf-8') as f:
        audio_transcript = json.load(f)
    
    matcher = TranscriptMatcher(viral_segments, audio_transcript)
    return matcher.match_all_segments(similarity_threshold)


"""if __name__ == "__main__":
    output = load_and_match_from_files(
        'src/demo_files/gemini_prompt_result_pt.json',
        'src/demo_files/assembly_transcript_pt.json',
        similarity_threshold=0.5
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
"""