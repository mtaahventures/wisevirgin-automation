"""
Script Cleaner - Separates voiceover text from production notes
"""
import re

class ScriptCleaner:
    def clean_for_tts(self, script):
        """Remove all production notes, visual cues, and formatting for clean TTS"""

        # Remove section headers with ** or * markers
        script = re.sub(r'\*\*\[.*?\]\*\*', '', script)
        script = re.sub(r'\*\[.*?\]\*', '', script)
        script = re.sub(r'\[.*?\]', '', script)

        # Remove italic stage directions
        script = re.sub(r'\*[A-Z][^*]*?\.\*', '', script)
        script = re.sub(r'\*Cut to.*?\*', '', script, flags=re.IGNORECASE)
        script = re.sub(r'\*Fade.*?\*', '', script, flags=re.IGNORECASE)
        script = re.sub(r'\*End of.*?\*', '', script, flags=re.IGNORECASE)

        # Remove horizontal rules
        script = re.sub(r'---+', '', script)
        script = re.sub(r'===+', '', script)

        # Remove bold formatting but keep text
        script = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)

        # Clean up quote markers around prompts
        script = re.sub(r"\*['\u2018\u2019](.+?)['\u2018\u2019]\*", r'\1', script, flags=re.DOTALL)

        # Remove standalone asterisks
        script = re.sub(r'^\*\s*$', '', script, flags=re.MULTILINE)
        script = re.sub(r'^\*\s+', '', script, flags=re.MULTILINE)
        script = re.sub(r'\s+\*$', '', script, flags=re.MULTILINE)

        # Remove markdown headers
        script = re.sub(r'^#+\s+', '', script, flags=re.MULTILINE)

        # Remove "End of script" references
        script = re.sub(r'End of [Ss]cript\.?', '', script)

        # Clean up multiple newlines
        script = re.sub(r'\n{3,}', '\n\n', script)
        script = re.sub(r'\n\s*\n\s*\n', '\n\n', script)

        # Final cleanup
        script = script.strip()

        return script

    def extract_production_notes(self, script):
        """Extract visual cues separately"""
        production_notes = []
        visual_cues = re.findall(r'\[VISUAL CUE:(.*?)\]', script, flags=re.IGNORECASE)

        for i, cue in enumerate(visual_cues):
            production_notes.append({
                'index': i,
                'type': 'visual_cue',
                'content': cue.strip()
            })

        return production_notes
