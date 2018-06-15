# 2018 NLP project

## Project Data

[google-drive link](https://drive.google.com/drive/u/2/folders/18pnif3i3Rw4yPXInUloBQ65l6AsUgKm2)

0. google-drive -> 2018NLP_project
1. EVP/data/ -> crawler/EVP/data/
2. WEB/geniatagger-3.0.2/ -> WEB/WEB/utils/geniatagger-3.0.2/
3. WEB/img -> WEB/WEB/static/img/
4. WEB/data -> WEB/WEB/utils/data/
5. egp.txt -> WEB/WEB/utils/egp.txt

## How to start the server

```
python3 WEB.py # now port is 5487
```

### Access to server

http://nlp-ultron.cs.nthu.edu.tw:5487

### Tips

- Run the server even close ssh

   ```bash
   nohup python3 WEB.py > nohup.log &
   ```
-  Find our server process_id and running on which port

   ```bash
   netstat -ntpl
   ```
- Show all  jobs and process_id

   ```bash
   jobs -l 
   htop
   ```
- Kill process

   ```bash
   kill <process_id> # process_id can be found by Tips 2
   ```

### About Anaconda

```bash
conda create -n my_root anaconda # create a new Python environment
source activate my_root # change to our environment
conda install <package name> # install new package
conda list # show packages installed
```



