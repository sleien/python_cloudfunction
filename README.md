# Python Clooudfunction

This is a small webserver hosting serverless python functions. It's build for different github repos to deploy functions directly to it.
  
All functions are hosted at /function_name.  

## Install
```
pip install -r requiremets.txt
```

## Configure new functions  
1. Create config file in the configs folder (one is enough per source repository)
    ```
    - file: "test.py"
      endpoint: "test"
      methods: '["GET"]'
    - file: "helloworld.py"
      cron: "* * * * *"
    ```
    Use endpoint and methods for the function to be callable or cron for it to run on a timer. It is possible to use both.
1. Create a python file with a main() function and return str int (html code)
    ```
    def main():
        return {"message": "test function"}, 200
    ```

## Access functions
Simple open `/[endpoint]` with the in the config files configured endpoints.