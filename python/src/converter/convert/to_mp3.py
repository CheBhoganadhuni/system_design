import pika, json, tempfile, os
from bson.objectid import ObjectId
from moviepy import VideoFileClip

def start(message, fs_videos, fs_mp3s, ch):
    try:
        message = json.loads(message)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return "Invalid JSON", 400
    
    # 1. Create a temp file for the video input
    tf = tempfile.NamedTemporaryFile(delete=False) # delete=False ensures moviepy can read it

    try:
        # Get video contents from GridFS
        out = fs_videos.get(ObjectId(message["video_fid"]))
        tf.write(out.read())
        tf.close() # Close so MoviePy can access the file path reliably

        # 2. Convert video to mp3
        # Using context manager 'with' ensures audio/video handles are closed automatically
        tf_path = os.path.join(tempfile.gettempdir(), f"{message['video_fid']}.mp3")
        
        with VideoFileClip(tf.name) as video:
            audio = video.audio
            # Use logger=None to keep console clean if desired
            audio.write_audiofile(tf_path, logger=None)
        
        # 3. Upload mp3 to GridFS
        with open(tf_path, "rb") as f:
            data = f.read()
            fid = fs_mp3s.put(data)
        
        # Clean up the mp3 temp file
        os.remove(tf_path)
        
        # 4. Update message with mp3 file ID
        message["mp3_fid"] = str(fid)

        # 5. Publish to downstream queue
        queue_name = os.environ.get("MP3_QUEUE")
        if not queue_name:
            raise Exception("MP3_QUEUE environment variable not set")

        ch.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            )
        )
        
        return None, None

    except Exception as e:
        print(f"Error during conversion: {e}")
        # Cleanup: If we uploaded to GridFS but failed to publish, delete the orphan file
        if 'fid' in locals():
            fs_mp3s.delete(fid)
        return str(e), 500
    
    finally:
        # Always remove the initial video temp file
        if os.path.exists(tf.name):
            os.remove(tf.name)