from flask import Flask, request, jsonify
from open_bijoy import unicode_to_bijoy, bijoy_to_unicode

app = Flask(__name__)

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get('text', '')
    mode = data.get('mode', 'uni2bijoy')

    if not text:
        return jsonify({'result': ''})

    try:
        if mode == 'uni2bijoy':
            result = unicode_to_bijoy(text)
        elif mode == 'bijoy2uni':
            result = bijoy_to_unicode(text)
        else:
            return jsonify({'error': 'Invalid conversion mode'}), 400

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
