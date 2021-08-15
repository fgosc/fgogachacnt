PythonVersion="3.9.6"
PythonPth="python39._pth"

curl https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip -O python-$PythonVersion-embed-amd64.zip
curl https://bootstrap.pypa.io/get-pip.py -O get-pip.py

unzip python-$PythonVersion-embed-amd64.zip python
rm "./python/$PythonPth"

./python/python ./get-pip.py

./python/Scripts/pip install -r ../requirements.txt
./python/Scripts/pip install PySimpleGUIWx

rm python-$PythonVersion-embed-amd64.zip
rm get-pip.py

cd ..
./gui/python/python makecard.py
./gui/python/python makerarity.py
