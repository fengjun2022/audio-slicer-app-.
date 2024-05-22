from flask import Flask, request, jsonify, send_file
import os
import zipfile
from slicer2 import slice_audio

app = Flask(__name__)

@app.route('/slice_audio', methods=['POST'])
def slice_audio_endpoint():
    # 检查请求中是否包含音频文件，如果没有，则返回错误信息
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    # 从请求中获取音频文件
    audio_file = request.files['audio']
    # 获取输出目录，如果没有提供，则默认为 None
    output_dir = request.form.get('out', None)
    # 获取降噪阈值，没有则默认为 -40 dB
    db_thresh = float(request.form.get('db_thresh', -40))
    # 获取最小切片长度，没有则默认为 5000 毫秒
    min_length = int(request.form.get('min_length', 5000))
    # 获取切片间最小间隔，没有则默认为 300 毫秒
    min_interval = int(request.form.get('min_interval', 300))
    # 获取跳跃大小，没有则默认为 10 毫秒
    hop_size = int(request.form.get('hop_size', 10))
    # 获取保留的最大静音长度，没有则默认为 500 毫秒
    max_sil_kept = int(request.form.get('max_sil_kept', 500))

    # 为音频文件设置临时存储路径
    audio_path = os.path.join('/tmp', audio_file.filename)
    # 保存音频文件到临时路径
    audio_file.save(audio_path)

    # 如果未指定输出目录，则使用默认的临时目录
    if output_dir is None:
        output_dir = os.path.join('/tmp', 'sliced_audio')

    # 使用 slice_audio 函数切割音频，并返回切割后的音频文件路径列表
    chunk_paths = slice_audio(audio_path, output_dir, db_thresh, min_length, min_interval, hop_size, max_sil_kept)

    # 创建压缩文件，用于存放所有切割后的音频文件
    zip_path = os.path.join(output_dir, 'sliced_audio.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for chunk_path in chunk_paths:
            # 将切割后的音频文件添加到压缩包中
            zipf.write(chunk_path, os.path.basename(chunk_path))

    # 将压缩文件作为附件返回给客户端
    return send_file(zip_path, as_attachment=True)

# 启动 Flask 应用
if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True)
