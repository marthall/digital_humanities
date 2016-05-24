from bottle import route, run, template, static_file, redirect, request
import itertools


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


try:
	import ujson as json
except ImportError:
	import json

#LOADING MODULE FROM UPPER DIR - hackish..
import sys, os,csv
old_dir = os.path.abspath(os.curdir)
os.chdir('..')
sys.path.append(os.path.abspath(os.curdir))
from generate_word_buckets import give_results
os.chdir(old_dir)

#OK, HACK END



@route('/')
def index():
    redirect("/static/index.html")

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')

@route('/api', method='POST')
def process():
	text = request.forms.get('input') 
	results = give_results(text, 1800, 2000)
	dummy = ["matching: |X ∩ Y|", "dice: 2|X ∩ Y|/(|X| + |Y|)", "jaccard: |X ∩ Y|/|X ∪ Y|", "overlap: |X ∩ Y|/min(|X|,|Y|)", "cosine: |X ∩ Y|/sqrt(|X|*|Y|)"]
	return dict(data=[{
		"x": list(map(lambda x : x[0], results)),
		"y": list(map(lambda x : x[1][y_idx], results)),
		"name": dummy[y_idx]
	} for y_idx in range(5)])

@route('/about_dataset')
def about_dataset():
    redirect("/static/about_dataset.html")

@route('/api/about_dataset')
def about_dataset():

	with open("result", 'r') as infile:
		data = [line.split() for line in infile]
		d = dict()
		for k, g in itertools.groupby(data, lambda x: x[1][:4]):
			d[int(k)] = sum(map(lambda x: int(x[0]), g))

	x = []
	y = []
	with cd("../buckets/JDG"):
		for year in range(1800,2000):
			if not os.path.isfile("%d_stemmed.json" % year):
				continue
			with open("%d_stemmed.json" % year, 'r') as infile:
				obj = json.load(infile)
				if d[year]:
					x.append(year)
					y.append(float(obj["number_of_broken_words"])/d[year])
	return dict(data=[{
		"x": x,
		"y": y,
	}])


@route('/api/about_spellcheck')
def about_spellcheck():

	data = []
	for fname in ["JDG", "GDL"]:
		with open(fname + ".csv", 'r') as infile:
			reader = list(csv.reader(infile,  delimiter='\t'))
			dates = list(map(lambda x : x[0], reader))
			unique_before = list(map(lambda x : float(x[1]), reader))
			unique_after = list(map(lambda x : float(x[2]), reader))
			gain = list(map(lambda x : float(float(x[1])-float(x[2]))/float(x[1])*100.0, reader))
			good = list(map(lambda x : float(x[3]), reader))
			fixed = list(map(lambda x : float(x[4]), reader))
			dummy = {
				'unique_after': unique_after,
				'unique_before': unique_before,
				'gain': gain,
				'good': good,
				'fixed': fixed
			}
			for k,v in dummy.items():
				data.append({
					'name': fname + k,
					'y': v,
					'x': dates
					})
		
	
	return dict(data=data)


run(host='localhost', port=8080, reloader=True)