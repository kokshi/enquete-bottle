# enquete-bottle

```shell
$ cd enquete-bottle
$ docker build -t enquete-bottle .
$ docker run -d --rm --name enquete-bottle-app -p 8080:8080 -v $PWD/database:/usr/src/app/database/ enquete-bottle
```