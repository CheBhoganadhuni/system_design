import pika, json, tempfile, os
from bson.objectid import ObjectId
from moviepy import VideoFileClip

def start(message, fs_videos, fs_mp3s, ch):
    message = json.loads(message)
    
    # empty temp file
    tf = tempfile.NamedTemporaryFile()

    # video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))
    # add video contents to temp file
    tf.write(out.read())
    tf.seek(0)

    # convert video to mp3
    audio = VideoFileClip(tf.name).audio
    tf.close()
    
    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)
    
    # upload mp3 to gridfs - mongodb
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    # remove temp file
    os.remove(tf_path)
    
    # update message with mp3 fid
    message["mp3_fid"] = str(fid)

    try:
        # publish message to rabbitmq
        ch.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            )
        )
    except Exception as e:
        fs_mp3s.delete(fid)
        return str(e), 500
    
    return None, None
    
    