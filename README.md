# unit_ut61eplus
Access digtal multimeter UNI-T UT61E+ from Python via CP2110 based USB connection

It should work also for other models: 

* UT60BT
* UT61B+
* UT61D+
* UT161B
* UT161D
* UT161E

but for this the unit conversion has to be adjusted (see `from_vendor/*.json`)

## Status
> Working


## Example output (see `readDMM.py`)
```
mode=DCV
range=1
display=8.595
overload=False
decimal=8.595
unit=V
max=False
min=False
hold=False
rel=False
auto=True
battery=False
hvwarning=False
dc=True
peak_max=False
peak_min=False
```
