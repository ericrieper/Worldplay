from app import app

app.debug = True

## RUN APP ##
if __name__ == '__main__':
    app.run(host='0.0.0.0')