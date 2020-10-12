from flask import Flask, request

app = Flask(__name__)

books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


@app.route('/edf/fft-with-ica', methods=['GET'])
def fft_with_ica():
    file_location = request.args.get('file')
    if file_location:
        return file_location
    else:
        return "No file location"


@app.route('/edf/fft-no-ica', methods=['GET'])
def fft_no_ica():
    return "FFT with no ICA"


@app.route('/edf/ica-no-fft', methods=['GET'])
def ica_no_fft():
    return "ICA no FFT"


if __name__ == '__main__':
    app.run()
