#%%
from glob import glob
import json
import os
import shutil
# %%
files = glob("/home/sheldon/images/gundam/*")
# %%
file = files[0]
# %%
with open('/home/sheldon/images/gundam/tags.json') as f:
    data = json.load(f)
# %%
data_t = {}
for item in data:
    filename = item['filename']
    value = {x: y for x, y in data[0].items() if x != 'filename'}
    data_t[filename] = value
# %%

with open('/home/sheldon/images/gundam/tags_new.json', 'w') as f:
    json.dump(data_t, f, indent=4)
# %%
hf_data = []
for item in data:
    filename = os.path.basename(item['filename'])
    text = ','.join(item['tag'])
    if 'gundam' not in text.lower():
        print(text.lower())
        try:
            shutil.move(f"/home/sheldon/images/gundam/{filename}", f"/home/sheldon/images/bak/{filename}")
        except:
            pass
    hf_data.append({'file_name': filename, 'text': text})
# %%
for item in data:
    if '350' in item['filename']:
        print(','.join(item['tag']).lower())
# %%
