from flask import Flask
from flask import request
from flask import Response
from flask import stream_with_context

from lab.wandlab.streamer import Streamer

app = Flask(__name__)
streamer = Streamer()

@app.route('/stream')
def stream():
    """
    스트리밍 엔드포인트로, 비디오 스트림을 제공합니다.
    """
    src = request.args.get('src', default=0, type=int)
    
    try:
        return Response(
            stream_with_context(stream_gen(src)),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
        
    except Exception as e:
        print('[wandlab] ', 'stream error : ', str(e))

def stream_gen(src):
    """
    비디오 스트리밍을 생성하는 제너레이터 함수입니다.
    """
    try:
        streamer.run(src)
        
        while True:
            frame = streamer.bytescode()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    except GeneratorExit:
        print('[wandlab]', 'disconnected stream')