import requests
import json
import whisper
import srt
from datetime import timedelta

# Step 1: Diarization using PyAnnote API
def perform_diarization(audio_url):
    url = "https://api.pyannote.ai/v1/diarize"
    payload = {
        "url": audio_url,
        "webhook": "https://webhook.site/9f581bb2-c367-422b-8eb7-a4e6009e15d7",
        "confidence": False
    }
    headers = {
        "Authorization": "Bearer sk_4c3ccbe8a31f498dbd61d0772129ca73",
        "Content-Type": "application/json"
    }

    # Send request to PyAnnote API
    response = requests.post(url, json=payload, headers=headers)
    print("Diarization response:", response.text)

    # Save the diarization result to a JSON file
    diarization_result = response.json()
    with open("diarization.json", "w") as f:
        json.dump(diarization_result, f, indent=4)

    return diarization_result
    
# Step 2: Transcribe the audio using Whisper
def transcribe_audio(audio_file):
    # Load Whisper model
    model_size = "medium"  # You can change this to "small", "large", etc.
    model = whisper.load_model(model_size)

    # Transcribe the audio
    result = model.transcribe(audio_file, language="bn")  # 'bn' for Bengali
    return result

# Step 3: Generate SRT file from transcription
def generate_srt(result, output_file):
    subtitles = []
    for i, segment in enumerate(result["segments"]):
        start = timedelta(seconds=segment["start"])
        end = timedelta(seconds=segment["end"])
        text = segment["text"]
        subtitles.append(srt.Subtitle(index=i + 1, start=start, end=end, content=text))

    # Save as SRT file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))

    print(f"SRT file saved: {output_file}")

# Step 4: Align diarization with transcription and generate speaker-labeled SRT
def align_and_generate_speaker_srt(diarization_data, result, output_file):
    # Extract diarization segments
    diarization_segments = diarization_data["output"]["diarization"]

    # Extract Whisper segments
    whisper_segments = result["segments"]

    # Align diarization with Whisper transcription
    aligned_segments = []
    for segment in whisper_segments:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]

        # Find the corresponding diarization segment
        for diarization_segment in diarization_segments:
            if diarization_segment["start"] <= start and diarization_segment["end"] >= end:
                speaker = diarization_segment["speaker"]
                aligned_segments.append({
                    "speaker": speaker,
                    "start": start,
                    "end": end,
                    "text": text
                })
                break

    # Generate SRT with speaker labels
    with open(output_file, "w", encoding="utf-8") as f:
        for i, segment in enumerate(aligned_segments, start=1):
            start_time = srt.timedelta_to_srt_timestamp(timedelta(seconds=segment["start"]))
            end_time = srt.timedelta_to_srt_timestamp(timedelta(seconds=segment["end"]))
            speaker = segment["speaker"]
            text = segment["text"]
            f.write(f"{i}\n{start_time} --> {end_time}\n{speaker}: {text}\n\n")

    print(f"Speaker-labeled SRT file saved: {output_file}")

# Main function
def main():
    # Replace with your audio file path or URL
    audio_file = "clean_audio_file_MOTU_PATLU_EP_458B_HD_93475_HINDI_PREMIX.wav"  # Local file path
    audio_url = "https://oh-rianprod-s3.s3.us-east-2.amazonaws.com/249530116730/943d00c8/clean_audio_file_MOTU_PATLU_EP_456B_HD_89365_HINDI_PREMIX.wav?X-Amz-Expires=18000&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5XJBBBXGD3W5XYNV%2F20250311%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250311T113315Z&X-Amz-SignedHeaders=host&X-Amz-Signature=b8783cd6bc2897ce6a6d3d898f43273393ca86f551974d35be28ebb1fe95b9c6"
    # Step 1: Perform diarization
    diarization_data = perform_diarization(audio_url)

    # Step 2: Transcribe the audio
    result = transcribe_audio(audio_file)

    # Step 3: Generate basic SRT file
    srt_file = audio_file.rsplit(".", 1)[0] + ".srt"
    generate_srt(result, srt_file)

    # Step 4: Align diarization with transcription and generate speaker-labeled SRT
    speaker_srt_file = audio_file.rsplit(".", 1)[0] + "_speaker.srt"
    align_and_generate_speaker_srt(diarization_data, result, speaker_srt_file)

if __name__ == "__main__":
    main()


