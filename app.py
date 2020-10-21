from flask import Flask, request, jsonify

from cbPython import EEGAnalysis

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
    # file_location = request.args.get('file')
    # if file_location:
    #     return jsonify(file_location)
    # else:
    #     return jsonify("File not specified")
    a = EEGAnalysis.random(num_frames=100, sr=200, win_size=400)  # get a fake analysis
    print(a.electrodes)  # print out a dictionary of electrodes
    e = a.electrodes['Fp1']  # look at electrode FpZ
    e.graphic_frames  # print out a dictionary of all the graphic objects, one per frame of analysis
    f = e.graphic_frames[0]  # get the first frame
    # get a string that is JSON formatted with an indent of 2 spaces for the data in this frame
    return f.to_JSON(4)


@app.route('/edf/fft-no-ica', methods=['GET'])
def fft_no_ica():
    return "FFT with no ICA"


@app.route('/edf/ica-no-fft', methods=['GET'])
def ica_no_fft():
    return "ICA no FFT"


if __name__ == '__main__':
    app.run()
