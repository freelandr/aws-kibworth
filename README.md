# Serverless functions and API for Kibworth Ancestry project

## Usage

### Deployment

```
$ serverless deploy
```


### Invocation

```bash
export PASSWD=[insert password here]
export ENDPOINT=[insert endpoint here]
curl -i -H 'Content-Type: application/json' -X POST -d '{"password": "$PASSWD"}' https://$ENDPOINT/stop_rds
curl -i -H 'Content-Type: application/json' -X POST -d '{"password": "$PASSWD"}' https:/$ENDPOINT/restore_rds
```
