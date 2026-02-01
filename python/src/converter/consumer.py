import pika, sys, os, time
from pymongo import MongoClient
from gridfs import GridFS
from convert import to_mp3

def main():
    client = MongoClient(os.environ.get("MONGO_URI"))
    db_videos = client.videos
    db_mp3s = client.mp3s
    #GridFS for videos
    fs_videos = GridFS(db_videos)
    #GridFS for mp3s
    fs_mp3s = GridFS(db_mp3s)
    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    
    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            print(f"Failed to process message: {err}")
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag) 

    channel.basic_consume(queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback)
    print("Waiting For Messages, To Exit Press CTRL + C")
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)