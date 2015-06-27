from . import app

@app.route('/')
def meta_metrics():
  return ':)'
