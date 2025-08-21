from flask import *
from predict_user import func1
app=Flask(__name__)
app.secret_key="somekey"
@app.route('/')#,methods=['GET','POST'])
def base():
    #if request.method=='GET':
    return render_template('index.html')
    '''l.append([day['date'],outputs['recommended_generation_mw'],outputs['fuel_used_recommended'],\
                outputs['fuel_saved'],outputs['cost_saved'],outputs['co2_saved_tonnes'],\
                    outputs['recommended_efficiency']])'''

@app.route('/performance')
def performance():
    fuel=request.args['fuel']
    runtime=int(request.args['runtime'])
    cap=int(request.args['cap'])
    cur=int(request.args['cur'])
    inputs={
    "fuel_type": fuel,
    "max_capacity_mw": cap,
    "run_hours": runtime,
    "fuel_used_current": cur
    }
    #outputs=func1(inputs)
    session["result"]=func1(inputs)
    print(session["result"])
    outputs=session['result'][0]
    return render_template('performance.html',fuel=outputs[2],gen=outputs[1],co2=outputs[5],fuelsaved=outputs[3],\
                           costsaved=outputs[4])

@app.route('/analytics')
def analytics():
    outputs=session["result"]
    return render_template('analytics.html',l=outputs)

@app.route('/predictions')
def predictions():
    outputs=session["result"]
    return render_template('predictions.html',l=outputs)

app.run(host="0.0.0.0", port=5000,debug=True)